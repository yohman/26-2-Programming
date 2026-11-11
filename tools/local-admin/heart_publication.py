"""Durable local selection saves; coalesced Git publication runs separately."""
import json
import threading
import time
from pathlib import Path

class HeartPublisher:
    def __init__(self, save, publish, outbox, write, delay=0.7, retry=5):
        self.save_selection, self.publish_selection = save, publish
        self.outbox, self.write = Path(outbox), write
        self.delay, self.retry = delay, retry
        self.condition = threading.Condition()
        try: state = json.loads(self.outbox.read_text())
        except (OSError, ValueError): state = {}
        self.revision = state.get('revision', 0)
        self.published = state.get('published', 0)
        self.error, self.state = '', 'pending' if self.revision > self.published else 'idle'
        self.due, self.closed = time.monotonic() + delay, False
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _persist(self):
        self.write(self.outbox, {'revision': self.revision, 'published': self.published})

    def status(self):
        with self.condition:
            return dict(state=self.state, revision=self.revision, published=self.published, error=self.error)

    def save(self, request):
        with self.condition:
            result = self.save_selection(request)
            if result.pop('changed', True):
                self.revision += 1
                self.state, self.error = 'pending', ''
                self.due = time.monotonic() + self.delay
                self._persist(); self.condition.notify_all()
            return dict(result, sync=self.status())

    def _run(self):
        while True:
            with self.condition:
                while not self.closed and self.revision <= self.published:
                    self.condition.wait()
                if self.closed: return
                wait = self.due - time.monotonic()
                if wait > 0:
                    self.condition.wait(wait); continue
                target = self.revision
                self.state = 'publishing'
            try:
                self.publish_selection()
            except Exception:
                with self.condition:
                    self.state, self.error = 'error', 'Publication failed; selections are saved and will retry.'
                    self.due = time.monotonic() + self.retry
            else:
                with self.condition:
                    self.published = max(self.published, target)
                    self.state = 'pending' if self.revision > self.published else 'idle'
                    self.error = ''; self._persist(); self.condition.notify_all()

    def close(self):
        with self.condition:
            self.closed = True; self.condition.notify_all()
        self.thread.join(timeout=2)
