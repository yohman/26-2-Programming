"""Week 8: original 2025 quiz and a group bicycle-theft hackathon.

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
import hashlib
from collections import Counter
import quiz_package
import bicycle_ascii as ascii_bike

VERSION = '20261119-bike-hackathon'
RELEASE = '2026-11-19T12:00:00+09:00'
POLICE = 'https://www.police.pref.chiba.jp/seisoka/safe-life_publicspace-statistics_00002.html'
SPEC = dict(title='Bike Hackathon', title_ja='自転車盗ハッカソン', date='2026-11-19', due='2026-11-25', slides=[{}]*26)

LOAD = '''
# 読み込むファイルを設定する（Notebookと同じフォルダに保存）
filename = "bike.csv"
encoding = "cp932"

# 千葉県警のCSVはShift-JIS（CP932）。追加インストールは不要
import csv
with open(filename, encoding=encoding, newline="") as file:
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

RANK_PRETTY = '''
# 数字を右寄せすると、日本語の市名の長さが違っても揃う
print(f"CHIBA / TOP {top_n}")
print("-" * 24)
for place, count in top_places:
    print(f"{count:>6,}件  {place}")'''.strip()

BARS = '''
# 棒1個を何件にするか設定する
scale = 100

# 都市名と棒を別の行に。棒はすべて同じ位置から始まる
for place, count in top_places:
    bar = "#" * (count // scale)
    print(f"{place} ({count:,}件)")
    print(bar)'''.strip()
PANDAS = '''
# pandasが使える場合の別ルート。同じCSVを読む
filename = "bike.csv"
encoding = "cp932"
import pandas as pd
df = pd.read_csv(filename, encoding=encoding)

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
# 日付はYYYY-MM-DD。先頭7文字（年・月）で数える。違う年の同じ月を混ぜない
counts_by_month = {}
unknown_dates = 0
for row in incidents:
    date = row["発生年月日（始期）"]
    if date[:4].isdigit():
        month = date[:7]
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
    metadata = json.loads((folder/'bicycle-theft-source.json').read_text())
    assert hashlib.sha256((folder/'bike.csv').read_bytes()).hexdigest() == metadata['snapshot_sha256']
    with (folder/'bike.csv').open(encoding=metadata['encoding'], newline='') as f:
        incidents = list(csv.DictReader(f))
    total = len(incidents)
    assert total == metadata['record_count']
    locks = Counter(row['施錠関係'] for row in incidents)
    unknown_dates = sum(row['発生年月日（始期）']=='不明' for row in incidents)
    unknown_hours = sum(row['発生時（始期）']=='不明' for row in incidents)
    source_csv = metadata['source_csv']
    source_note = (f'千葉県警察が2025年分として公開している自転車盗CSV・{total:,}件（2026年11月18日取得）。発生年月日（始期）は2019〜2025年と不明を含みます。', f'The Chiba Police 2025 bicycle-theft release: {total:,} records, retrieved November 18, 2026. Occurrence-start dates include 2019–2025 and unknown values.')
    source_links = '<div class="lesson-links"><a href="'+POLICE+'" target="_blank" rel="noopener">'+bi('① 千葉県警のオープンデータを開く','① Open Chiba Police open data')+' ↗</a><a href="'+source_csv+'" target="_blank" rel="noopener">'+bi('② 2025年・自転車盗 CSV','② 2025 bicycle-theft CSV')+' ↗</a></div>'
    scope = {}
    results = {}
    cells = [c.mdcell('# 千葉の自転車盗：実行例\n\nこれは解説用の実行例です。新しい3人チームで、空のNotebookから一つの作品を作成してください。最初のMarkdownセルに作品タイトルと全員の氏名を記入。完成版は全員が同じものをUNIPAへ提出します。\n\n'+source_note[0]+'\n\n出典：'+POLICE+'\n\n[公式ページを開く]('+POLICE+') → 令和7年の「自転車盗（CSV形式）」をダウンロード。\n\n## 1. 準備\nダウンロードしたファイルを `bike.csv` に名前変更し、Notebookと同じフォルダに保存。文字コードはCP932です。標準ライブラリのルートは追加インストール不要。')]
    examples = [
        ('load', '2. CSVを読む', 'csv.DictReaderは、各行を「列名: 値」の辞書にします。listで全行をまとめ、lenで件数を確認します。', LOAD),
        ('row', '3. 1件の内容を見る', 'incidentsはリスト、incidents[0]は最初の事件の辞書。列名をキーに値を取り出します。列名一覧は list(incidents[0]) で確認。', ROW),
        ('count', '4. forで数える', 'counts.get(label, 0)は、登録済みなら件数、未登録なら0。その値に1を足して保存します。事件の総数と集計の合計が一致するか確かめよう。', COUNT),
        ('filter', '5. 市区町村を絞る', '==は一致の比較。appendはリストの末尾へ1件追加。市名を変えて再実行し、件数を比較してみよう。', FILTER),
        ('rank', '6. ランキング', 'CounterはPython標準ライブラリ。未登録のキーは0から数えられます。most_common(5)は件数の多い上位5組を返します。件数は人口や駐輪台数で補正した被害率ではありません。', RANK),
        ('pretty', '6+. 結果を読みやすく', 'forで各組を取り出し、f文字列で表示を整えます。{count:>6,}は6文字幅で右寄せし、3桁ごとにカンマを付けます。日本語の市名より先に数字を置くので、列が揃います。', RANK_PRETTY),
        ('bars', '7. pandasなしで棒を描く', '文字の繰り返しで簡単な棒グラフを作れます。#一つは100件。都市名の次の行に棒を出すと、開始位置が揃います。//は整数の商、:,は3桁ごとの桁区切りです。棒は切り捨てなので、正確な数値も必ず添えます。', BARS),
        ('months', '発展：年月ごとの件数', '日付不明は別に数えます。同じ「9月」でも年が違えば別の集計。既存CSVのため、毎月・毎年が完全な期間とは限りません。', MONTHS),
        ('ascii', '遊び：文字だけで自転車', 'レポートのタイトルや区切りに使ってみよう。r付きの文字列ではバックスラッシュをそのまま書けます。自転車や背景を自分で変えてみよう。', ascii_bike.STILL),
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
        optional_count = len(examples) + 1
        outputs = execute(PANDAS, scope, optional_count)
        cell = c.codecell(PANDAS, count=optional_count); cell['outputs'] = outputs
        cells += [c.mdcell('## 任意：pandasで同じ集計\n\npandas・Matplotlibが使える人向け。使えなくても上のルートで課題を完成できます。\n\n[pandas公式ガイド](https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html)\n\nvalue_counts()は値ごとの件数を降順に並べ、head(5)は先頭5件を表示します。'), cell]
        results['pandas'] = outputs[-1]['data']['text/plain']
        outputs = execute(PANDAS_LOOP, scope, optional_count + 1)
        loop_cell = c.codecell(PANDAS_LOOP, count=optional_count + 1); loop_cell['outputs'] = outputs
        cells += [c.mdcell('## 任意：pandasとforを組み合わせる\n\npandasを使う場合も、レポートにforを含めます。citiesの市名を自分で選び直し、結果を比較しよう。内側の条件は、列の値がcityと一致する行を選びます。'), loop_cell]
        plt.close('all')
        execute(PLOT.replace('plt.show()', ''), scope, optional_count + 2)
        image = io.BytesIO(); plt.gcf().savefig(image, format='png', dpi=130)
        png = image.getvalue(); (folder/'bicycle-lock-status.png').write_bytes(png)
        plot_cell = c.codecell(PLOT, count=optional_count + 2)
        plot_cell['outputs'] = [dict(output_type='display_data', metadata={}, data={'image/png': base64.b64encode(png).decode(), 'text/plain': f'Lock status: Unlocked {locks["施錠せず"]}; Locked {locks["施錠した"]}.'})]
        cells += [c.mdcell('## 任意：Matplotlibの棒グラフ\n\n同じデータを使った実際の出力です。環境ごとの日本語フォント問題を避けるためラベルだけ英訳しています。'), plot_cell]
        plt.close('all')
    cells += [c.mdcell(f'## 問いに戻る\n\n件数の違いから何が言えますか？ 分母（駐輪台数など）がないため、盗まれる確率や施錠の効果は計算できません。\n\n緯度・経度はありません。架空の座標を作って事件地点として表示しないこと。地図は任意。地域の代表点を使う場合は「地域別の集計」と明記してください。\n\n発生日の不明{unknown_dates}件、時刻の不明{unknown_hours}件を含みます。除外した場合は、何件除外したかを説明してください。')]
    # Execute the optional animation too, keeping the final notebook frame as output.
    # Verify the authored animation, suppressing terminal clearing escape sequences.
    with contextlib.redirect_stdout(io.StringIO()):
        exec(ascii_bike.ANIMATION)
    animation_cell = c.codecell(ascii_bike.ANIMATION, count=optional_count + 3)
    animation_cell['outputs'] = [dict(output_type='stream',name='stdout',text=ascii_bike.FRAMES[-1]+'\n')]
    cells += [c.mdcell('## 任意：タイヤを回す\n\n上の自転車をforで動かしてみよう。4種類のスポークを4周、0.15秒ずつ表示します。clear_outputは前の出力を消し、time.sleepは少し待ちます。Jupyter / VS CodeのNotebookで実行。turns・pause・wheelsを変えてみよう。保存時は最後のコマだけ残します。'), animation_cell]
    c.notebook(folder/'bicycle-theft-guide.ipynb', cells)

    quiz_package.build(root,c)

    def code(key, source):
        result = c.code_html(source, results[key])
        if key in {'count','filter','rank','bars','pandas'}:
            result = '<div class="bike-code-pair">'+result+'</div>'
        return result
    def slide(key, ja, en, body, layout='plain'):
        level = 'h1' if layout=='hero' else 'h2'
        return f'<section class="slide lesson-slide layout-{layout}" data-slide data-ink-id="w8-bike-{key}" hidden><{level}>'+bi(ja,en)+f'</{level}>'+body+'</section>'
    quiz_links = links([('quiz.html','パスワードを入力してNotebookを入手','Enter the password to get the notebook')])
    clock = '<div class="quiz-clock" data-quiz-clock><div class="quiz-phases"><button data-phase="0" aria-pressed="true">'+bi('① 自力で6分','① Independent · 6 min')+'</button><button data-phase="1" aria-pressed="false">'+bi('② Open book 6分','② Open book · 6 min')+'</button></div><output data-clock aria-live="off">06:00</output><div><button data-clock-toggle aria-label="Start / pause">▶</button><button data-clock-reset aria-label="Reset">↶</button><span data-clock-status>'+bi('開始待ち','Ready')+'</span></div></div>'
    build_clock = '<div class="quiz-clock bike-build-clock" data-bike-clock data-seconds="2100"><output data-clock aria-live="off">35:00</output><div><button data-clock-toggle aria-label="Start timer">▶</button><button data-clock-reset aria-label="Reset timer">↶</button><span data-clock-status>'+bi('開始待ち','Ready')+'</span></div></div>'
    first_rows = '<div class="bike-table"><table><thead><tr>'+''.join('<th>'+bi(j,e)+'</th>' for j,e in [('市区町村','Municipality'),('発生時（始期）','Hour (start)'),('施錠関係','Lock status')])+'</tr></thead><tbody>'
    for row in incidents[:3]:
        first_rows += '<tr>'+''.join('<td>'+html.escape(row[k])+'</td>' for k in ['市区町村（発生地）','発生時（始期）','施錠関係'])+'</tr>'
    first_rows+='</tbody></table></div>'
    plot_code = c.code_html(PLOT, 'chart').split('<pre class="lesson-output"',1)[0]
    plot_code += '<figure class="lesson-output bike-plot-output" hidden><img class="bike-chart" src="bicycle-lock-status.png" alt="Reported thefts by lock status in the 2025 Chiba Police CSV"></figure>'
    # One reveal shows the next small formatting step and its real CSV result.
    rank_html = c.code_html(RANK, results['rank']).split('<pre class="lesson-output"',1)[0]
    rank_html += '<div class="rank-readout" hidden>'+p('続けて、表示を整える。','Then format the display.')+'<pre data-language="python"><code>'+html.escape(RANK_PRETTY)+'</code></pre><pre class="rank-result">'+html.escape(results['pretty'])+'</pre></div>'
    rank_html = '<div class="bike-code-pair bike-rank-pair">'+rank_html+'</div>'
    slides = [
        slide('quiz','では、小テスト。','Now: a short quiz.', '<div class="quiz-score">6 '+bi('問','questions')+'<span>30 '+bi('点','points')+'</span></div>'+p('これまでの入力・文字列・リスト・計算を、自分のコードで。12分、個人で取り組みます。','Input, strings, lists and arithmetic, in your own code. Work individually for 12 minutes.')+p('パスワードで開く → ダウンロード → VS Codeで準備。合図で開始。','Unlock → download → open in VS Code. Start on the instructor’s signal.')+quiz_links,'hero'),
        slide('quiz-clock','6分 ＋ 6分','6 minutes + 6 minutes', '<div class="ascii-clock-row">'+clock+ascii_bike.art('spin')+'</div>'+p('前半は自力。後半は教科書・ノート・教材・通常のWeb検索OK。12分を通して、生成AI・他者との相談は不可。','First work independently; then use notes, textbooks, course materials and ordinary web search. No generative AI or collaboration during either phase.'),'quiz'),
        slide('quiz-save','12分後、途中でも提出。','After 12 minutes: submit what you have.', '<p class="big-filename">week08_quiz_氏名.ipynb</p>'+p('解けたセルを実行して、出力を保存。UNIPAの小テスト提出先へ。','Run the cells you have completed and save their outputs. Submit to the quiz assignment on UNIPA.')+p('各問：指定された処理3点＋指定どおりの出力2点。問1-5は計算の手順も採点します。','Each question: 3 points for the required logic and 2 for the required output. Question 1-5 must perform the specified calculation steps.'),'statement'),
        slide('brief','自転車が、なくなった。','The bike is gone.', p('あなたは千葉県警の調査担当。自転車盗データから、どんな防犯の呼びかけを提案する？','You are investigating bicycle theft in Chiba. What prevention message would you recommend from the data?')+'<div class="bike-deliverable">'+bi('件数 → 比較 → 根拠のある提案','Count → compare → recommend')+'</div>','question'),
        slide('data',f'{total:,}件の記録。',f'{total:,} incident records.', first_rows+p(*source_note,'source-note')+p('1行が1件。市区町村、場所、年月日、時刻、年齢、職業、施錠関係があります。','One row is one record: municipality, place, date, hour, age group, occupation and lock status.')),
        slide('load','まず、CSVを読む。','First, read the CSV.', p('空のNotebookを作り、公式CSVをbike.csvに名前変更して同じフォルダへ。pandasは不要。','Create a blank notebook. Rename the official CSV to bike.csv and save it beside the notebook. No pandas required.')+code('load',LOAD)) ,
        slide('row','リストの中に、辞書。','A list of dictionaries.', code('row',ROW)+p('<code>incidents[0]</code> は最初の1行。<code>["列名"]</code> で、その列の値を取り出します。','<code>incidents[0]</code> is the first row. <code>["column name"]</code> selects one value.')),
        slide('count','forで、1件ずつ数える。','Count one record at a time.', code('count',COUNT)+p('<code>.get(label, 0)</code>：まだないキーなら0。そこに1を足して、同じキーへ保存。','<code>.get(label, 0)</code>: start at zero for a new key, add one, then save it back.')),
        slide('filter','柏市だけなら？','What about Kashiwa?', code('filter',FILTER)+p('<code>==</code> は一致の確認。<code>.append(row)</code> は一致した1件をリストへ追加。市名を変えたら、どうなる？','<code>==</code> checks equality. <code>.append(row)</code> adds a matching record. Predict what changes with another city.')),
        slide('rank','件数の多い順に。','Rank by incident count.', rank_html+p('<code>Counter</code> は標準ライブラリ。<code>.most_common(5)</code> は上位5組を返します。<code>{count:>6,}</code>：6文字幅・右寄せ・桁区切り。','<code>Counter</code> is in the standard library. <code>.most_common(5)</code> returns the five most frequent pairs. <code>{count:>6,}</code>: width 6, right aligned, comma separators.')),
        slide('bars','棒にすると、比べやすい。','Make the comparison visible.', code('bars',BARS)+p('<code>#</code>一つ＝100件（端数は切り捨て）。<code>print(bar)</code>で改行し、左端を揃える。正確な数値も添える。','Each <code>#</code> represents 100 records, rounded down. <code>print(bar)</code> puts every bar at the left edge on a new line. Include exact counts.')),
        slide('pandas','pandasが使える人は。','If pandas works for you.', code('pandas',PANDAS)+p('<code>value_counts()</code>：値ごとの件数を降順に。<code>head(5)</code>：先頭5件だけ。','<code>value_counts()</code> counts values in descending order. <code>head(5)</code> shows the first five.')+'<div class="lesson-links"><a href="https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html">'+bi('pandas公式チュートリアル','Official pandas tutorials')+' ↗</a></div>'),
        slide('chart','同じ集計を、グラフへ。','Turn the count into a chart.', '<div class="bike-chart-pair">'+plot_code+'</div>'+p(f'「盗難記録のうち、施錠せずが{locks["施錠せず"]:,}件」。これだけでは施錠の効果や被害確率は分かりません。',f'{locks["施錠せず"]:,} of the reported cases were unlocked. These counts alone cannot establish theft risk or the effect of locking.','source-note')),
        slide('deliverable','1チーム、1つのNotebook','One team, one notebook', '<p class="big-filename">bike.ipynb</p>'+c.list_html([
            ('問い・出典・3人全員の氏名。説明はMarkdownで。','A question, source and all three names. Explain the work in Markdown.'),
            ('forの集計・絞り込み ＋ ランキング ＋ グラフ。文字の棒でもOK。','A for-loop count or filter, a ranking and a chart. Text bars are fine.'),
            ('数値を使った発見2つ ＋ 防犯の提案1つ。','Two numerical findings and one prevention recommendation.')])+p('例の列・条件を自分たちで変更し、元データや合計と照合する。','Change the example’s column or condition, then check it against source rows or totals.')),
        slide('teamwork','新しい3人で、どう進める？','How will your new team work?', '<dl class="bike-team-roles"><div><dt>'+bi('調べる','Investigate')+'</dt><dd>'+bi('問い・使う列・条件を決める','Choose the question, columns and conditions')+'</dd></div><div><dt>'+bi('つくる','Build')+'</dt><dd>'+bi('集計を動かし、図を見せる','Run the count and make the visual')+'</dd></div><div><dt>'+bi('確かめる','Check')+'</dt><dd>'+bi('数値を照合し、説明と提案を整える','Verify the numbers and refine the explanation')+'</dd></div></dl>'+p('役割は目安。全員で画面を見て、各自がコードを変更・実行し、担当をMarkdownに残そう。','Roles are a starting point. Review the screen together; everyone changes and runs code, then notes their contribution in Markdown.')+p('AIは説明・部分的なデバッグに。全員が、自分たちのforと図を説明できること。','Use AI for explanations or a specific bug. Everyone must be able to explain the team’s for loop and visual.','source-note')),
        slide('challenge','制作スタート','Build time', '<div class="bike-build-row">'+build_clock+ascii_bike.art('spin')+'</div>'+p('最初の5分で問いと担当を決める → 25分で集計と図 → 最後の5分で確認・保存。','First 5 minutes: choose a question and roles → 25 minutes: count and visual → final 5: check and save.')+links([('challenge.html','ハッカソンの手順','Hackathon instructions'),('challenge.html#ascii','ASCIIで遊ぶ','ASCII fun')]),'challenge'),
        slide('share','1チーム、1分で実演','One minute per team', '<div class="share-sequence">'+bi('問い → 図 → 発見 → 提案','Question → visual → finding → action')+'</div>'+p('全チームがNotebookを画面で見せる。全員が一言話し、一人は使った列とforの役割を説明する。','Every team shows its notebook on screen. Everyone speaks briefly; one member explains the columns and the for loop.')+p('件数 ≠ 被害率。確認したことと、データからは言えないことも一言。','Counts are not rates. Briefly mention one check and what the data cannot tell you.'),'statement'),
        slide('homework','チームの作品を、仕上げる','Finish your team’s report', ascii_bike.art('finish')+p('11月25日（水）23:59まで。全員の氏名と担当を記入し、コード・出力・図・Markdownを保存。','Due Wednesday, November 25 at 23:59 JST. Include all names and contributions; save code, outputs, visuals and Markdown.')+p('代表者だけでなく、3人全員が同じ完成版bike.ipynbをUNIPAへ提出。GitHubにもNotebookとCSVを保存し、Notebookへの直接リンクを添える。','All three members submit the same completed bike.ipynb to UNIPA, not just the representative. Save the notebook and CSV on GitHub and include the direct notebook link.')+p('クラスギャラリーでは、メンバー名付きのグループ作品として紹介します。','The class gallery will show each team’s project with its member names.')+links([('challenge.html#homework','課題・提出方法','Assignment and submission')]),'exit')
    ]
    review = slide('review','先週の天気アプリ。','Last week’s weather apps.', '<div class="ascii-review-row"><div class="large-stamp">20 MIN</div>'+ascii_bike.weather_art()+'</div>'+p('使う人に、何ができるアプリ？ 実際に動かしながら、作品をクラスで振り返ります。','Who is the app for, and what can it do? Run the work and review it together.')+'<div class="review-prompts">'+bi('目的 → 天気の見せ方 → forの役割 → 改善','Purpose → weather display → role of for → improvements')+'</div>'+links([('../../gallery.html?week=7','みんなの作品：天気ハッカソン','Class gallery: weather hackathon'),('../week-07/challenge.html','先週の天気ハッカソンの要件','Last week’s weather hackathon requirements')]),'hero')
    moments = [
        ('Tsukada先生の自転車が盗まれた。','Tsukada sensei’s bike was stolen.','2024-10-23 · 08:10:06 · さつき駐輪場','2024-10-23 · 08:10:06 · Satsuki bicycle parking'),
        ('17:25:04','17:25:04','2024-10-23 · さつき駐輪場','2024-10-23 · Satsuki bicycle parking'),
        ('17:25:15','17:25:15','2024-10-23 · さつき駐輪場','2024-10-23 · Satsuki bicycle parking'),
        ('17:25:33','17:25:33','2024-10-23 · 別のカメラへ','2024-10-23 · A different camera'),
        ('17:25:35','17:25:35','2024-10-23 · 駐輪場の外側','2024-10-23 · Outside the bicycle parking area'),
        ('同じ資料の、拡大画像。','An enlarged still from the same document.','ここから記録できる項目は？ 場所・日付・時刻…','What could become data? Location, date, time…')]
    # Display only the camera picture, excluding the document frame and black bands.
    # The original JPEGs remain unchanged; SVG view boxes perform the display crop.
    frames = [
        (781,527,(13,89,753,423),'xMinYMid'),
        (761,510,(3,84,754,423),'xMidYMid'),
        (764,582,(9,90,752,423),'xMinYMid'),
        (770,561,(10,89,750,423),'xMidYMid'),
        (772,556,(18,90,751,423),'xMidYMid'),
        (1189,928,(0,120,1189,740),'xMidYMid')]
    camera_slides = []
    for index,((ja,en,caption,caption_en),(width,height,crop,alignment)) in enumerate(zip(moments,frames),1):
        image = f'security/camera-{index:02}.jpg'
        assert (folder/image).exists()
        label = bi('Tsukada先生の自転車 · 2024/10/23 08:10:06','Tsukada’s bike · 2024/10/23 08:10:06') if index==1 else bi('同資料の拡大画像','Enlarged still') if index==6 else html.escape(ja)
        view_box = ' '.join(map(str,crop))
        picture = f'<svg class="camera-image" viewBox="{view_box}" preserveAspectRatio="{alignment} slice" role="img" aria-labelledby="camera-title-{index:02}"><title id="camera-title-{index:02}">'+html.escape(en)+f'</title><image href="{image}" width="{width}" height="{height}"/></svg>'
        camera_slides.append(slide(f'cctv-{index:02}',ja,en,'<figure class="camera-frame">'+picture+'<figcaption>'+label+'</figcaption></figure>','camera'))
    police_source = slide('police-source','まずは、千葉県警のデータへ。','Start with Chiba Police open data.', p('2024年の学内事例から、県全体へ。公式サイトの「令和7年中の発生情報」→「自転車盗（CSV形式）」を開こう。','From the 2024 campus case to the whole prefecture. On the official site, choose the 2025 section and its bicycle-theft CSV.')+source_links+ascii_bike.art('data')+p('ダウンロード後、bike.csvに名前変更。文字コードはCP932。問いを選び、件数・ランキング・グラフから防犯の提案を作ります。','Rename the download to bike.csv. Its encoding is CP932. Choose a question and use counts, rankings and a chart to recommend a prevention action.')+p(*source_note,'source-note'),'question')
    hackathon = slide('hackathon','自転車盗ハッカソン','Bike Hackathon', '<p class="large-stamp">NEW TEAMS / 3 PEOPLE</p>'+p('先週とは違うメンバーで、新しい3人チームを作ります。','Form a new three-person team with different classmates from last week.')+p('千葉の自転車盗データから、誰に、どんな防犯の呼びかけをする？ 1チームで一つのNotebookを作ろう。','What prevention message could Chiba’s bicycle-theft data support, and who is it for? Build one notebook together.')+ascii_bike.art('ride'),'hero')
    # Review → individual quiz → camera sequence → new teams → data → group hackathon.
    slides = [review] + slides[:3] + camera_slides + [hackathon, police_source] + slides[4:]
    assert len(slides) == len(SPEC['slides'])
    head = c.page_head('Week 08 · '+SPEC['title'],'course-decks.css','course-decks.js',VERSION)
    head += '<link rel="stylesheet" href="bicycle-week.css?v='+VERSION+'"><link rel="stylesheet" href="../../assets/slide-annotations.css"><script src="../../assets/slide-annotations.js" defer></script><script src="../../assets/slide-swipe.js" defer></script><script src="bicycle-week.js?v='+VERSION+'" defer></script><script src="ascii-bikes.js?v='+VERSION+'" defer></script></head>'
    header = '<header class="lecture-header"><a id="lecture-return" href="../../agenda.html?open=08#week-08">← '+bi('授業予定','Agenda')+'</a><span class="lecture-mark">PRG / 26–2 · W08</span><button id="language-toggle" class="language-toggle" type="button">EN</button></header>'
    nav = '<nav class="slide-controls" aria-label="Slide navigation"><div class="slide-nav-group"><button id="previous-slide" type="button">← '+bi('前へ','Previous')+'</button><span id="slide-count" aria-live="polite"></span><button id="next-slide" type="button">'+bi('次へ','Next')+' →</button></div><button id="slide-fullscreen" type="button" class="slide-fullscreen" aria-pressed="false">⛶</button></nav>'
    c.write(folder/'lecture.html',head+f'<body class="lecture-page course-deck bicycle-week" data-week="8" data-release="{RELEASE}">'+header+'<main><div id="slides-view" class="view">'+nav+'<div class="slide-stage">'+''.join(slides)+'</div></div></main><script type="application/json" id="lesson-data">{}</script></body></html>')

    quiz_head = c.page_head('Week 08 · 小テスト①','course-pages.css','course-page.js',VERSION)
    quiz_head += '<link rel="stylesheet" href="bicycle-week.css?v='+VERSION+'"><script src="../../assets/site.js?v='+VERSION+'" defer></script><script src="quiz.js?v='+VERSION+'" defer></script></head>'
    quiz_body = '<h1>'+bi('小テスト①','Quiz 01')+'</h1>'+p('授業中に案内するパスワードを入力してください。開いたらNotebookをダウンロードし、VS Codeで開いて合図を待ちます。','Enter the password announced in class. Then download the notebook, open it in VS Code and wait for the instructor’s signal.')
    quiz_body += '<div class="quiz-entry" data-quiz-lock><form><label for="quiz-password">'+bi('パスワード','Password')+'</label><div><input id="quiz-password" type="password" autocomplete="off" autocapitalize="none" spellcheck="false" required><button type="submit">'+bi('開く','Open')+' →</button></div></form><p role="status" data-quiz-status></p><section data-quiz-unlocked hidden><h2>'+bi('ダウンロードして、準備する','Download and get ready')+'</h2><a class="quiz-download" data-quiz-download>'+bi('小テストNotebookをダウンロード','Download quiz notebook')+' ↓</a>'+p('ダウンロードした.ipynbをVS Codeで開き、氏名を記入。準備ができたら合図を待つ。小テストは自力6分＋オープンブック6分です。','Open the downloaded .ipynb in VS Code and add your name. Wait for the start signal. The quiz is 6 minutes independent + 6 minutes open-book.')+'<details><summary>'+bi('問題をプレビュー','Preview the questions')+'</summary><div data-quiz-preview></div></details></section></div>'
    c.write(folder/'quiz.html',quiz_head+f'<body class="course-challenge bicycle-week quiz-page" data-release="{RELEASE}">'+header+'<main id="course-page" hidden>'+quiz_body+'</main></body></html>')

    challenge_body = '<p class="slide-kicker">'+bi('新しい3人チームで制作 → 同じ作品を宿題へ','New three-person teams → finish the same project at home')+'</p><h1>'+bi('自転車盗ハッカソン','Bike Hackathon')+'</h1>'+ascii_bike.art('ride')
    challenge_body += p('先週とは違うメンバーで、新しい3人チームを作ります。千葉の自転車盗データを調べ、根拠のある防犯の提案を一つのNotebookにまとめよう。','Form a new three-person team with different classmates from last week. Investigate Chiba bicycle-theft data and build one notebook with an evidence-based prevention recommendation.')
    challenge_body += '<h2>'+bi('1. 千葉県警のオープンデータを開く','1. Open Chiba Police open data')+'</h2>'+source_links+p('「令和7年中の発生情報」から「自転車盗（CSV形式）」をダウンロード。ファイル名をbike.csvに変更します。','In the 2025 section, download the bicycle-theft CSV and rename it to bike.csv.')+p(*source_note)+p('同じ内容の授業用コピーも下にあります。文字コードは公式ファイルと同じCP932です。','The class copy below contains the same data and retains the official CP932 encoding.')
    challenge_body += '<h2>'+bi('2. 空のNotebookを作る','2. Create a blank notebook')+'</h2><ol>'+''.join('<li>'+bi(j,e)+'</li>' for j,e in [
        ('チームでweek08フォルダを用意し、空のJupyter Notebookを一つ作る。ファイル名は bike.ipynb。','Prepare a week08 folder and create one blank Jupyter notebook for the team, named bike.ipynb.'),
        ('bike.csvを同じフォルダへ保存。最初のMarkdownセルに作品タイトル・3人全員の氏名・調べたい問いを書く。','Save bike.csv in the same folder. In the first Markdown cell, write the project title, all three members’ names and your question.'),
        ('＋コードでPython、＋Markdownで説明を追加。以下の読み込みコードから始め、実行結果の下にチームの説明を置く。','Add Code cells for Python and Markdown cells for explanations. Begin with the loading code below; explain each result together underneath.')])+'</ol>'+c.code_html(LOAD)+p(f'実行すると {total}。読み込めないときは、ファイル名とNotebookから見た保存場所を確認。',f'Expected result: {total}. If loading fails, check the filename and its location relative to your notebook.')+links([('bike.csv','配布CSV','Class CSV'),('bicycle-theft-guide.ipynb','読み込み・集計・グラフの実行例','Worked examples: load, count and chart')],8)
    challenge_body += '<h2>'+bi('問いを選ぶ','Choose a question')+'</h2>'+c.list_html([
        ('どの市区町村で報告件数が多い？ 自分の通学エリアでは？','Which municipalities have more reported cases? What about your commuting area?'),
        ('どの時間帯・場所に多い？ どんな呼びかけが役に立ちそう？','Which hours or places have more cases? What message might help?'),
        ('年代・職業・施錠関係では、どんな違いが見える？','What differences appear by age group, occupation or lock status?')])
    challenge_body += '<h2>'+bi('レポートに必要なもの','Your report needs')+'</h2><ol>'+''.join('<li>'+bi(j,e)+'</li>' for j,e in [
        ('問い・出典・対象データの説明。1行が何を表すかを書く。','A question, source and description of the data, including what one row represents.'),
        ('forを使った集計または絞り込み。列や条件を自分で変える。whileや関数は必須ではありません。','A count or filter using a for loop. Change the columns or conditions yourself. While loops and custom functions are optional.'),
        ('上位ランキングと、グラフを一つ以上。pandasが使えなければ、文字の棒グラフでOK。正確な件数と単位を表示する。','A ranking and at least one chart. A text bar chart is fine without pandas. Include exact counts and units.'),
        ('数値を使った発見を2つ以上、それに基づく防犯の提案を一つ。結果をMarkdownで説明する。','At least two numerical findings and one prevention recommendation. Explain them in Markdown.'),
        ('元の数行や集計の合計を照合し、確認したことと限界を短く書く。全員がforの役割を説明できるように。','Check a few original rows or the sum of your counts. Note the check and a limitation. Everyone must be able to explain the for loop.')])+'</ol>'
    challenge_body += '<h2>'+bi('3人で進めるために','Working as a team')+'</h2>'+c.list_html([
        ('調査：問い・使う列・条件を提案する。制作：集計と図を作る。確認：数値の照合とMarkdownの説明を整える。まずは担当を相談しよう。','Discuss initial roles: investigate the question and columns, build the count and visual, and check the numbers and Markdown.'),
        ('役割は固定しなくてOK。全員で結果を見て、各自がコードの一部を変更・実行する。担当したことを氏名付きで短く記録する。','Roles can change. Look at the results together; each member changes and runs part of the code and briefly records their contribution by name.'),
        ('作業用のNotebookを一つ決め、最後に全員へ同じ完成版を共有する。全員がforと図を説明できるようにしよう。','Choose one working notebook and share the same final version with everyone. Make sure every member can explain the for loop and visual.')])
    challenge_body += '<h2>'+bi('授業中：制作35分 → 全チーム発表15分','In class: 35-minute build → 15-minute demos')+'</h2>'+p('14:00–14:35：最初の5分で問いと担当を決め、25分で集計と図、最後の5分で確認・保存。14:35–14:50：1チーム約1分で、Notebookを画面で実演します。','14:00–14:35: use 5 minutes for the question and roles, 25 for the count and visual, and 5 to check and save. From 14:35–14:50, every team gives an approximately one-minute notebook demo.')+p('発表は「問い → 図 → 発見 → 提案」。全員が一言話し、一人は使った列とforの役割を説明する。','Present in this order: question → visual → finding → action. Everyone speaks briefly; one member explains the columns and for loop.')+p('AIは説明・部分的なデバッグに使ってよい。ただし、完成品を丸ごと任せず、自分たちでコードを変更・実行・確認する。利用箇所と確かめたことをMarkdownに記録する。','AI may explain a concept or help debug a specific part. Do not delegate the whole project: change, run and check the code yourselves. Record where AI helped and what you verified in Markdown.')

    challenge_body += '<section class="ascii-playground" id="ascii"><h2>'+bi('文字だけで、遊んでみよう。','Play with letters, lines and wheels.')+'</h2>'+ascii_bike.art('ride')+p('レポートの見せ方は自由。ASCIIの自転車をタイトルに置いたり、タイヤを回したり。中心はデータの発見と防犯の提案です。','Make the report your own: add an ASCII bicycle to its title or spin the wheels. Build around your data findings and prevention recommendation.')+c.code_html(ascii_bike.STILL)+'<pre class="ascii-result">'+html.escape(results['ascii'])+'</pre>'+'<details><summary>'+bi('任意：forでタイヤを回す','Optional: spin the wheels with for')+'</summary>'+p('Notebook用。4種類のスポークを4周、0.15秒ずつ表示。clear_outputは前の出力を消す、time.sleepは少し待つ。数字や文字を変えてみよう。','For notebooks: show four spoke positions four times, 0.15 seconds each. clear_output replaces the previous frame; time.sleep pauses briefly. Try changing the numbers and characters.')+c.code_html(ascii_bike.ANIMATION)+'</details></section>'
    challenge_body += '<h2>'+bi('データを正しく読む' ,'Read the evidence carefully')+'</h2>'+p(*source_note)+p(f'日付不明{unknown_dates}件、時刻不明{unknown_hours}件。別の年の同じ月を混ぜず、除外した行数を示す。件数だけでは、人口・駐輪台数あたりの被害率や、施錠の効果は分かりません。',f'There are {unknown_dates} unknown dates and {unknown_hours} unknown hours. Keep years separate and report exclusions. Counts alone do not measure risk per resident or parked bicycle, or the effect of locking.')+p('地図は任意。緯度・経度の列はありません。使うなら住所を確認し、地域の代表点は「地域別の集計」と明記。架空の座標を事件地点として表示しないこと。','Maps are optional; coordinates are not supplied. Verify locations first. Label representative area points as area-level summaries; do not invent incident locations.')+'<p><a href="'+POLICE+'">'+bi('出典：千葉県警察 オープンデータ','Source: Chiba Police open data')+'</a></p>'
    challenge_body += '<h2 id="homework">'+bi('宿題・提出','Homework and submission')+'</h2>'+p('チームで授業のレポートを仕上げる。最初のMarkdownセルに作品タイトルと3人全員の氏名を記入し、各自の担当も短く書く。','Finish the same team report. Put the project title and all three members’ names in the first Markdown cell, and briefly describe each person’s contribution.')+p('11月25日（水）23:59までに、3人全員が同じ完成版bike.ipynbをそれぞれUNIPAへ提出。代表者だけの提出ではありません。','By Wednesday, November 25, 23:59 JST, every member submits the same completed bike.ipynb separately to UNIPA, not just the representative.')+p('Notebookとbike.csvを各自のGitHubにも保存し、Notebookへの直接リンクを添える。小テストは個人の別提出です。','Save the notebook and bike.csv on each member’s GitHub and include the direct notebook link. The individual quiz is a separate submission.')+p('全セルを上から実行して、結果とグラフが残る状態で保存。評価は、動くコード・集計と図の正確さ・根拠のある説明と提案を重視します。提出作品はメンバー名付きでクラスギャラリーへ。','Run cells from the top and save outputs and charts. Assessment focuses on working code, accurate counts and visuals, and evidence-based explanations and recommendations. Reports will appear in the class gallery as grouped projects with member names.')+links([('lecture.html','講義スライド','Lecture slides')])
    challenge_head = c.page_head('Week 08 · Bike Hackathon','course-pages.css','course-page.js',VERSION)+'<link rel="stylesheet" href="bicycle-week.css?v='+VERSION+'"><script src="ascii-bikes.js?v='+VERSION+'" defer></script></head>'
    c.write(folder/'challenge.html', challenge_head+f'<body class="course-challenge bicycle-week" data-release="{RELEASE}">'+header+'<main id="course-page" hidden>'+challenge_body+'</main></body></html>')
    # Keep the old text brief useful without a second set of stale instructions.
    c.write(folder/'bicycle-theft-brief.md', '# Week 08 · 自転車盗ハッカソン\n\n[チャレンジ・宿題の手順](challenge.html)\n\n先週とは違うメンバーで新しい3人チームを作る。チームで一つの空のNotebook（bike.ipynb）を作り、配布のbike.csvを読む。作品タイトル・全員の氏名・各自の担当を記す。forで集計または絞り込み、ランキング、グラフ（文字の棒でも可）、数値を使った発見2つと防犯の提案1つをまとめる。\n\n制作35分、最後に全チーム約1分で実演。2026年11月25日23:59 JSTまでに、全員が同じ実行済みbike.ipynbとGitHubの直接リンクをそれぞれUNIPAへ。\n\n任意：ASCII自転車や文字の棒グラフで、レポートの見せ方も工夫しよう。タイヤを回すforの例は[課題ページ](challenge.html#ascii)へ。\n\n[実行例Notebook](bicycle-theft-guide.ipynb) / [CSV](bike.csv)\n\n'+source_note[0]+'\n\n出典：'+POLICE+'\n')

    front = '''---
week: 8
publish_at: 2026-11-19T12:00:00+09:00
preview: true
phase: HACKATHON
practice_mix: Individual quiz · New teams of 3 · Explain AI use
practice_mix_ja: 小テストは個人・AI不可／新しい3人チームで制作・AIの利用箇所を説明
notebook_title: Graded quiz · 30 points
notebook_title_ja: 小テスト①・成績評価対象
challenge_title: Bike Hackathon
challenge_title_ja: 自転車盗ハッカソン
title: Bike Hackathon
title_ja: 自転車盗ハッカソン
course_date: 2026-11-19
homework_due: 2026-11-25T23:59:00+09:00
course_time: 13:10–14:50
overview: Review weather apps, take an individual quiz, then investigate bicycle theft in new teams of three.
overview_ja: 先週の天気アプリを振り返り、個人の小テスト後、新しい3人チームで自転車盗ハッカソン。
homework_title: Finish your team’s bike report
homework_title_ja: チームの自転車盗レポートを仕上げる
---
'''
    sections = [
        ('Student Work',('[みんなの作品：Week 7 天気ハッカソン](gallery.html?week=7) — Notebookと実行結果をプレビュー。グループのメンバーと提出Notebookを確認でき、Colabでも開けます。','[Student work: Week 7 weather hackathon](gallery.html?week=7) — Preview notebooks and saved outputs. Projects are grouped by authors, with member names and submitted notebook versions; open notebooks in Colab too.')),
        ('Lecture Flow',('13:10–13:30：先週の天気アプリをレビュー（約20分）、13:30–13:45：パスワードで問題を入手・準備→小テスト6分＋6分、13:45–14:00：学内の防犯カメラ事例→千葉県警データのミニ講義、14:00–14:35：新しい3人チームで制作、14:35–14:50：全チーム約1分で発表・保存。','13:10–13:30 review last week’s weather apps (~20 min); 13:30–13:45 unlock/download and prepare → quiz (6 + 6 min); 13:45–14:00 campus camera case → Chiba Police data mini-lecture; 14:00–14:35 hackathon in new three-person teams; 14:35–14:50 one-minute demos from every team and save.')),
        ('In-Class Notebook',('成績評価対象：個人・6問・30点（各問、処理3点＋出力2点）。最初の6分は自力、次の6分は教科書・ノート・通常のWeb検索OK。生成AI・他者との相談は不可。パスワードは授業中に案内。開いてダウンロードし、準備後に合図で開始。解けたセルの出力を保存し、13:45を目安にUNIPAへ提出。未完成でも提出する。','Graded individual quiz: 6 questions, 30 points (3 for logic + 2 for output per question). Work independently for 6 minutes, then use textbooks, notes and ordinary web search for 6 minutes. No generative AI or collaboration. The password is announced in class. Unlock, download, and wait for the start signal. Save completed outputs and submit to UNIPA around 13:45, even if unfinished.')),
        ('In-Class Challenge',('先週とは違うメンバーで新しい3人チームを作り、一つのNotebookを制作。まず[千葉県警のオープンデータ](https://www.police.pref.chiba.jp/seisoka/safe-life_publicspace-statistics_00002.html)から[2025年の自転車盗CSV](https://www.police.pref.chiba.jp/content/common/000074746.csv)をダウンロード。根拠のある防犯の提案を作る。空のbike.ipynbに全員の氏名を記入し、forの集計・ランキング・図・発見2つ・防犯の提案1つをまとめる。最後に全チームが実演。pandasなしでも取り組める。[手順を開く](weeks/week-08/challenge.html)。','Form a new three-person team with different classmates from last week and build one shared notebook. Start at [Chiba Police open data](https://www.police.pref.chiba.jp/seisoka/safe-life_publicspace-statistics_00002.html) and download the [2025 bicycle-theft CSV](https://www.police.pref.chiba.jp/content/common/000074746.csv). Create a blank bike.ipynb with all member names, a for-loop count, ranking, visual, two findings and one prevention recommendation. Every team demos. A no-pandas route is provided. [Open instructions](weeks/week-08/challenge.html).')),
        ('Take-Home Assignment',('チームの同じ作品を仕上げる。タイトル・3人全員の氏名・各自の担当を記入。forの集計、ランキング、図、発見2つと防犯の提案1つを含める。11月25日（水）23:59までに、全員が同じ実行済みbike.ipynbと各自のGitHub直接リンクをそれぞれUNIPAへ。メンバー名付きでクラスギャラリーに掲載。[要件・提出方法](weeks/week-08/challenge.html#homework)。','Finish the same team project. Include the title, all three names and contributions, a for-loop count, ranking, visual, two findings and one prevention recommendation. Every member submits the same executed bike.ipynb and their direct GitHub link separately to UNIPA by November 25, 23:59 JST. Projects appear in the gallery with member names. [Requirements and submission](weeks/week-08/challenge.html#homework).')),
        ('Aha!',('同じforで、何千件の記録から自分の問いを調べられる。','The same for loop can investigate your question across thousands of records.')),
        ('Takeaway',('件数を数え、比較し、言えることと言えないことを分ける。','Count, compare, and distinguish what the evidence does and does not show.'))]
    text = front
    for title,(ja,en) in sections:
        text += f'## {title}\nEN: {en}\nJP: {ja}\n'
    text += '''## Resources
- [Week 08 Lecture — Bike Hackathon](weeks/week-08/lecture.html) {lecture}
- [小テスト①・パスワードで開く / Open Graded Quiz 01](weeks/week-08/quiz.html) {notebook}
- [自転車盗ハッカソン / Bike Hackathon](weeks/week-08/challenge.html) {challenge}
- [宿題・提出方法 / Homework and Submission](weeks/week-08/challenge.html#homework) {homework}
- [自転車盗CSV / Bicycle-Theft CSV](weeks/week-08/bike.csv) {data}
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
    print('Built Week 8: 26 slides, individual quiz and new-team Bike Hackathon.')