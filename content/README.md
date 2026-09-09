# Weekly course content

Each file in `content/weeks/` is the live, editable source for one teaching week. The site reads these Markdown files directly when it loads—there is no build step.

Edit the front matter for the week number, titles, phase, and publication controls. The agenda renders: `Lecture Flow`, `In-Class Notebook`, `In-Class Challenge`, `Take-Home Assignment`, `Aha!`, `Takeaway`, and `Resources`. The In-Class Notebook should state its Human Coding, AI Completion, and Agent-Based Coding stages. Keep the `EN:` and `JP:` lines for the bilingual layout.

```yaml
week: 1
publish_at: 2026-09-29T09:00:00+09:00
preview: true
```

`publish_at` uses Japan time. While `preview: true`, the full entry is visible regardless of date (the current setting for all weeks). When you are ready to follow the schedule, change that line to `preview: false`. Before its `publish_at` time, students see only the week title and a coming-soon notice. Add `?planning=1` to `agenda.html` to inspect all weeks yourself, even after turning previews off.

The three programming practices are intentional: early weeks require independent tracing and writing before AI use; the middle weeks use AI for bounded completion and review; later weeks use agents only from a written brief with acceptance checks. Every `Take-Home Assignment` must state what is due, how to submit, and what demonstrates individual understanding.

Resources use one line each:

```md
- [Lecture PDF](weeks/week-01/lecture.pdf) {lecture}
```

Valid resource types include `lecture`, `fundamentals`, `challenge`, `data`, `experiment`, and `support`.
