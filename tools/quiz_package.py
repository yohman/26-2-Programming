"""Package a classroom quiz for a password-unlocked browser download.

Question text and the temporary passphrase live only under ignored admin/.course-private/week08/.
A checkout without that private source reuses the already encrypted package.
"""
from pathlib import Path
import base64, hashlib, json, secrets

ITERATIONS = 250_000

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
                filename='week08_quiz.ipynb', mime='application/x-ipynb+json')

def build(root, course):
    private = root/'admin/.course-private/week08'
    target = root/'weeks/week-08/quiz-01.enc.json'
    source = private/'quiz-source.json'
    if source.exists():
        config = json.loads(source.read_text())
        cells = [course.mdcell('# Week 08 小テスト①（成績評価対象）\n\n氏名：\n\n2026年11月19日／個人・6問・30点満点（各5点）\n\n準備できたら、教員の合図から12分。13:45を目安に提出します。\n\n- 最初の6分：自分で解く（この問題文とHintのみ）。\n- 次の6分：教科書・ノート・教材・通常のWeb検索を使ってよい。\n- 12分を通して、生成AI・他者との相談・他者の解答のコピーは不可。\n- 採点：各問、指定された処理3点＋指定どおりの出力2点。未完成でも途中のコードを残してください。\n- 問題1-5は指定された計算を順番にコードで行うこと。結果の数値だけを書いても処理の点はつきません。\n- 解けたセルを実行し、出力を保存。`week08_quiz_氏名.ipynb`としてUNIPAへ提出。未完成でも提出してください。\n- この小テストと後半の自転車盗レポートは別の提出です。')]
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
    # Old direct-download URLs must no longer expose the plaintext notebook.
    (root/'weeks/week-08/quiz-01.ipynb').unlink(missing_ok=True)
