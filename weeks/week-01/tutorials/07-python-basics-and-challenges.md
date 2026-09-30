# Tutorial 07 — Python Basics

同じcycleで進めます。

> **読む → 予想する → 実行する → 一つ変える → 変化を書く**

> **GOAL / ゴール：** 値、variable、計算、inputを組み合わせ、小さなprogramを作る。

## 1. Outputと値

```python
print("10")
print(10)
print(10.5)
```

`"10"`は文字、`10`は整数、`10.5`は小数です。

```python
print(type("10"))
print(type(10))
print(type(10.5))
```

> **AHA!：** 見た目が同じ`10`でも、引用符があると文字、ないと数字になる。

## 2. Variableと計算

```python
price = 180
count = 3
total = price * count
print(total)
```

`price`か`count`を変え、Outputを予想してから実行します。

| 記号 | 意味 |
| --- | --- |
| `+` / `-` | 足す / 引く |
| `*` / `/` | 掛ける / 割る |

```python
name = "Aki"
score = 85
print(f"{name}さんのscoreは{score}です。")
```

> **AHA!：** `=`は「同じ」ではなく、右の値を左の名前に覚えさせる命令。

## 3. Inputを使う

```python
name = input("名前は？ ")
print(f"Hello, {name}!")
```

数字を計算するときは`int()`または`float()`へ変換します。

```python
age = int(input("年齢は？ "))
print(f"次の誕生日には{age + 1}歳です。")
```

> **TIP / ヒント：** `input()`のanswerは最初は文字。数字として計算するときだけ変換する。

## 4. Errorを手がかりにする

次はそのままでは動きません。

```python
age = input("年齢は？ ")
print(age + 1)
```

Errorの最後にある`TypeError`を読み、どこへ`int()`を加えるか考えて直します。

> **AHA!：** Errorは「失敗」ではなく、Pythonが理解できなくなった場所のreport。

## Local Challenge — 一つ選ぶ

完成したら、直下のMarkdown cellに**何を変え、何を確認したか**を一文書きます。

### A. Profile card

名前、好きなもの、今日の気分をvariableに保存し、f-stringで一つのcardとして表示する。

- 必須：三つのvariable、f-string
- Extra：数字のvariableを一つ加える

### B. Useful calculation

合計金額、移動時間、残り時間など、自分の生活に関係する計算を作る。

- 必須：二つの数字、variable、計算、単位
- Extra：別の値で二回目をtestする

### C. Ask and respond

実行した人へ質問し、answerを使った結果を返す。

- 必須：`input()`、variable、f-string
- Extra：数字を受け取り、計算する

> **CHECK / 確認：** Run AllでErrorなく完了し、Codeの意味と自分が変えた場所を説明できる。
