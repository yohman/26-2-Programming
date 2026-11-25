"""Package a classroom quiz for a password-unlocked browser download.

Question text and the temporary passphrase live only under ignored admin/.course-private/week08/.
A checkout without that private source reuses the already encrypted package.
"""
from pathlib import Path
import base64, hashlib, json, secrets

ITERATIONS = 250_000
QUIZ_RELEASE = '2026-11-26T13:15:00+09:00'

def decrypt(payload, passphrase):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    decode = base64.b64decode
    key = hashlib.pbkdf2_hmac('sha256', passphrase.encode(), decode(payload['salt']), payload['iterations'], 32)
    return AESGCM(key).decrypt(decode(payload['iv']), decode(payload['ciphertext']), None)

def package(plaintext, passphrase, existing=None):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
    if existing:
        try:
            if decrypt(existing, passphrase) == plaintext:
                return existing
        except (ValueError, KeyError, InvalidTag):
            pass
    salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
    key = hashlib.pbkdf2_hmac('sha256', passphrase.encode(), salt, ITERATIONS, 32)
    encode = lambda value: base64.b64encode(value).decode('ascii')
    return dict(version=1, algorithm='AES-GCM', kdf='PBKDF2', hash='SHA-256', iterations=ITERATIONS,
                salt=encode(salt), iv=encode(iv), ciphertext=encode(AESGCM(key).encrypt(iv, plaintext, None)),
                filename='week09_quiz.ipynb', mime='application/x-ipynb+json')

def build(root, course):
    private = root/'admin/.course-private/week08'
    target = root/'weeks/week-09/quiz-01.enc.json'
    source = private/'quiz-source.json'
    if source.exists():
        config = json.loads(source.read_text())
        cells = [course.mdcell('# Week 09 小テスト①（成績評価対象）\n\n氏名：\n\n2026年11月26日／個人・6問・30点満点（各5点）\n\n準備できたら、教員の合図から12分。終了の合図で提出します。\n\n- 最初の6分：自分で解く（この問題文とHintのみ）。\n- 次の6分：教科書・ノート・教材・通常のWeb検索を使ってよい。\n- 12分を通して、生成AI・他者との相談・他者の解答のコピーは不可。\n- 採点：各問、指定された処理3点＋指定どおりの出力2点。未完成でも途中のコードを残してください。\n- 問題1-5は指定された計算を順番にコードで行うこと。結果の数値だけを書いても処理の点はつきません。\n- 解けたセルを実行し、出力を保存。`week09_quiz_氏名.ipynb`としてUNIPAへ提出。未完成でも提出してください。\n- この小テストと関数チャレンジは別の提出です。')]
        for ident, text in config['questions']:
            cells += [course.mdcell('## 小テスト①問題'+ident+'（5点）\n\n'+text), course.codecell('')]
        cells += [course.mdcell('## メモ（任意）\n\n途中まで考えたことや、動かなかった箇所があれば短く記す。')]
        notebook = private/'quiz-01.ipynb'
        course.notebook(notebook, cells)
        existing = json.loads(target.read_text()) if target.exists() else None
        payload = package(notebook.read_bytes(), config['passphrase'], existing)
        course.write(target, json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    elif not target.exists():
        raise FileNotFoundError('The private quiz source or an encrypted package is required.')


def build_page(root, c, header, version):
    version += '-quiz-code'
    bi, p = c.bi, c.p
    head = c.page_head('Week 09 · 小テスト①','course-pages.css','course-page.js',version)
    head += f'<link rel="stylesheet" href="../week-08/bicycle-week.css"><script src="../../assets/site.js?v={version}" defer></script><script src="../week-08/quiz.js?v={version}" defer></script></head>'
    body = '<h1>'+bi('小テスト①','Quiz 01')+'</h1>'+p(
        '授業中に案内するパスワードを入力。Notebookをダウンロードして氏名を記入し、開始の合図を待ちます。',
        'Enter the password announced in class. Download the notebook, add your name, and wait for the start signal.')
    body += '<div class="quiz-entry" data-quiz-lock><form><label for="quiz-password">'+bi('パスワード','Password')+'</label><div><input id="quiz-password" type="password" autocomplete="off" autocapitalize="none" spellcheck="false" required><button type="submit">'+bi('開く','Open')+'</button></div></form><p role="status" data-quiz-status></p><section data-quiz-unlocked hidden><a class="quiz-download" data-quiz-download>'+bi('小テストNotebookをダウンロード','Download quiz notebook')+' ↓</a><details><summary>'+bi('問題をプレビュー','Preview the questions')+'</summary><div data-quiz-preview></div></details></section></div>'
    c.write(root/'weeks/week-09/quiz.html',head+f'<body class="course-challenge bicycle-week quiz-page" data-release="{QUIZ_RELEASE}">'+header+'<main id="course-page" hidden>'+body+'</main></body></html>')
