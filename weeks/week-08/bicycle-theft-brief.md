# Chiba Bicycle Theft Challenge

## あなたの新しい任務

<img src="https://www.police.pref.chiba.jp/content/admin/logo_header.png" alt="Chiba Police" width="300"/>

あなたは千葉県警に新しく採用された新人捜査員です。最初の仕事として、  
**「千葉県内で過去1年間に発生した自転車盗難の状況をまとめたレポート」** を  
来週までに提出するように命じられました。

あなたの任務：
- 自転車盗難件数をまとめる  
- 被害者の特徴（年齢・性別など）が分かればまとめる  
- どの地域で盗難が多いかを示す  
- どの月が最も多いか  
- どの時間帯に多いか  
- 鍵の有無によって盗難件数は変わるのか（Impactのある考察）
- その他、興味深い発見があればまとめる

提出形式は **Jupyter Notebook (.ipynb)**。  
コード、グラフ、Markdownによる説明を入れてレポートとしてまとめてください。  


## 課題内容
1. 千葉県警のオープンデータページにアクセスする：  
   https://www.police.pref.chiba.jp/seisoka/safe-life_publicspace-statistics_00002.html  

2. ページ内の **「自転車盗（CSV形式）」データ** を自分のPCにダウンロードする。  

3. VS Code で **Jupyter Notebook（.ipynb）** を作成し、このデータを使って  
   - まとめ（summary）  
   - 分析（analysis）  
   - 可視化（visualization：グラフなど）  
   を行う Notebook を完成させる。  

4. 完成した Notebook を **GitHub にコミット**し、その URL を提出する。  
   今日の授業内でスタートし、続きは宿題として完成させる。

---

## How to Begin（スタートガイド）

### 1. フォルダと Notebook の準備
- VS Code を開く  
- 自分の GitHub リポジトリ（例：「me」）の中に、今日の授業用フォルダ（例：`Week8`）を作成  
- そのフォルダの中に `jitensha.ipynb` を作成  
- ダウンロードした自転車盗データ（CSV）を同じフォルダに保存（例：`jitensha.csv`）

### 2. pandas でデータを読み込む

```python
import pandas as pd

df = pd.read_csv("jitensha.csv")
df.head()
```

### ヒント：分析の始め方


#### 市区町村ごとの件数を出す
```python
df.groupby('市区町村（発生地）').size().sort_values(ascending=False)
```

#### 時間帯を作る（例：深夜・朝・昼・夕方）
```python
df.groupby('発生時（始期）').size().sort_values(ascending=False)
```

#### 鍵の有無による Impact を見る
```python
df.groupby('施錠関係').size()
```

#### 月ごとの件数を出す
```python
df['発生日'] = pd.to_datetime(df['発生年月日（始期）'], format="%Y%m%d", errors='coerce')
df['月'] = df['発生日'].dt.month
df.groupby('月').size()
```

### 被害者の職業
```python
df.groupby('被害者職業').size().sort_values(ascending=False)
```

### 3. 可視化の例

```python
# bar graph of 被害者の職業
import matplotlib.pyplot as plt

# fix japanese font issue for mac
plt.rcParams['font.family'] = 'Hiragino Sans'

# fix japanese font issue for windows
plt.rcParams['font.family'] = 'MS Gothic'

occupation_counts = df['被害者の職業'].value_counts().head(10)  # top 10 occupations
occupation_counts.plot(kind='bar')
plt.xlabel('被害者の職業')
plt.ylabel('件数')
plt.title('被害者の職業別自転車盗難件数（上位10件）')
plt.show()
```

---

## Notebook に含めてほしい内容
1. **データの基本情報**  
2. **簡単な集計・分析**  
3. **可視化（グラフ）** (ひとつ以上)  
4. **Markdown での説明**

---

## 提出
- 完成した `jitensha.ipynb` を GitHub にコミット  
- Notebook への **直接リンク** を提出  
- 授業中にできなかった部分は宿題として完成させる  

## Super Challenge (任意)!

Warning：難易度高めです。時間があれば挑戦してください。

- folium を使って盗難発生地点のマップを作成する

* Hint: 緯度・経度のカラムはないので、  
  住所から緯度・経度を取得する必要があります。  
  
