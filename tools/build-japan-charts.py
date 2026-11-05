"""Build the chart reference page and notebook by executing the displayed Python.

Run from the repository with admin/.venv/bin/python tools/build-japan-charts.py.
Only this trusted example code is executed; student notebooks are not read.
"""
from pathlib import Path
from contextlib import redirect_stdout
import base64
import html
import io
import json
import os

os.environ.setdefault('MPLCONFIGDIR', '/tmp/programming-chart-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'weeks/week-06'
ASSETS = DEST / 'japan-charts'
ASSETS.mkdir(exist_ok=True)

SETUP = '''import csv
import matplotlib.pyplot as plt

# Put japan.csv in the same folder as your notebook.
with open("japan.csv", encoding="utf-8-sig", newline="") as file:
    data = list(csv.DictReader(file))

print(len(data), "prefectures")
print(data[0]["Prefecture"], data[0]["総人口"])'''

EXAMPLES = [
    dict(id='bar', title='棒グラフ / Bar chart', question='人口が多い都道府県は？ / Which prefectures have the largest populations?',
         note='<code>sorted(..., key=..., reverse=True)</code>で人口順に並べ、<code>[:5]</code>で上位5件。<code>key=lambda row: ...</code>は各行から並べ替えに使う値を取り出します。<code>int()</code>で文字列を数値にし、100万で割って百万人単位にします。<code>plt.bar(x, height)</code>の第1引数は名前、第2引数は高さ。',
         read='棒の高さは人口。東京都が最大です。縦軸は0から始まります。 / Height represents population, in millions.',
         code='''top5 = sorted(data, key=lambda row: int(row["総人口"]), reverse=True)[:5]
names = [row["Prefecture"] for row in top5]
population = [int(row["総人口"]) / 1_000_000 for row in top5]

plt.figure(figsize=(8, 4))
plt.bar(names, population, color="#315876")
plt.ylabel("Population (millions)")
plt.title("Five most populous prefectures")
plt.tight_layout()
plt.show()'''),
    dict(id='barh', title='横棒グラフ / Horizontal bar chart', question='高齢者の割合が高いのは？ / Where is the share aged 65+ highest?',
         note='<code>65歳以上人口 / 総人口 * 100</code>で割合（%）を計算。人数の多さと割合の高さは違います。<code>plt.barh()</code>は横棒。<code>invert_yaxis()</code>で最大値を上にします。',
         read='人口の大小にかかわらず、高齢者の割合で比べます。 / Compare shares rather than counts.',
         code='''top5 = sorted(data,
              key=lambda row: int(row["65歳以上人口"]) / int(row["総人口"]),
              reverse=True)[:5]
names = [row["Prefecture"] for row in top5]
shares = [int(row["65歳以上人口"]) / int(row["総人口"]) * 100 for row in top5]

plt.figure(figsize=(8, 4))
plt.barh(names, shares, color="#3f6d57")
plt.gca().invert_yaxis()
plt.xlabel("Population aged 65+ (%)")
plt.title("Five highest shares aged 65+")
plt.tight_layout()
plt.show()'''),
    dict(id='stacked', title='年齢の積み上げ棒グラフ / Stacked bar', question='人口の年齢構成を比べよう / Compare age composition.',
         note='<code>bottom=young</code>で2段目の開始位置を指定。3段目の<code>base</code>は下の2段の合計です。<code>label</code>と<code>legend()</code>で凡例を表示。これは人数の積み上げで、100%積み上げではありません。',
         read='棒全体は3年齢区分の合計。構成比を比べたい場合は各区分を合計で割ります。CSVでは総人口と3区分の合計に差がある県もあるので、必ず確認しよう。 / These are counts, not percentages; check age totals against total population.',
         code='''chosen = [row for row in data
          if row["Prefecture"] in ["Tokyo", "Chiba", "Akita", "Okinawa"]]
names = [row["Prefecture"] for row in chosen]
young = [int(row["15歳未満人口"]) / 1_000_000 for row in chosen]
working = [int(row["15～64歳人口"]) / 1_000_000 for row in chosen]
older = [int(row["65歳以上人口"]) / 1_000_000 for row in chosen]
base = [young[i] + working[i] for i in range(len(chosen))]

plt.figure(figsize=(8, 4))
plt.bar(names, young, label="Under 15", color="#d9ac60")
plt.bar(names, working, bottom=young, label="15-64", color="#315876")
plt.bar(names, older, bottom=base, label="65+", color="#3f6d57")
plt.ylabel("Population (millions)")
plt.title("Age composition in four prefectures")
plt.legend()
plt.tight_layout()
plt.show()'''),
    dict(id='stacked-100', title='100%積み上げ棒グラフ / 100% stacked bar', question='人口の規模をそろえ、年齢構成の割合を比べよう / Compare age shares on the same scale.',
         note='各年齢区分を<code>3区分の合計</code>で割り、100を掛けます。これで、どの県も棒全体が100%になります。<code>plt.ylim(0, 100)</code>だけでは割合に変換されません。CSVでは総人口と年齢区分の合計に小さな差がある県もあるため、この図は「3年齢区分に占める割合」です。',
         read='人数の積み上げと同じ4県・同じ色です。人口の多さは見えなくなり、構成比を比較しやすくなります。秋田県と沖縄県の65歳以上の割合はどう違う？ / Equal heights show composition, not population size.',
         code='''chosen = [row for row in data
          if row["Prefecture"] in ["Tokyo", "Chiba", "Akita", "Okinawa"]]
names = [row["Prefecture"] for row in chosen]
young = [int(row["15歳未満人口"]) for row in chosen]
working = [int(row["15～64歳人口"]) for row in chosen]
older = [int(row["65歳以上人口"]) for row in chosen]

# Divide each age group by the sum of all three age groups.
totals = [young[i] + working[i] + older[i] for i in range(len(chosen))]
young = [young[i] / totals[i] * 100 for i in range(len(chosen))]
working = [working[i] / totals[i] * 100 for i in range(len(chosen))]
older = [older[i] / totals[i] * 100 for i in range(len(chosen))]
base = [young[i] + working[i] for i in range(len(chosen))]

plt.figure(figsize=(8, 4))
plt.bar(names, young, label="Under 15", color="#d9ac60")
plt.bar(names, working, bottom=young, label="15-64", color="#315876")
plt.bar(names, older, bottom=base, label="65+", color="#3f6d57")
plt.ylim(0, 100)
plt.ylabel("Share of the three age groups (%)")
plt.title("Age composition: every bar totals 100%")
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.show()'''),
    dict(id='histogram', title='ヒストグラム / Histogram', question='高齢者の割合は、どの範囲に集中する？ / How are the 47 shares distributed?',
         note='<code>plt.hist(values, bins=8)</code>は数値を8区間に分け、各区間に入る都道府県の数を数えます。棒グラフの「都道府県ごと」と異なり、横軸は数値の範囲です。<code>bins</code>を変えると分布の見え方も変わります。',
         read='横軸は65歳以上の割合、縦軸は都道府県数。47件の分布であり、47人の年齢分布ではありません。 / Each observation is a prefecture.',
         code='''shares = [int(row["65歳以上人口"]) / int(row["総人口"]) * 100
          for row in data]

plt.figure(figsize=(8, 4))
plt.hist(shares, bins=8, color="#315876", edgecolor="white")
plt.xlabel("Population aged 65+ (%)")
plt.ylabel("Number of prefectures")
plt.title("Distribution across all 47 prefectures")
plt.tight_layout()
plt.show()'''),
    dict(id='boxplot', title='箱ひげ図 / Box plot', question='中央値とばらつきを一目で見る / Summarize the same 47 shares.',
         note='<code>plt.boxplot(shares)</code>で同じ47件を要約。箱は第1〜第3四分位数（中央の約50%）、箱の中の線は中央値。ひげは箱から1.5×四分位範囲以内の最遠点まで伸び、その外は点で表示されます。ひげが必ず最小値・最大値とは限りません。',
         read='箱ひげ図は個々の県名を示しません。どの県か知りたいときは、横棒グラフや表も使います。 / A dot beyond a whisker is not automatically a data error.',
         code='''shares = [int(row["65歳以上人口"]) / int(row["総人口"]) * 100
          for row in data]

plt.figure(figsize=(8, 4))
plt.boxplot(shares)
plt.xticks([1], ["47 prefectures"])
plt.ylabel("Population aged 65+ (%)")
plt.title("Spread of the share aged 65+")
plt.tight_layout()
plt.show()'''),
    dict(id='boxplot-prefectures', title='県ごとに並べる箱ひげ図 / Side-by-side prefectures', question='同じ支出項目を、4県で比べよう / Compare the same spending categories across four prefectures.',
         note='1県につき1つの数値だけでは、その県の分布を比較できません。この例は各県の<strong>食料費・住居費・教養娯楽費の3項目</strong>を使います。<code>values</code>は「県ごとのリストを並べたリスト」。<code>plt.boxplot(values)</code>は内側のリストごとに箱を作ります。<code>plt.xticks()</code>で県名を付け、色付きの点で各項目の実際の値も示します。<code>enumerate()</code>は0・1・2の番号と項目名を取り出し、同じ項目の値を各県から集めます。',
         read='各箱の観測値は3つの支出項目です。住民や世帯の個票データではないため、「この県の世帯の支出のばらつき」とは言えません。3項目だけの箱は要約が粗いので、点や表も確認しよう。住民の年齢などを県別の箱で比べるには、各県に複数の観測値がある別のデータが必要です。 / Each box summarizes three category values, not the distribution of individual households.',
         code='''chosen = [row for row in data
          if row["Prefecture"] in ["Tokyo", "Chiba", "Akita", "Okinawa"]]
names = [row["Prefecture"] for row in chosen]
columns = ["食料費（二人以上の世帯）", "住居費（二人以上の世帯）",
           "教養娯楽費（二人以上の世帯）"]
values = [[int(row[column]) for column in columns] for row in chosen]

plt.figure(figsize=(8, 4))
plt.boxplot(values)
plt.xticks(range(1, len(names) + 1), names)

# Show the three actual values inside each prefecture's summary.
for category, label in enumerate(["Food", "Housing", "Recreation"]):
    amounts = [row[category] for row in values]
    plt.scatter(range(1, len(names) + 1), amounts, label=label, zorder=3)

plt.ylabel("Reported spending (CSV values)")
plt.title("Three spending categories per prefecture")
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.show()'''),
    dict(id='scatter', title='散布図 / Scatter plot', question='2つの数値の関係を探す / Compare two variables.',
         note='<code>plt.scatter(x, y)</code>は1県を1点で表します。<code>x</code>と<code>y</code>は同じ順序・同じ件数にします。<code>alpha=0.7</code>は透明度。関係が見えても、それだけで原因とは言えません。',
         read='横軸は高齢者の割合、縦軸は合計特殊出生率。合計特殊出生率は出生数でも人口に占める出生割合でもありません。 / Association does not establish causation.',
         code='''shares = [int(row["65歳以上人口"]) / int(row["総人口"]) * 100
          for row in data]
fertility = [float(row["合計特殊出生率"]) for row in data]

plt.figure(figsize=(8, 4))
plt.scatter(shares, fertility, color="#3f6d57", alpha=0.7)
plt.xlabel("Population aged 65+ (%)")
plt.ylabel("Total fertility rate")
plt.title("Age structure and fertility: 47 prefectures")
plt.tight_layout()
plt.show()'''),
    dict(id='loop', title='forで複数のグラフ / One loop, two charts', question='同じ処理を、違う県に使う / Repeat a chart for each prefecture.',
         note='<code>for row in chosen:</code>で1県ずつ処理。<code>plt.figure()</code>をループ内に置き、県ごとに新しい図を作ります。<code>f"...{...}..."</code>でタイトルも変わります。リスト内包表記の角括弧も「各データから値を取り出す」繰り返しです。',
         read='県名を追加すれば、その県のグラフも作られます。比べやすくするため、縦軸を両方とも0〜100に固定しています。 / Add a prefecture name to make another chart.',
         code='''chosen = [row for row in data if row["Prefecture"] in ["Tokyo", "Chiba"]]

for row in chosen:
    total = int(row["総人口"])
    shares = [int(row["15歳未満人口"]) / total * 100,
              int(row["15～64歳人口"]) / total * 100,
              int(row["65歳以上人口"]) / total * 100]

    plt.figure(figsize=(8, 4))
    plt.bar(["Under 15", "15-64", "65+"], shares,
            color=["#d9ac60", "#315876", "#3f6d57"])
    plt.ylim(0, 100)
    plt.ylabel("Share of population (%)")
    plt.title(f"Age composition: {row['Prefecture']}")
    plt.tight_layout()
    plt.show()'''),
]

def code_block(code):
    return '<pre><code class="language-python">' + html.escape(code) + '</code></pre>'

namespace = {}
original_dir = Path.cwd()
os.chdir(ROOT / 'weeks/week-05')
stream = io.StringIO()
with redirect_stdout(stream):
    exec(SETUP, namespace)
setup_output = stream.getvalue()
assert len(namespace['data']) == 47
assert all(int(r['総人口']) > 0 for r in namespace['data'])

cells = []
def markdown(source):
    cells.append(dict(cell_type='markdown', metadata={}, source=source))
def code_cell(code, outputs):
    cells.append(dict(cell_type='code', metadata={}, source=code, execution_count=sum(c['cell_type']=='code' for c in cells)+1, outputs=outputs))

markdown('# Japan chart examples / 日本データのグラフ例\nRun the setup first; put japan.csv beside this notebook. Uses csv and Matplotlib; pandas is not required.\nOutputs are generated from the course japan.csv (47 prefectures), not current live statistics.')
code_cell(SETUP, [dict(output_type='stream', name='stdout', text=setup_output)])
sections = []
for number, example in enumerate(EXAMPLES, 1):
    rendered = []
    outputs = []
    def capture(*args, **kwargs):
        figure = plt.gcf()
        filename = f'{example["id"]}-{len(rendered)+1}.png'
        buffer = io.BytesIO()
        figure.savefig(buffer, format='png', dpi=150, facecolor='white')
        png = buffer.getvalue()
        (ASSETS / filename).write_bytes(png)
        rendered.append(f'<img src="japan-charts/{filename}" width="1200" height="600" loading="lazy" alt="{html.escape(figure.axes[0].get_title())}">')
        outputs.append(dict(output_type='display_data', metadata={}, data={'image/png':base64.b64encode(png).decode(), 'text/plain':'<Matplotlib chart>'}))
        plt.close(figure)
    plt.show = capture
    exec(example['code'], namespace)
    assert len(rendered) == (2 if example['id']=='loop' else 1)
    markdown(f'## {number}. {example["title"]}\n{example["question"]}')
    code_cell(example['code'], outputs)
    sections.append(f'''<section id="{example['id']}" class="example">
<p class="eyebrow">{number:02d} / PYTHON → OUTPUT</p><h2>{example['title']}</h2>
<p class="question">{example['question']}</p>
<p class="explanation">{example['note']}</p>{code_block(example['code'])}
<figure><figcaption>実行結果 / Actual output · japan.csv</figcaption>{''.join(rendered)}</figure>
<p class="reading">{example['read']}</p></section>''')
os.chdir(original_dir)
notebook=dict(nbformat=4, nbformat_minor=4, metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}}, cells=cells)
(DEST / 'japan-chart-examples.ipynb').write_text(json.dumps(notebook, ensure_ascii=False, indent=1)+'\n')
toc=''.join(f'<a href="#{e["id"]}"><span>{i:02d}</span> {e["title"]}</a>' for i,e in enumerate(EXAMPLES,1))
page=f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Japan chart snippets · Week 06 Programming</title><link rel="icon" href="../../favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="japan-charts.css"><link rel="stylesheet" href="../../assets/copy-blocks.css">
<script src="japan-charts.js" defer></script><script src="../../assets/copy-blocks.js" defer></script></head>
<body><a class="skip" href="#main">本文へ / Skip to examples</a><div id="chart-page" hidden>
<aside><a class="back" href="japan-report.html">← 課題に戻る / Report Part 2</a>
<nav aria-label="目次 / Table of contents"><p class="eyebrow">CODE SNIPPETS / 目次</p><a href="#setup"><span>00</span> 準備 / Load the data</a>{toc}</nav>
<div class="downloads"><a href="../week-05/japan.csv" download>↓ japan.csv</a><a href="japan-chart-examples.ipynb" download>↓ 実行済みNotebook / .ipynb</a><a href="../../agenda.html?open=06#week-06">授業予定 / Agenda ↗</a></div></aside>
<main id="main"><header><p class="eyebrow">WEEK 06 · JAPAN DATA / CHART REFERENCE</p><h1>問いに合う、<br>グラフを選ぼう。</h1><p class="intro">Choose a chart that answers your question.</p>
<p>日本の47都道府県のデータで、短いPythonコードと実際の結果を見比べよう。コードをコピーし、自分のNotebookで試してください。全部を使う必要はありません。</p>
<p class="small">すべて授業の <a href="../week-05/japan.csv" download>japan.csv</a> からPythonで生成した出力です。ライブ統計ではありません。図のラベルは日本語フォントの設定なしで使えるよう英語です。<br>Actual Python outputs from the course CSV. Chart labels use English to avoid font setup.</p></header>
<section id="setup" class="example"><p class="eyebrow">00 / START HERE</p><h2>準備 / Load the data</h2>
<p>新しい空のNotebookを作り、<strong>同じフォルダにjapan.csvを置く</strong>。最初にこのCode Cellを実行。その後は好きなグラフのコードを別のCellに貼り付けます。説明・問い・気づきはMarkdown Cellに書こう。</p>
<p><code>csv</code>はPython標準ライブラリ。<a href="https://matplotlib.org/stable/users/getting_started/">Matplotlib</a>はグラフを描くライブラリ、<code>plt</code>はその呼び名です。<strong>pandasは使いませんが、グラフにはMatplotlibが必要です。</strong></p>
<details><summary>Matplotlibが見つからないとき / ModuleNotFoundError</summary><p>NotebookのCode Cellで <code>%pip install matplotlib</code> を実行し、必要ならカーネルを再起動して準備Cellを実行し直します。インストールできない場合は、課題ページの文字のランキングや表でレポートを作って構いません。</p></details>
<p><code>csv.DictReader</code>は1行を辞書として読み込み、<code>list()</code>で47行をリストにします。CSVの値は文字列なので、計算では<code>int()</code>や<code>float()</code>で数値に変えます。</p>
{code_block(SETUP)}<div class="text-output" data-no-copy><p class="eyebrow">OUTPUT</p><pre>{html.escape(setup_output)}</pre></div>
<p class="small">共通：<code>figure()</code>で新しい図、<code>title()</code>でタイトル、<code>xlabel()</code>・<code>ylabel()</code>で軸名と単位、<code>tight_layout()</code>で余白を調整、<code>show()</code>で表示。リスト内包表記 <code>[値 for row in data]</code> は、forで各行から値を集める短い書き方です。</p></section>
{''.join(sections)}
<footer><h2>グラフの下に、一文を。 / Explain what you found.</h2><p>「何を比較したか → 何がわかったか → この組織にとって何を意味するか」。結果を見て、自分の言葉で説明しよう。</p><a href="japan-report.html">課題・提出方法に戻る / Back to the assignment →</a>
<p class="small">公式リファレンス / Matplotlib: <a href="https://matplotlib.org/stable/plot_types/basic/bar.html">bar</a> · <a href="https://matplotlib.org/stable/plot_types/stats/hist_plot.html">hist</a> · <a href="https://matplotlib.org/stable/plot_types/stats/boxplot_plot.html">boxplot</a></p></footer></main></div></body></html>'''
(DEST / 'japan-charts.html').write_text(page)
print(f'Built {len(EXAMPLES)} examples, {sum(len(c.get("outputs", [])) for c in cells[2:])} chart PNGs, and an executed notebook from 47 CSV rows.')
