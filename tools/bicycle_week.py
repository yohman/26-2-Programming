"""Week 8: original 2025 quiz and an evidence-based bicycle-theft report.

Build only this week: admin/.venv/bin/python tools/bicycle_week.py
The archived source notebooks are read-only references, never executed.
"""
from pathlib import Path
import ast
import base64
import contextlib
import csv
import html
import io
import json
import re
import sys

VERSION = '20261118-bike-quiz'
RELEASE = '2026-11-19T12:00:00+09:00'
POLICE = 'https://www.police.pref.chiba.jp/seisoka/safe-life_publicspace-statistics_00002.html'
SPEC = dict(title='Bicycle theft: what does the data say?', title_ja='自転車盗を、データで調べる', date='2026-11-19', due='2026-11-25', slides=[{}]*16)

LOAD = '''
# 読み込むファイルを設定する（Notebookと同じフォルダに保存）
filename = "bicycle-theft.csv"

# Python標準のcsvで読む。追加インストールは不要
import csv
with open(filename, encoding="utf-8-sig", newline="") as file:
    incidents = list(csv.DictReader(file))

# 1行が1件の事件。件数を確認する
len(incidents)'''.strip()
ROW = '''
# 最初の事件から、必要な列を選んで確認する
row = incidents[0]
row["市区町村（発生地）"], row["発生時（始期）"], row["施錠関係"]'''.strip()
COUNT = '''
# 集計したい列を選ぶ
column = "施錠関係"
counts = {}

# 同じ値が出てくるたびに、件数を1増やす
for row in incidents:
    label = row[column]
    counts[label] = counts.get(label, 0) + 1

counts'''.strip()
FILTER = '''
# 調べたい市区町村を指定する
city = "柏市"
selected = []

# 条件に合う事件だけ、新しいリストへ入れる
for row in incidents:
    if row["市区町村（発生地）"] == city:
        selected.append(row)

len(selected)'''.strip()
RANK = '''
column = "市区町村（発生地）"
top_n = 5

# Counterは標準ライブラリ。未登録の値は0件から数える
from collections import Counter
counts = Counter()
for row in incidents:
    counts[row[column]] += 1

# 件数の多い上位5組を取り出す
top_places = counts.most_common(top_n)
top_places'''.strip()

BARS = '''
# 棒1個を何件にするか設定する
scale = 100

# 正確な件数も表示する（棒の長さは100件未満を切り捨て）
for place, count in top_places:
    bar = "█" * (count // scale)
    print(f"{place}: {bar} {count:,}件")'''.strip()
PANDAS = '''
# pandasが使える場合の別ルート。同じCSVを読む
filename = "bicycle-theft.csv"
import pandas as pd
df = pd.read_csv(filename)

# 列を1本選び、値ごとの件数を多い順に表示する
df["市区町村（発生地）"].value_counts().head(5)'''.strip()
PANDAS_LOOP = '''
# 比較する市区町村を、先に設定する
cities = ["柏市", "松戸市", "流山市"]

# 市名をforで順に変え、条件に合う行だけ数える
for city in cities:
    selected_df = df[df["市区町村（発生地）"] == city]
    print(city, len(selected_df))'''.strip()

PLOT = '''
# グラフの文字は英語にして、追加フォントを不要にする
import matplotlib.pyplot as plt
lock_counts = df["施錠関係"].value_counts()
lock_counts.index = lock_counts.index.map({
    "施錠せず": "Unlocked", "施錠した": "Locked"
})

# 棒グラフを描く
lock_counts.plot.bar(color=["#315876", "#98b1a1"], rot=0)
plt.xlabel("Lock status")
plt.ylabel("Reported thefts")
plt.title("Lock status in the supplied Chiba CSV")
plt.tight_layout()
plt.show()'''.strip()
MONTHS = '''
# 日付の先頭6文字（年・月）で数える。違う年の同じ月を混ぜない
counts_by_month = {}
unknown_dates = 0
for row in incidents:
    date = row["発生年月日（始期）"]
    if len(date) == 8 and date.isdigit():
        month = date[:6]
        counts_by_month[month] = counts_by_month.get(month, 0) + 1
    else:
        unknown_dates += 1

# 年月の文字列を並べると、時間順になる
for month in sorted(counts_by_month):
    print(month, counts_by_month[month])
print("Unknown dates:", unknown_dates)'''.strip()
HOURS = '''
# 時刻が不明の事件は、0時に変えず別に数える
hours = {}
unknown_hours = 0
for row in incidents:
    value = row["発生時（始期）"]
    if value.isdigit():
        hour = int(value)
        hours[hour] = hours.get(hour, 0) + 1
    else:
        unknown_hours += 1

for hour in sorted(hours):
    print(f"{hour:02}:00", hours[hour])
print("Unknown hours:", unknown_hours)'''.strip()

# Verbatim question text and hints from the 2025 quiz; no solutions.
QUESTIONS = [
('1-1', 'Pythonで\n```\nReitaku University\n```\nと表示するプログラムを作成せよ。'),
('1-2', 'キーボードから2つの文字列を入力する。そのとき、2つの文字列を ` and ` で結んで出力するプログラムを作成せよ。例えば、キーボードから\n```\nあいう\nABC\n```\nが入力されたら\n```\nあいう and ABC\n```\nと出力されるようにせよ。**`and` の前後に半角スペースを入れることを忘れないように**。\n\nHint: 文字列の入力には `input()` 関数を用いる。\n\n```\nstr1 = input()\nstr2 = input()\n```'),
('1-3', 'キーボードからいくつかの文字を半角スペース区切りで入力する。そのとき、最後から1つ前の要素を出力するプログラムを作成せよ。\n例えば、\n```\na b c d e\n```\nが入力されたとき、`d` を出力する。キーボードからは2つ以上の文字が入力されることを前提としてよい。\n\nプログラムの最初に\n```\nmylist = input().split()\n```\nと書くと、キーボードから半角スペース区切りで入力されたいくつかの文字がリスト型変数 `mylist` に入力される。\n\nHint: リストの最後から1つ前の要素は `mylist[-2]` で参照できる。'),
('1-4', 'キーボードから4つの文字を半角スペース区切りで入力する。入力された文字を逆の順番で出力するプログラムを作成せよ。\n\n例えば、キーボードから\n```\n1 2 3 4\n```\nが入力されたとき\n```\n4 3 2 1\n```\nと出力する。\n\n入力される整数の個数が4であることは前提としてよい。\n\nプログラムの先頭に\n```\nmylist = input().split()\n```\nと書くと、キーボードから半角スペース区切りで入力された文字が、リスト型変数 `mylist` に代入される。\n\nHint: リストの要素を逆順に参照するにはスライスを用いる。たとえば、`mylist[::-1]` は `mylist` の要素を逆順にしたリストを表す。'),
('1-5', 'キーボードからある1つの正の整数を入力する。この数に対して\n\n1. 4を足して\n2. 2を掛けて\n3. 6を引いて\n4. 2で割る\n5. キーボードから入力された最初の正の整数を引く\n\nという操作を行った場合の答えを出力するプログラムを作成しなさい。\n\nHint: 途中の計算結果を変数に保存しておくとよい。'),
('1-6', 'キーボードから半角スペース区切りで3つの好きなもの（食べ物、動物、場所など）を入力するとき、次の処理を行うプログラムを作成しなさい。\n\n1. 3つの単語それぞれの末尾に `!` を付けて、1行ずつ表示する（入力された順を保つ）。\n2. 最初と最後の単語を `+` でつないだ文字列を作り、`secret combo: ...` の形式で4行目に表示する。\n\nたとえば `cat pizza coffee` が入力されたら、次のように出力する。\n```\ncat!\npizza!\ncoffee!\nsecret combo: cat+coffee\n```\n\nHint: インデックスを使ってリストの最初と最後の要素を取り出せる。')]


def execute(source, scope, number):
    """Run trusted authored examples, including the notebook's final expression."""
    tree = ast.parse(source)
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        value = None
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            exec(compile(ast.Module(body=tree.body[:-1], type_ignores=[]), '<course>', 'exec'), scope)
            value = eval(compile(ast.Expression(tree.body[-1].value), '<course>', 'eval'), scope)
        else:
            exec(compile(tree, '<course>', 'exec'), scope)
    outputs = []
    if stream.getvalue():
        outputs.append(dict(output_type='stream', name='stdout', text=stream.getvalue()))
    if value is not None:
        data = {'text/plain': repr(value)}
        if hasattr(value, '_repr_html_') and value._repr_html_():
            data['text/html'] = value._repr_html_()
        outputs.append(dict(output_type='execute_result', data=data, metadata={}, execution_count=number))
    return outputs


def build(root, c):
    folder = root/'weeks/week-08'
    bi, p, links = c.bi, c.p, c.links
    with (folder/'bicycle-theft.csv').open(encoding='utf-8-sig', newline='') as f:
        incidents = list(csv.DictReader(f))
    assert len(incidents) == 9943
    source_note = ('2025年度教材から引き継いだ千葉県警公開CSV・9,943件。発生日は2019〜2024年と不明を含む。最新の事件情報ではありません。', 'A frozen Chiba Police CSV from the 2025 materials: 9,943 records, with occurrence dates in 2019–2024 or unknown. This is not live incident data.')
    scope = {}
    results = {}
    cells = [c.mdcell('# 千葉の自転車盗：実行例\n\nこれは解説用の実行例です。提出用は新しい空のNotebookを作成してください。\n\n'+source_note[0]+'\n\n出典：'+POLICE+'\n\n## 1. 準備\n`bicycle-theft.csv` をNotebookと同じフォルダに保存。標準ライブラリのルートは追加インストール不要。')]
    examples = [
        ('load', '2. CSVを読む', 'csv.DictReaderは、各行を「列名: 値」の辞書にします。listで全行をまとめ、lenで件数を確認します。', LOAD),
        ('row', '3. 1件の内容を見る', 'incidentsはリスト、incidents[0]は最初の事件の辞書。列名をキーに値を取り出します。列名一覧は list(incidents[0]) で確認。', ROW),
        ('count', '4. forで数える', 'counts.get(label, 0)は、登録済みなら件数、未登録なら0。その値に1を足して保存します。事件の総数と集計の合計が一致するか確かめよう。', COUNT),
        ('filter', '5. 市区町村を絞る', '==は一致の比較。appendはリストの末尾へ1件追加。市名を変えて再実行し、件数を比較してみよう。', FILTER),
        ('rank', '6. ランキング', 'CounterはPython標準ライブラリ。未登録のキーは0から数えられます。most_common(5)は件数の多い上位5組を返します。件数は人口や駐輪台数で補正した被害率ではありません。', RANK),
        ('bars', '7. pandasなしで棒を描く', '文字の繰り返しで簡単な棒グラフを作れます。棒1個は100件。//は整数の商、:,は3桁ごとの桁区切りです。棒は切り捨てなので、正確な数値も必ず添えます。', BARS),
        ('months', '発展：年月ごとの件数', '日付不明は別に数えます。同じ「9月」でも年が違えば別の集計。既存CSVのため、毎月・毎年が完全な期間とは限りません。', MONTHS),
        ('hours', '発展：時間帯', '不明を0時に変えないでください。発生時（始期）は警察データの項目名です。事件が起きた正確な時刻とは限りません。', HOURS),
    ]
    with contextlib.chdir(folder):
        for number, (key, title, explanation, code) in enumerate(examples, 1):
            outputs = execute(code, scope, number)
            results[key] = ''.join(o.get('text', '') if o['output_type']=='stream' else o['data']['text/plain']+'\n' for o in outputs)
            cell = c.codecell(code, count=number); cell['outputs'] = outputs
            cells += [c.mdcell('## '+title+'\n\n'+explanation), cell]
        # Optional, actually executed pandas and Matplotlib route.
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        outputs = execute(PANDAS, scope, 9)
        cell = c.codecell(PANDAS, count=9); cell['outputs'] = outputs
        cells += [c.mdcell('## 任意：pandasで同じ集計\n\npandas・Matplotlibが使える人向け。使えなくても上のルートで課題を完成できます。\n\n[pandas公式ガイド](https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html)\n\nvalue_counts()は値ごとの件数を降順に並べ、head(5)は先頭5件を表示します。'), cell]
        results['pandas'] = outputs[-1]['data']['text/plain']
        outputs = execute(PANDAS_LOOP, scope, 10)
        loop_cell = c.codecell(PANDAS_LOOP, count=10); loop_cell['outputs'] = outputs
        cells += [c.mdcell('## 任意：pandasとforを組み合わせる\n\npandasを使う場合も、レポートにforを含めます。citiesの市名を自分で選び直し、結果を比較しよう。内側の条件は、列の値がcityと一致する行を選びます。'), loop_cell]
        plt.close('all')
        execute(PLOT.replace('plt.show()', ''), scope, 11)
        image = io.BytesIO(); plt.gcf().savefig(image, format='png', dpi=130)
        png = image.getvalue(); (folder/'bicycle-lock-status.png').write_bytes(png)
        plot_cell = c.codecell(PLOT, count=11)
        plot_cell['outputs'] = [dict(output_type='display_data', metadata={}, data={'image/png': base64.b64encode(png).decode(), 'text/plain': 'Lock status: Unlocked 6781; Locked 3162.'})]
        cells += [c.mdcell('## 任意：Matplotlibの棒グラフ\n\n同じデータを使った実際の出力です。環境ごとの日本語フォント問題を避けるためラベルだけ英訳しています。'), plot_cell]
        plt.close('all')
    cells += [c.mdcell('## 問いに戻る\n\n件数の違いから何が言えますか？ 分母（駐輪台数など）がないため、盗まれる確率や施錠の効果は計算できません。\n\n緯度・経度はありません。架空の座標を作って事件地点として表示しないこと。地図は任意。地域の代表点を使う場合は「地域別の集計」と明記してください。\n\n発生日の不明93件、時刻の不明115件を含みます。除外した場合は、何件除外したかを説明してください。')]
    c.notebook(folder/'bicycle-theft-guide.ipynb', cells)

    quiz = [c.mdcell('# Week 08 小テスト①（成績評価対象）\n\n氏名：\n\n2026年11月19日 13:10〜13:30／個人・6問・30点満点（各5点）\n\n- 最初の10分：自分で解く（この問題文とHintのみ）。\n- 次の10分：教科書・ノート・教材・通常のWeb検索を使ってよい。\n- 20分を通して、生成AI・他者との相談・他者の解答のコピーは不可。\n- 採点：各問、指定された処理3点＋指定どおりの出力2点。未完成でも途中のコードを残してください。\n- 問題1-5は、指定された計算を順番にコードで行うこと。結果の数値だけを書いても処理の点はつきません。\n- 解けたセルを実行して出力を保存。`week08_quiz_氏名.ipynb` として13:30にUNIPAへ提出。未完成でも提出してください。\n- この小テストと、後半の自転車盗レポートは別の提出です。')]
    for ident, text in QUESTIONS:
        quiz += [c.mdcell('## 小テスト①問題'+ident+'（5点）\n\n'+text), c.codecell('')]
    quiz += [c.mdcell('## メモ（任意）\n\n途中まで考えたことや、動かなかった箇所があれば短く記す。')]
    c.notebook(folder/'quiz-01.ipynb', quiz)

    def code(key, source):
        result = c.code_html(source, results[key])
        if key in {'count','filter','rank','bars','pandas'}:
            result = '<div class="bike-code-pair">'+result+'</div>'
        return result
    def slide(key, ja, en, body, layout='plain'):
        level = 'h1' if layout=='hero' else 'h2'
        return f'<section class="slide lesson-slide layout-{layout}" data-slide data-ink-id="w8-bike-{key}" hidden><{level}>'+bi(ja,en)+f'</{level}>'+body+'</section>'
    quiz_links = links([('quiz-01.ipynb','小テスト①・問題Notebook','Quiz 01 · question notebook')],8,'lecture.html')
    guide_links = links([('bicycle-theft-guide.ipynb','CSVの読み込み〜集計・グラフ：実行例','Worked examples: CSV → counts → chart')],8,'lecture.html')
    clock = '<div class="quiz-clock" data-quiz-clock><div class="quiz-phases"><button data-phase="0" aria-pressed="true">'+bi('① 自力で10分','① Independent · 10 min')+'</button><button data-phase="1" aria-pressed="false">'+bi('② Open book 10分','② Open book · 10 min')+'</button></div><output data-clock aria-live="off">10:00</output><div><button data-clock-toggle aria-label="Start / pause">▶</button><button data-clock-reset aria-label="Reset">↶</button><span data-clock-status>'+bi('開始待ち','Ready')+'</span></div></div>'
    first_rows = '<div class="bike-table"><table><thead><tr>'+''.join('<th>'+bi(j,e)+'</th>' for j,e in [('市区町村','Municipality'),('発生時（始期）','Hour (start)'),('施錠関係','Lock status')])+'</tr></thead><tbody>'
    for row in incidents[:3]:
        first_rows += '<tr>'+''.join('<td>'+html.escape(row[k])+'</td>' for k in ['市区町村（発生地）','発生時（始期）','施錠関係'])+'</tr>'
    first_rows+='</tbody></table></div>'
    plot_code = c.code_html(PLOT, 'chart').split('<pre class="lesson-output"',1)[0]
    plot_code += '<figure class="lesson-output bike-plot-output" hidden><img class="bike-chart" src="bicycle-lock-status.png" alt="Reported thefts: unlocked 6,781; locked 3,162"></figure>'
    slides = [
        slide('quiz','まずは、小テスト。','First: a short quiz.', '<div class="quiz-score">6 '+bi('問','questions')+'<span>30 '+bi('点','points')+'</span></div>'+p('これまでの入力・文字列・リスト・計算を、自分のコードで。20分、個人で取り組みます。','Input, strings, lists and arithmetic, in your own code. Work individually for 20 minutes.')+quiz_links,'hero'),
        slide('quiz-clock','10分 ＋ 10分','10 minutes + 10 minutes', clock+p('前半は自力。後半は教科書・ノート・教材・通常のWeb検索OK。20分を通して、生成AI・他者との相談は不可。','First work independently; then use notes, textbooks, course materials and ordinary web search. No generative AI or collaboration during either phase.'),'quiz'),
        slide('quiz-save','13:30、途中でも提出。','13:30: submit what you have.', '<p class="big-filename">week08_quiz_氏名.ipynb</p>'+p('解けたセルを実行して、出力を保存。UNIPAの小テスト提出先へ。','Run the cells you have completed and save their outputs. Submit to the quiz assignment on UNIPA.')+p('各問：指定された処理3点＋指定どおりの出力2点。問1-5は計算の手順も採点します。','Each question: 3 points for the required logic and 2 for the required output. Question 1-5 must perform the specified calculation steps.'),'statement'),
        slide('brief','自転車が、なくなった。','The bike is gone.', p('あなたは千葉県警の調査担当。自転車盗データから、どんな防犯の呼びかけを提案する？','You are investigating bicycle theft in Chiba. What prevention message would you recommend from the data?')+'<div class="bike-deliverable">'+bi('件数 → 比較 → 根拠のある提案','Count → compare → recommend')+'</div>','question'),
        slide('data','9,943件の記録。','9,943 incident records.', first_rows+p(*source_note,'source-note')+p('1行が1件。市区町村、場所、年月日、時刻、年齢、職業、施錠関係があります。','One row is one record: municipality, place, date, hour, age group, occupation and lock status.')),
        slide('load','まず、CSVを読む。','First, read the CSV.', p('新しい空のNotebookを作成。CSVを同じフォルダに保存します。pandasは不要。','Create a blank notebook and save the CSV beside it. No pandas required.')+code('load',LOAD)) ,
        slide('row','リストの中に、辞書。','A list of dictionaries.', code('row',ROW)+p('<code>incidents[0]</code> は最初の1行。<code>["列名"]</code> で、その列の値を取り出します。','<code>incidents[0]</code> is the first row. <code>["column name"]</code> selects one value.')),
        slide('count','forで、1件ずつ数える。','Count one record at a time.', code('count',COUNT)+p('<code>.get(label, 0)</code>：まだないキーなら0。そこに1を足して、同じキーへ保存。','<code>.get(label, 0)</code>: start at zero for a new key, add one, then save it back.')),
        slide('filter','柏市だけなら？','What about Kashiwa?', code('filter',FILTER)+p('<code>==</code> は一致の確認。<code>.append(row)</code> は一致した1件をリストへ追加。市名を変えたら、どうなる？','<code>==</code> checks equality. <code>.append(row)</code> adds a matching record. Predict what changes with another city.')),
        slide('rank','件数の多い順に。','Rank by incident count.', code('rank',RANK)+p('<code>Counter</code> は標準ライブラリ。<code>.most_common(5)</code> は上位5組を返します。','<code>Counter</code> is in the standard library. <code>.most_common(5)</code> returns the five most frequent pairs.')),
        slide('bars','棒にすると、比べやすい。','Make the comparison visible.', code('bars',BARS)+p('棒1個 ≈ 100件。正確な数値も添える。この文字の棒グラフでもOK。','Each block represents about 100 records. Include exact counts. This text bar chart meets the visual requirement.')),
        slide('pandas','pandasが使える人は。','If pandas works for you.', code('pandas',PANDAS)+p('<code>value_counts()</code>：値ごとの件数を降順に。<code>head(5)</code>：先頭5件だけ。','<code>value_counts()</code> counts values in descending order. <code>head(5)</code> shows the first five.')+'<div class="lesson-links"><a href="https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html">'+bi('pandas公式チュートリアル','Official pandas tutorials')+' ↗</a></div>'),
        slide('chart','同じ集計を、グラフへ。','Turn the count into a chart.', '<div class="bike-chart-pair">'+plot_code+'</div>'+p('「盗難記録のうち、施錠せずが6,781件」。これだけでは施錠の効果や被害確率は分かりません。','6,781 of the reported cases were unlocked. These counts alone cannot establish theft risk or the effect of locking.','source-note')),
        slide('challenge','何を、誰に伝える？','What will you tell whom?', p('45分。空のNotebookから、自分の調査レポートを作る。地域・時間帯・年代・施錠などから、問いを一つ選ぼう。','45 minutes. Build your own report in a blank notebook. Choose a question about location, time, age group or lock status.')+'<ol class="report-steps"><li>'+bi('forで集計・絞り込み','Use a for loop to count or filter')+'</li><li>'+bi('ランキング＋グラフを一つ以上','Include a ranking and at least one chart')+'</li><li>'+bi('数値を使った発見＋防犯の提案','Explain a numerical finding and recommend an action')+'</li></ol>'+links([('challenge.html','チャレンジ・宿題の手順','Challenge and homework instructions')])+guide_links,'challenge'),
        slide('share','2分で、根拠を見せる。','Two minutes. Show your evidence.', '<div class="share-sequence">'+bi('問い → 図 → 発見 → 提案','Question → visual → finding → action')+'</div>'+p('使った列とforの役割を説明。相手の「それは何を数えたの？」に答えよう。','Explain the columns and the role of your for loop. Be ready to answer: what exactly did you count?')+p('件数 ≠ 被害率。不明な日付・時刻は不明のまま扱う。緯度・経度はないので、地図は任意。','Counts are not rates. Keep unknown dates and hours separate. Coordinates are not supplied; maps are optional.'),'statement'),
        slide('homework','同じレポートを、仕上げる。','Finish the same report.', p('11月25日（水）23:59まで。コード・出力・グラフ・Markdownの説明を保存し、実行済み.ipynbをUNIPAへ提出。','Due Wednesday, November 25 at 23:59 JST. Save code, outputs, chart and Markdown explanations; submit the executed .ipynb to UNIPA.')+p('GitHubにもNotebookとCSVを保存し、Notebookへの直接リンクを添える。提出作品はクラスギャラリーへ。','Save the notebook and CSV on GitHub too, and include the direct notebook link. Reports will appear in the class gallery.')+links([('challenge.html#homework','課題・提出方法','Assignment and submission')]),'exit')
    ]
    assert len(slides) == len(SPEC['slides'])
    head = c.page_head('Week 08 · '+SPEC['title'],'course-decks.css','course-decks.js',VERSION)
    head += '<link rel="stylesheet" href="bicycle-week.css?v='+VERSION+'"><link rel="stylesheet" href="../../assets/slide-annotations.css"><script src="../../assets/slide-annotations.js" defer></script><script src="../../assets/slide-swipe.js" defer></script><script src="bicycle-week.js?v='+VERSION+'" defer></script></head>'
    header = '<header class="lecture-header"><a id="lecture-return" href="../../agenda.html?open=08#week-08">← '+bi('授業予定','Agenda')+'</a><span class="lecture-mark">PRG / 26–2 · W08</span><button id="language-toggle" class="language-toggle" type="button">EN</button></header>'
    nav = '<nav class="slide-controls" aria-label="Slide navigation"><div class="slide-nav-group"><button id="previous-slide" type="button">← '+bi('前へ','Previous')+'</button><span id="slide-count" aria-live="polite"></span><button id="next-slide" type="button">'+bi('次へ','Next')+' →</button></div><button id="slide-fullscreen" type="button" class="slide-fullscreen" aria-pressed="false">⛶</button></nav>'
    c.write(folder/'lecture.html',head+f'<body class="lecture-page course-deck bicycle-week" data-week="8" data-release="{RELEASE}">'+header+'<main><div id="slides-view" class="view">'+nav+'<div class="slide-stage">'+''.join(slides)+'</div></div></main><script type="application/json" id="lesson-data">{}</script></body></html>')

    challenge_body = '<p class="slide-kicker">'+bi('授業内チャレンジ → 同じ作品を宿題へ','In class → finish the same report at home')+'</p><h1>'+bi('千葉の自転車盗を調査せよ','Investigate bicycle theft in Chiba')+'</h1>'
    challenge_body += p('あなたは千葉県警の調査担当。データに基づく防犯の提案を、読みやすいNotebookにまとめてください。','You are investigating bicycle theft in Chiba. Produce a readable notebook with an evidence-based prevention recommendation.')
    challenge_body += '<h2>'+bi('まず、空のNotebookを作る','Start with a blank notebook')+'</h2><ol>'+''.join('<li>'+bi(j,e)+'</li>' for j,e in [
        ('自分のリポジトリ内にweek08フォルダを作り、新しいJupyter Notebookを保存する。ファイル名は bicycle_report_氏名.ipynb。','Create a week08 folder in your repository and a new Jupyter notebook named bicycle_report_YourName.ipynb.'),
        ('bicycle-theft.csvを同じフォルダへ保存。最初のMarkdownセルにタイトル・氏名・調べたい問いを書く。','Save bicycle-theft.csv in the same folder. In the first Markdown cell, write your title, name and question.'),
        ('＋コードでPython、＋Markdownで説明を追加。以下の読み込みコードから始め、実行結果の下に自分の説明を置く。','Add Code cells for Python and Markdown cells for explanations. Begin with the loading code below; explain each result underneath.')])+'</ol>'+c.code_html(LOAD)+p('実行すると 9943。読み込めないときは、ファイル名とNotebookから見た保存場所を確認。','Expected result: 9943. If loading fails, check the filename and its location relative to your notebook.')+links([('bicycle-theft.csv','配布CSV','Class CSV'),('bicycle-theft-guide.ipynb','読み込み・集計・グラフの実行例','Worked examples: load, count and chart')],8)
    challenge_body += '<h2>'+bi('問いを選ぶ','Choose a question')+'</h2>'+c.list_html([
        ('どの市区町村で報告件数が多い？ 自分の通学エリアでは？','Which municipalities have more reported cases? What about your commuting area?'),
        ('どの時間帯・場所に多い？ どんな呼びかけが役に立ちそう？','Which hours or places have more cases? What message might help?'),
        ('年代・職業・施錠関係では、どんな違いが見える？','What differences appear by age group, occupation or lock status?')])
    challenge_body += '<h2>'+bi('レポートに必要なもの','Your report needs')+'</h2><ol>'+''.join('<li>'+bi(j,e)+'</li>' for j,e in [
        ('問い・出典・対象データの説明。1行が何を表すかを書く。','A question, source and description of the data, including what one row represents.'),
        ('forを使った集計または絞り込み。列や条件を自分で変える。whileや関数は必須ではありません。','A count or filter using a for loop. Change the columns or conditions yourself. While loops and custom functions are optional.'),
        ('上位ランキングと、グラフを一つ以上。pandasが使えなければ、文字の棒グラフでOK。正確な件数と単位を表示する。','A ranking and at least one chart. A text bar chart is fine without pandas. Include exact counts and units.'),
        ('数値を使った発見を2つ以上、それに基づく防犯の提案を一つ。結果をMarkdownで説明する。','At least two numerical findings and one prevention recommendation. Explain them in Markdown.'),
        ('元の数行や集計の合計を照合し、確認したことと限界を短く書く。自分のforが何をしているか説明できるように。','Check a few original rows or the sum of your counts. Note the check and a limitation. Be able to explain your for loop.')])+'</ol>'
    challenge_body += '<h2>'+bi('授業中：45分 → 2分で共有','In class: 45 minutes → a 2-minute share')+'</h2>'+p('3〜4人で相談してよいですが、Notebookは各自で作成。まず一つの集計を動かし、次にグラフ、最後に説明と提案。共有は「問い→図→発見→提案」の順で。','You may discuss in groups of 3–4; each student creates their own notebook. Get one count working, add a chart, then explain and recommend. Share in this order: question → visual → finding → action.')+p('AIは部分的な説明・デバッグに使ってよい。ただし、自分で変更・実行・確認する。使った場合は、何を頼み、どこを自分で確かめたかを記す。','AI may help explain a concept or debug a part. Make, run and check your own changes. If used, state what you asked and what you verified yourself.')
    challenge_body += '<h2>'+bi('データを正しく読む','Read the evidence carefully')+'</h2>'+p(*source_note)+p('日付不明93件、時刻不明115件。別の年の同じ月を混ぜず、除外した行数を示す。件数だけでは、人口・駐輪台数あたりの被害率や、施錠の効果は分かりません。','There are 93 unknown dates and 115 unknown hours. Keep years separate and report exclusions. Counts alone do not measure risk per resident or parked bicycle, or the effect of locking.')+p('地図は任意。緯度・経度の列はありません。使うなら住所を確認し、地域の代表点は「地域別の集計」と明記。架空の座標を事件地点として表示しないこと。','Maps are optional; coordinates are not supplied. Verify locations first. Label representative area points as area-level summaries; do not invent incident locations.')+'<p><a href="'+POLICE+'">'+bi('出典：千葉県警察 オープンデータ','Source: Chiba Police open data')+'</a></p>'
    challenge_body += '<h2 id="homework">'+bi('宿題・提出','Homework and submission')+'</h2>'+p('授業のレポートを仕上げる。11月25日（水）23:59までに、実行結果を保存した.ipynbをUNIPAへ提出。NotebookとCSVをGitHubにも保存し、Notebookへの直接リンクを添えてください。','Finish the same report. Submit the executed .ipynb to UNIPA by Wednesday, November 25, 23:59 JST. Save the notebook and CSV on GitHub and include the direct notebook link.')+p('全セルを上から実行して、結果とグラフが残る状態で保存。評価は、動くコード・集計と図の正確さ・根拠のある説明と提案を重視します。提出作品はクラスギャラリーへ。','Run cells from the top and save outputs and charts. Assessment focuses on working code, accurate counts and visuals, and evidence-based explanations and recommendations. Reports will appear in the class gallery.')+links([('lecture.html','講義スライド','Lecture slides')])
    challenge_head = c.page_head('Week 08 · Bicycle-theft challenge','course-pages.css','course-page.js',VERSION)+'<link rel="stylesheet" href="bicycle-week.css?v='+VERSION+'"></head>'
    c.write(folder/'challenge.html', challenge_head+f'<body class="course-challenge bicycle-week" data-release="{RELEASE}">'+header+'<main id="course-page" hidden>'+challenge_body+'</main></body></html>')
    # Keep the old text brief useful without a second set of stale instructions.
    c.write(folder/'bicycle-theft-brief.md', '# Week 08 · 千葉の自転車盗を調査せよ\n\n[チャレンジ・宿題の手順](challenge.html)\n\n新しい空のNotebookを作り、配布のbicycle-theft.csvを読む。forで集計または絞り込み、ランキング、グラフ（文字の棒でも可）、数値を使った発見2つと防犯の提案1つをまとめる。\n\n2026年11月25日23:59 JSTまでに実行済み.ipynbとGitHubの直接リンクをUNIPAへ。\n\n[実行例Notebook](bicycle-theft-guide.ipynb) / [CSV](bicycle-theft.csv)\n\n'+source_note[0]+'\n\n出典：'+POLICE+'\n')

    front = '''---
week: 8
publish_at: 2026-11-19T12:00:00+09:00
preview: true
phase: INVESTIGATE
practice_mix: Quiz 100% individual · Report with explained AI support
practice_mix_ja: 小テストは個人・AI不可／レポートはAIの利用箇所を説明
notebook_title: Graded quiz · 30 points
notebook_title_ja: 小テスト①・成績評価対象
challenge_title: Bicycle-theft investigation
challenge_title_ja: 自転車盗を調査せよ
title: Bicycle theft: what does the data say?
title_ja: 自転車盗を、データで調べる
course_date: 2026-11-19
homework_due: 2026-11-25T23:59:00+09:00
course_time: 13:10–14:50
overview: A graded quiz, then an investigation of Chiba bicycle-theft data.
overview_ja: 小テストで基礎を確認し、千葉の自転車盗データを調査する。
homework_title: Finish your bicycle-theft report
homework_title_ja: 自転車盗レポートを仕上げる
---
'''
    sections = [
        ('Lecture Flow',('13:10–13:30：小テスト（自力10分＋オープンブック10分）、13:30–13:45：データの読み方・集計、13:45–14:30：調査、14:30–14:45：共有、14:45–14:50：保存。','13:10–13:30 quiz (10 minutes independent + 10 open-book); 13:30–13:45 CSV and counting; 13:45–14:30 investigate; 14:30–14:45 share; 14:45–14:50 save.')),
        ('In-Class Notebook',('成績評価対象：個人・6問・30点（各問、処理3点＋出力2点）。最初の10分は自力、次の10分は教科書・ノート・通常のWeb検索OK。生成AI・他者との相談は不可。解けたセルの出力を保存し、13:30にUNIPAへ提出。未完成でも提出する。','Graded individual quiz: 6 questions, 30 points (3 for logic + 2 for output per question). Work independently for 10 minutes, then use textbooks, notes and ordinary web search for 10 minutes. No generative AI or collaboration. Save completed outputs and submit to UNIPA at 13:30, even if unfinished.')),
        ('In-Class Challenge',('千葉の自転車盗データから、根拠のある防犯の提案を作る。空のNotebookに、forでの集計・ランキング・グラフ・Markdownの説明をまとめる。pandasなしでも取り組める。[手順を開く](weeks/week-08/challenge.html)。','Use Chiba bicycle-theft data to make an evidence-based prevention recommendation. Start a blank notebook with a for-loop count, ranking, chart and Markdown explanations. A no-pandas route is provided. [Open instructions](weeks/week-08/challenge.html).')),
        ('Take-Home Assignment',('授業の同じレポートを仕上げる。問い・集計・ランキング・グラフ・発見2つ・防犯の提案1つを含める。11月25日（水）23:59までに実行済み.ipynbとGitHubの直接リンクをUNIPAへ。[要件・提出方法](weeks/week-08/challenge.html#homework)。','Finish the same report: a question, count, ranking, chart, two findings and one prevention recommendation. Submit the executed .ipynb and direct GitHub link to UNIPA by November 25, 23:59 JST. [Requirements and submission](weeks/week-08/challenge.html#homework).')),
        ('Aha!',('同じforで、何千件の記録から自分の問いを調べられる。','The same for loop can investigate your question across thousands of records.')),
        ('Takeaway',('件数を数え、比較し、言えることと言えないことを分ける。','Count, compare, and distinguish what the evidence does and does not show.'))]
    text = front
    for title,(ja,en) in sections:
        text += f'## {title}\nEN: {en}\nJP: {ja}\n'
    text += '''## Resources
- [Week 08 Lecture — Bicycle-theft investigation](weeks/week-08/lecture.html) {lecture}
- [小テスト①・問題Notebook / Graded Quiz 01](weeks/week-08/quiz-01.ipynb) {notebook}
- [自転車盗チャレンジ / Bicycle-Theft Challenge](weeks/week-08/challenge.html) {challenge}
- [宿題・提出方法 / Homework and Submission](weeks/week-08/challenge.html#homework) {homework}
- [自転車盗CSV / Bicycle-Theft CSV](weeks/week-08/bicycle-theft.csv) {data}
- [集計・グラフの実行例 / Counting and Chart Examples](weeks/week-08/bicycle-theft-guide.ipynb) {support}
'''
    c.write(root/'content/weeks/08-bicycle-theft.md',text)

if __name__ == '__main__':
    import importlib.util
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('course_builder',root/'tools/build-course-flow.py')
    c = importlib.util.module_from_spec(spec);sys.modules[spec.name]=c;spec.loader.exec_module(c)
    build(root,c)
    manifest = root/'tools/course-flow-manifest.json'
    entries = json.loads(manifest.read_text())
    for entry in entries:
        if entry['week']==8:entry.update(title=SPEC['title'], slides=len(SPEC['slides']))
    c.write(manifest,json.dumps(entries,ensure_ascii=False,indent=2)+'\n')
    print('Built Week 8: 16 slides, graded quiz, challenge and verified CSV examples.')