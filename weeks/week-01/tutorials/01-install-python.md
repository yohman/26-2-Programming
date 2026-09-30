# Tutorial 01 — Pythonをインストールする

Pythonは、書いたcodeを動かす**エンジン**です。インストールして、一度だけ動作を確認します。

> **GOAL / ゴール：** Python 3のversionが表示され、`print()`を一行実行できる。

<!-- tabs:start -->
### Windows

## 1. Install

1. [Python公式ダウンロードページ](https://www.python.org/downloads/)を開く。
2. **Download Python install manager**を選び、downloadしたfileを開く。
3. **Install**を選ぶ。終了したらPowerShellを開き直す。

> **TIP / ヒント：** Microsoft Storeが開いたら、発行元が**Python Software Foundation**であることを確認する。

## 2. Check

PowerShellで次を実行します。

```text
python --version
```

`Python 3.x.x`と表示されたら、続けて試します。

```text
python
```

```python
print("Python is ready!")
```

終了するときは`exit()`と入力します。

| うまくいかない | まず試すこと |
| --- | --- |
| `python`が見つからない | PowerShellを閉じて開き直す。 |
| Storeが開く | Python Install Managerをinstallする。 |

### macOS

## 1. Install

1. [Python公式macOSダウンロードページ](https://www.python.org/downloads/macos/)を開く。
2. 最新の安定版の**macOS installer**をdownloadする。`pre-release`は選ばない。
3. `.pkg`を開き、**Continue → Install**で完了する。

## 2. Check

`Command + Space`でTerminalを開き、次を実行します。

```text
python3 --version
```

`Python 3.x.x`と表示されたら、続けて試します。

```text
python3
```

```python
print("Python is ready!")
```

終了するときは`exit()`と入力します。

> **TIP / ヒント：** macOSでは確認するときに`python`ではなく`python3`を使う。

| うまくいかない | まず試すこと |
| --- | --- |
| `command not found` | Terminalを閉じて開き直す。 |
| installerが開かない | downloadが完了し、file名が`.pkg`で終わるか確認する。 |
<!-- tabs:end -->

> **CHECK / 確認：** Python 3のversionと`Python is ready!`の両方が表示されれば完了。
