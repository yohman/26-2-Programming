"""Build the archived Week 9 quiz page; keep the original packaging helper.

Question text and the temporary passphrase live only under ignored admin/.course-private/week08/.
A checkout without that private source reuses the already encrypted package.
"""
from pathlib import Path
import base64, hashlib, json, secrets

ITERATIONS = 250_000
QUIZ_RELEASE = '2026-11-26T13:15:00+09:00'
ROUND_A = 'A: AIなし / Without AI'
ROUND_B = 'B: AIあり / AI-assisted'

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
        cells = [course.mdcell(
            '# Week 09 小テスト①（成績評価対象）\n\n氏名：\n\n'
            '2026年11月26日／個人・6問\n\n'
            '- **A：最初の6分（AIなし）**。問題文とヒントだけで解き、Aセルだけに書いて実行します。AI補完もオフにしてください。切り替えの合図で保存します。\n'
            '- **B：次の6分（AI利用OK）**。Aは編集・再実行せず、直したい問題や未回答の問題はBセルに解答を書いて実行します。変更しない問題はBを空欄のままにします。\n'
            '- どちらのラウンドも個人で取り組みます。相談や他の学生の解答のコピーは不可。\n'
            '- AIなし・AI利用可の得点はそれぞれ30点満点（各問：処理3点＋出力2点）。Bが空欄の問題は、Bの得点にもAの解答を使います。\n'
            '- 問題1-5は指定された計算を順番にコードで行うこと。結果の数値だけを書いても処理の点はつきません。\n'
            '- 実行結果を残して保存。「すべて実行」は使わず、必要なセルだけを実行します。最後に、途中でも `week09_quiz_氏名.ipynb` をUNIPAへ1回だけ提出します。\n'
            '- この小テストと関数チャレンジは別の提出です。')]
        for ident, text in config['questions']:
            cells.append(course.mdcell('## 小テスト①問題'+ident+'（各ラウンド5点）\n\n'+text))
            for phase, label in [('a', ROUND_A), ('b', ROUND_B)]:
                cell = course.codecell('# '+label+'\n')
                cell['metadata']['tags'] = ['quiz-round-'+phase]
                cells.append(cell)
        cells += [course.mdcell('## メモ（任意）\n\n途中まで考えたことや、動かなかった箇所があれば短く記す。')]
        notebook = private/'quiz-01.ipynb'
        course.notebook(notebook, cells)
        existing = json.loads(target.read_text()) if target.exists() else None
        payload = package(notebook.read_bytes(), config['passphrase'], existing)
        course.write(target, json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    elif not target.exists():
        raise FileNotFoundError('The private quiz source or an encrypted package is required.')


def build_page(root, c, header, version):
    bi, p = c.bi, c.p
    archive = root/'weeks/week-09/quiz-01.ipynb'
    notebook = json.loads(archive.read_text(encoding='utf-8'))
    answers = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']
    expected = ['# '+label for label in (ROUND_A, ROUND_B)]*6
    if ([cell['source'].strip() for cell in answers] != expected
            or any(cell['outputs'] or cell['execution_count'] is not None for cell in answers)):
        raise ValueError('The public quiz archive must contain only blank answer cells.')
    head = c.page_head('Week 09 · 小テスト①','course-pages.css','course-page.js',version)
    head += f'<link rel="stylesheet" href="../week-08/bicycle-week.css"><script src="../../assets/site.js?v={version}" defer></script><script src="quiz-archive.js?v={version}" defer></script></head>'
    body = '<h1>'+bi('小テスト①','Quiz 01')+'</h1>'+p(
        '11月26日に実施した小テストです。問題を見直したり、解答欄が空のNotebookで練習したりできます。',
        'Review the November 26 quiz questions or practice with the blank notebook.')
    body += p('AはAIなしで6分。合図で保存し、次の6分はAIを使ってBだけ修正できます。提出はNotebook 1ファイルです。',
              'A: six minutes without AI. Save at the signal, then take six minutes to revise in B with AI if you choose. Submit one notebook.')
    body += '<div class="quiz-entry" data-quiz-archive><a class="quiz-download" href="quiz-01.ipynb" download="week09_quiz.ipynb">'+bi('小テストNotebookをダウンロード','Download quiz notebook')+' ↓</a><details open><summary>'+bi('問題をプレビュー','Preview the questions')+'</summary><div data-quiz-preview aria-busy="true"></div></details></div>'
    c.write(root/'weeks/week-09/quiz.html',head+f'<body class="course-challenge bicycle-week quiz-page" data-release="{QUIZ_RELEASE}">'+header+'<main id="course-page" hidden>'+body+'</main></body></html>')
