"""Week 7 weather hackathon, using the established course presentation shell."""
from urllib.parse import urlencode
import ast
import contextlib
import hashlib
import html
import io
import json
import re
from datetime import datetime, timedelta, timezone

VERSION = '20261112-weather-guide'
LOCATION_CODE = '''import json
from urllib.request import urlopen
from urllib.parse import urlencode

city = "Kashiwa"  # Change this city name
url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode({
    "name": city, "count": 1, "language": "en"
})
with urlopen(url, timeout=10) as response:
    locations = json.load(response)
place = locations["results"][0]
place["name"], place.get("admin1"), place["country"]'''

WEATHER_CODE = '''url = "https://api.open-meteo.com/v1/forecast?" + urlencode({
    "latitude": place["latitude"], "longitude": place["longitude"],
    "daily": ("temperature_2m_max,temperature_2m_min,"
              "precipitation_probability_max,rain_sum,showers_sum"),
    "past_days": 1, "forecast_days": 3, "timezone": "auto"
})
with urlopen(url, timeout=10) as response:
    weather = json.load(response)
weather["daily"]'''

FOR_CODE = '''daily = weather["daily"]
for i in range(1, len(daily["time"])):
    print(daily["time"][i],
          daily["temperature_2m_max"][i], "°C",
          daily["precipitation_probability_max"][i], "%")'''

IDEAS = [
    ('場所を入力 → その街の天気を分かりやすく見せる。', 'Enter a city and show its weather clearly.'),
    ('「今日は雨が降りそう？」→ 今日の降水確率で答える。予報なので断定しない。', '“Will it rain today?” Use today’s rain probability; describe a chance, not a certainty.'),
    ('「昨日、雨は降った？」→ 昨日の雨量のモデル推定値で答える。観測の証明ではない。', '“Did it rain yesterday?” Use the model estimate of yesterday’s rainfall, not a confirmed observation.'),
    ('「明日、どこで雨が降りそう？」→ 選んだ複数の街をforで比較する。', '“Where might it rain tomorrow?” Use for to compare a chosen list of cities.'),
    ('気温や降水確率を、文字の棒・絵文字・表など、自分らしい表示にする。', 'Give the forecast a useful visual form: text bars, emoji, a table or a chart.'),
]
GROUP_GUIDE = [
    ('最初に、使う人と問いを全員で決める。', 'Agree on the user and the question before coding.'),
    ('コード・動作確認・表示と説明を分担し、困ったら一緒に考える。', 'Share the coding, checking and visual explanation; help each other when stuck.'),
    ('全員がコードの変更に参加し、その変更を説明できるようにする。', 'Everyone contributes a code change and understands what it does.'),
    ('小さく動かし、一つずつ変更する。発表前に全員で実行する。', 'Get a small version working, check one change at a time, then run it together.'),
]
AI_GUIDE = ('AIはエラーの説明や小さなヒントに使ってよい。作品全体を任せず、使うコードを読み、自分たちで結果を確かめる。',
            'AI can explain an error or give a small hint. Build the app yourselves, read the code you use and check its results.')
BUILD_STEPS = [
    ('スターターの2つのコードセルを順番に実行し、都市と天気を確認する。', 'Run the starter’s two code cells in order; check the city and weather.'),
    ('使う人と問いを決め、下に自分たちのCode CellとMarkdown Cellを追加する。', 'Choose a user and question, then add your own Code and Markdown cells below.'),
    ('forで複数の日・街・項目を扱い、役立つ結果と視覚表示を作る。', 'Use for across days, cities or weather items; create a useful answer and visual.'),
    ('条件や場所を2通り試し、コードと結果を説明できるようにする。', 'Test two locations or settings and be ready to explain the code and results.'),
]
DEMO_GUIDE = [
    ('誰の、何を助ける？目的を一文で。', 'State whose question your app answers.'),
    ('視覚表示を見せ、場所や条件を変えてもう一度動かす。', 'Show the visual; change a location or setting and run it again.'),
    ('forの一行と、分かったことを説明。全員が一言話す。', 'Explain a line of your for loop and one finding. Everyone speaks briefly.'),
]
SPEC = dict(
    title='Weather Hackathon', title_ja='天気ハッカソン',
    date='2026-11-12', due='2026-11-18', version=VERSION,
    aim=('APIの天気データとforを使い、人に役立つ天気アプリを作る。whileは任意。',
         'Use weather API data and for loops to build a useful weather app. while is optional.'),
    brief=('2〜3人で、人に役立つ天気アプリをNotebookで作ろう。問いを一つ選び、APIのデータをforで扱い、結果を見やすく伝える。最後は全チームが実演。',
           'In teams of 2–3, build a useful weather app in a notebook. Choose a question, use API data and a for loop, and present a clear visual answer. Every team demos.'),
    flow=('13:10 説明10分 / 13:20 準備5分 / 13:25 チーム制作60分 / 14:25 発表20分 / 14:45 保存・まとめ5分。',
          '13:10 briefing 10 min / 13:20 setup 5 min / 13:25 build 60 min / 14:25 demos 20 min / 14:45 save and wrap up 5 min.'),
    requirements=[
        ('使う人と、答えたい問いをMarkdownで書く。', 'Explain the user and the question in Markdown.'),
        ('APIの天気データを使い、自分たちのforループを入れる。whileは任意。関数の定義は不要。', 'Use API weather data and add your own for loop. while is optional; no function definitions required.'),
        ('結果が見て分かる表示を一つ。表・文字の棒・絵文字・グラフなど。Notebookの中でよい。', 'Include a readable visual: a table, text bars, emoji or a chart. It can stay inside the notebook.'),
        ('場所や条件を2通り試し、結果・単位・日付・出典を確認する。', 'Test two locations or settings; check the results, units, dates and source.'),
        ('全員が自分の変更を説明できる。コードと結果が残る実行済みNotebookにする。', 'Everyone can explain their contribution. Save an executed notebook with code and outputs.'),
    ],
    homework=('実演の意見を使い、同じアプリを一つ改善する。各自の実行済み.ipynbをUNIPAへ提出（追加ファイルを使った場合は添付）。チームの氏名、自分の担当、改善点、2通りの確認を短く記す。AIを使った場合は、用途と自分で確認したことも書く。',
              'Improve one part of the app using demo feedback. Each student submits an executed .ipynb to UNIPA, plus any extra files their app needs. Briefly name the team, your contribution, improvement and two checks. Note any AI help and what you verified.'),
    slides=[('今日は、天気ハッカソン','Today: Weather Hackathon'),
            ('天気で、誰の何を助ける？','Whose weather question will you answer?'),
            ('どう作る？','How will you build it?'),
            ('必要なもの','What is required?'),
            ('最後は、動くところを見せる','How will you present it?'),
            ('① 都市名 → 場所','① City name → location'),
            ('② 場所 → 天気データ','② Location → weather data'),
            ('forで、日ごとに取り出す','Use for to read each day'),
            ('グループで、うまく進める','Working well together'),
            ('グループで制作開始','Groups: build time'),
            ('全チーム、実演','Demo time'),
            ('保存して、改善する','Save it and improve it')],
)


def execute_cell(source, scope):
    """Execute trusted author code and return stdout and the final expression."""
    tree = ast.parse(source, filename='<lesson cell>')
    expression = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(tree, '<lesson cell>', 'exec'), scope)
        value = eval(compile(ast.Expression(expression.value), '<lesson cell>', 'eval'), scope) if expression else None
    return output.getvalue(), value


def build(root, c):
    folder = root/'weeks/week-07'
    data = json.loads((folder/'weather-response.json').read_text())
    source = json.loads((folder/'weather-source.json').read_text())
    assert source['hashes'] == [hashlib.sha256(code.encode()).hexdigest() for code in [LOCATION_CODE, WEATHER_CODE]]
    retrieved = datetime.fromisoformat(source['retrieved_at']).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M JST')
    outputs = [entry[0]['data']['text/plain'] for entry in source['outputs']]
    loop_output, _ = execute_cell(FOR_CODE, {'weather':data})
    rows = [('challenge-starter.ipynb','スターターNotebook（コード2セル）','Starter notebook (2 code cells)')]
    guide_link = ('weather-code.html','天気コード集・実行結果','Weather code guide / outputs')
    source_line = c.p('実際のPython実行結果：柏、'+retrieved+'取得。今実行すると値が変わります。<a href="https://open-meteo.com/en/docs">Open-Meteo</a>。',
                      'Actual Python output: Kashiwa, retrieved '+retrieved+'. Fresh requests return updated values. <a href="https://open-meteo.com/en/docs">Open-Meteo</a>.','weather-source')
    def steps(items): return '<ol class="weather-steps">'+''.join('<li>'+c.bi(*item)+'</li>' for item in items)+'</ol>'
    def heading(ja,en): return '<h2>'+c.bi(ja,en)+'</h2>'
    def shown(code, output):
        return c.code_html(code,output).replace('aria-expanded="false"','aria-expanded="true"').replace(' hidden aria-live',' aria-live')
    def timer(key,seconds,unit):
        value = seconds/60 if unit=='minutes' else seconds
        return f'''<div class="hackathon-clock" data-countdown="{key}" data-seconds="{seconds}" data-unit="{unit}"><output role="timer" aria-live="off" data-clock>00:00</output><div class="clock-controls"><button type="button" data-clock-toggle aria-label="Start / 開始" aria-pressed="false">▶</button><button type="button" data-clock-reset aria-label="Reset / リセット">↺</button><label>{c.bi('時間','Time')} <input data-clock-duration type="number" min="1" max="{180 if unit=='minutes' else 600}" value="{value:g}" step="1"> {c.bi('分','min') if unit=='minutes' else c.bi('秒','sec')}</label><span data-clock-status role="status"></span></div></div>'''
    bodies = [
        c.p('天気データを、役立つアプリに。','Turn weather data into a useful app.','lesson-lead')+'<p class="large-stamp">60 MIN / 2–3 PEOPLE</p>'+c.p('最後は全チームが、動く作品を見せます。','Every team finishes with a working demo.')+c.p(*SPEC['flow'],'hackathon-plan'),
        c.p('完成品は、問いに答えるNotebook。結果を見て分かること。','Your app is a notebook that answers a question, with a result people can see.','lesson-lead')+c.list_html([IDEAS[0],IDEAS[1],IDEAS[3]]),
        steps(BUILD_STEPS)+c.p('必要な例だけ、別ページのコード集から選べます。追加インストールは不要。','Use the separate code guide when needed. No extra packages to install.')+c.links([guide_link]),
        c.list_html(SPEC['requirements']),
        c.p('1チーム60〜90秒。Notebookをそのまま見せる。別の発表スライドは不要。','60–90 seconds per team. Present from the notebook; no separate slide deck.','lesson-lead')+steps(DEMO_GUIDE),
        c.p('都市名を緯度・経度に変えるAPI。results[0]は最初の候補。街・地域・国が合っているか確認しよう。','This API turns a city name into coordinates. results[0] is the first match: check the city, region and country.')+'<div class="api-example">'+shown(LOCATION_CODE,outputs[0])+'</div>'+source_line,
        c.p('その場所の天気をjson.loadで辞書に。最後のweather["daily"]はprintなしで表示できる。','json.load reads weather into a dictionary. The final weather["daily"] displays automatically, without print().')+'<div class="api-example">'+shown(WEATHER_CODE,outputs[1])+'</div>'+c.p('この設定では0＝昨日、1＝今日、2＝明日、3＝明後日。日付は選んだ場所の現地時間。昨日はモデル推定値。','With these settings: 0 = yesterday, 1 = today, 2 = tomorrow, 3 = the next day. Dates use the location’s local time. Yesterday is a model estimate.'),
        c.p('1から始め、昨日を飛ばす。同じ番号iで日付・最高気温・降水確率を取り出す。','Start at 1 to skip yesterday. Use the same index i for the date, high temperature and rain probability.')+'<div class="api-example">'+shown(FOR_CODE,loop_output)+'</div>'+c.p('このforを自分たちで書き、目的に合わせて変えよう。printはループ内の各行を表示するために使う。','Write and adapt a for loop for your own app. Here print is needed to show each row inside the loop.')+c.links([guide_link]),
        c.list_html(GROUP_GUIDE)+c.p(*AI_GUIDE,'weather-ai-note'),
        c.p('2〜3人で集まろう。スターターの2つのコードセルを実行できたら、その下から制作開始。','Form groups of 2–3. Run the starter’s two code cells, then add your app below.','lesson-lead')+timer('build',3600,'minutes')+c.links(rows,7,'lecture.html?slide=10')+c.links([('challenge.html','課題の手順','Challenge instructions'),guide_link]),
        c.p('14:25–14:45。全チームが実演。20分をチーム数で割り、1組60〜90秒を目安に調整。','14:25–14:45. Every team demos. Divide 20 minutes among teams, aiming for 60–90 seconds each.','lesson-lead')+timer('presentation',90,'seconds')+c.p('目的を一文。表示を見せる。条件を変える。forを一行説明。全員が一言。','State the purpose. Show the visual. Change a setting. Explain one for-loop line. Everyone speaks.'),
        c.p(*SPEC['homework'],'lesson-lead')+c.p('締切：2026年11月18日（水）23:59 JST。作品はクラスギャラリーへ。','Due: Wednesday, November 18, 2026, 23:59 JST. Projects go to the class gallery.')+c.links([('challenge.html','課題・提出方法','Assignment / submission')]),
    ]
    layouts = ['hero','question','plain','requirements','plain','api','api','api','pair','timer','presentation','exit']
    sections = []
    assert len(bodies)==len(layouts)==len(SPEC['slides'])
    for i,((ja,en),body,layout) in enumerate(zip(SPEC['slides'],bodies,layouts),1):
        tag = 'h1' if i==1 else 'h2'
        sections.append(f'<section class="slide lesson-slide layout-{layout}" data-slide data-slide-number="{i}" data-ink-id="w7-weather-{i}" hidden><p class="slide-kicker">WEEK 07 · WEATHER HACKATHON</p><{tag}>'+c.bi(ja,en)+f'</{tag}>'+body+'</section>')
    release = SPEC['date']+'T12:00:00+09:00'
    head = c.page_head('Week 07 · Weather Hackathon','course-decks.css','course-decks.js',VERSION)
    head += f'<link rel="stylesheet" href="hackathon.css?v={VERSION}"><script src="hackathon.js?v={VERSION}" defer></script><link rel="stylesheet" href="../../assets/slide-annotations.css"><script src="../../assets/slide-annotations.js" defer></script><script src="../../assets/slide-swipe.js" defer></script></head>'
    c.write(folder/'lecture.html',head+f'<body class="lecture-page course-deck weather-hackathon" data-week="7" data-release="{release}"><header class="lecture-header"><a id="lecture-return" href="../../agenda.html?open=07#week-07">← '+c.bi('授業予定','Agenda')+'</a><span class="lecture-mark">PRG / 26–2</span><button id="language-toggle" class="language-toggle" type="button">EN</button></header><main><div id="slides-view" class="view"><nav class="slide-controls" aria-label="Slide navigation"><div class="slide-nav-group"><button id="previous-slide" type="button">← '+c.bi('前へ','Previous')+'</button><span id="slide-count" aria-live="polite"></span><button id="next-slide" type="button">'+c.bi('次へ','Next')+' →</button></div><button id="slide-fullscreen" type="button" class="slide-fullscreen" aria-pressed="false">⛶</button></nav><div class="slide-stage">'+''.join(sections)+'</div></div></main><script type="application/json" id="lesson-data">{}</script></body></html>')

    starter = [c.mdcell('''# Week 07 · 天気ハッカソン / Weather Hackathon

チーム全員の氏名 / Team members：

自分の担当 / My contribution：

人に役立つ天気アプリを、このNotebookで作ろう。最初は下の**コード2セルだけ**を順に実行。追加インストール・pandas・APIキーは不要。
Build a useful weather app here. Run the **two code cells** below in order; no extra packages or API key.

## 1. 都市名から場所を探す / Find a city
`city` を変えて実行。表示された街・地域・国を確認。見つからなければ英字で別の都市名を試そう。
Change `city`, run the cell and check the returned city, region and country. Try another spelling if no match is found.'''),c.codecell(LOCATION_CODE),
        c.mdcell('''## 2. その場所の天気を取得 / Get its weather

1つ目のセルの `place`（緯度・経度）を使います。`urlopen` でAPIにつなぎ、`json.load` で辞書に読み込みます。最後の値は `print()` なしで表示できます。
Uses coordinates from `place`. `urlopen` connects to the API; `json.load` reads a dictionary. The last expression displays automatically.

`past_days=1`、`forecast_days=3` なので、**0＝昨日、1＝今日、2＝明日、3＝明後日**。`timezone="auto"` はその場所の現地時間。
With these settings: **0 = yesterday, 1 = today, 2 = tomorrow, 3 = the next day**, in the selected location’s local time.

- `temperature_2m_max` / `temperature_2m_min`：最高・最低気温 / high and low (°C)
- `precipitation_probability_max`：1日の最大降水確率 / daily maximum precipitation probability (%)
- `rain_sum` + `showers_sum`：雨量の合計 / total liquid rain (mm)

昨日の値はモデル推定で、観測の証明ではありません。降水確率は「必ず降る」という意味ではありません。
Yesterday’s values are model estimates, not confirmed observations. A probability does not guarantee rain.'''),c.codecell(WEATHER_CODE),
        c.mdcell('## ここから、自分たちのアプリへ / Your app starts here\n\n'+SPEC['brief'][0]+'\n\n'+SPEC['brief'][1]+'\n\n**必須：APIデータ・自分たちのfor・見やすい結果。whileは任意。関数の定義は不要。**\n**Required: API data, your own for loop, and a clear visual result. while is optional; no function definitions needed.**\n\n### 例えば / Ideas\n'+ '\n'.join('- '+ja+'  \n  '+en for ja,en in IDEAS)+'\n\n下にCode CellとMarkdown Cellを追加。使う人・問い・コード・結果・説明を残そう。場所や条件を2通り確認し、全員が自分の変更を説明できるように。AIを使った場合は用途と自分で確認したことを一言。\nAdd your own Code and Markdown cells: user, question, code, results and explanation. Check two locations or settings. Each person explains their change; briefly note any AI help and what you checked.\n\n[課題・提出方法 / Challenge](https://yohman.github.io/26-2-Programming/weeks/week-07/challenge.html?p=) · [コード集 / Code guide](https://yohman.github.io/26-2-Programming/weeks/week-07/weather-code.html?p=) · [Data: Open-Meteo](https://open-meteo.com/en/docs)\n\nプレビューの保存出力：'+retrieved+'、柏。自分で実行すると更新されます。\nSaved preview output: Kashiwa, '+retrieved+'. Running the cells fetches fresh values.')]
    for i,cell in enumerate([starter[1],starter[3]]):
        cell['execution_count']=i+1
        cell['outputs']=source['outputs'][i]
    c.notebook(folder/'challenge-starter.ipynb',starter)
    for obsolete in ['practice.ipynb','week-07-in-class-logic-review.ipynb','starter-files.zip']:
        (folder/obsolete).unlink(missing_ok=True)

    body = c.p(*SPEC['brief'],'lesson-lead')+heading('完成品・必要なもの','Final deliverable and requirements')+c.list_html(SPEC['requirements'])
    body += heading('始め方','Get started')+c.p('スターターの2つのコードセルを順番に実行。都市名を変えて場所を確認し、その場所の天気データを読む。下に自分たちのセルを追加する。', 'Run the starter’s two code cells in order. Change the city, confirm its location and fetch the weather. Add your own cells below.')+c.links(rows,7)+c.links([guide_link])
    body += c.p('コード集は必要なテーマだけ使う参考ページ。すべて作る必要はありません。追加インストール・pandas・APIキーは不要。', 'Choose only the examples you need from the code guide; you do not need to build them all. No extra packages, pandas or API key.')
    body += heading('アイデアを選ぶ','Choose a question')+c.list_html(IDEAS)+c.p('予報は確率。昨日の雨量はモデル推定。日付は選んだ場所の現地時間で確認しよう。','Forecasts describe probabilities. Yesterday’s rainfall is a model estimate. Check dates in the selected location’s local time.')
    body += heading('作り方','Build it')+steps(BUILD_STEPS)+heading('今日の流れ','Today’s plan')+c.p(*SPEC['flow'])
    body += heading('グループの進め方','Good group work')+c.list_html(GROUP_GUIDE)+c.p(*AI_GUIDE)
    body += '<details class="weather-hints"><summary>'+c.bi('困ったとき','If you get stuck')+'</summary>'+c.list_html([
        ('resultsが見つからない：都市名を英字で入力し直す。別の街が出たら国・地域を確認する。', 'No results? Try another spelling. A city name can match another place: check the country and region.'),
        ('通信エラー：少し待ってセルを再実行。つながらない間はコード集の実行結果を参考に、説明と画面の案を考える。', 'Network error? Retry the cell after a short wait. Use the guide’s recorded outputs to plan the explanation and display meanwhile.'),
        ('Noneは値なし。0%や0mmと同じ意味ではない。', 'None means missing data; it is different from 0% or 0 mm.'),
    ])+'</details>'
    body += heading('最後に、全チームが実演','Every team demos')+c.p('14:25から20分。1組60〜90秒を目安に調整。Notebookをそのまま見せる。','Twenty minutes from 14:25; aim for 60–90 seconds per team. Present directly from the notebook.')+steps(DEMO_GUIDE)
    body += heading('宿題・提出','Homework / submission')+c.p(*SPEC['homework'])+c.p('締切：2026年11月18日（水）23:59 JST。作品はクラスギャラリーへ。途中でも、自分で書いたコードと試したことを残して提出。','Due: Wednesday, November 18, 2026, 23:59 JST. Projects go to the class gallery. If unfinished, submit your own code and explain what you tried.')+c.links([('lecture.html','講義・制作タイマー','Briefing and timers')])
    c.write(folder/'challenge.html',c.page_head('Week 07 · Weather Hackathon','course-pages.css','course-page.js',VERSION)+f'<link rel="stylesheet" href="hackathon.css?v={VERSION}"></head><body class="course-challenge weather-hackathon" data-release="{release}"><header class="lecture-header"><a href="../../agenda.html?open=07#week-07">← '+c.bi('授業予定','Agenda')+'</a><span class="lecture-mark">WEEK 07</span><button id="language-toggle" class="language-toggle" type="button">EN</button></header><main id="course-page" hidden><p class="slide-kicker">'+c.bi('授業内ハッカソン＋宿題','In-class hackathon + homework')+'</p><h1>'+c.bi(SPEC['title_ja'],SPEC['title'])+'</h1>'+body+'</main></body></html>')

    old = (root/'content/weeks/07-logic-loops.md').read_text(); front=old.split('---',2)[1]
    updates=dict(title=SPEC['title'],title_ja=SPEC['title_ja'],overview=SPEC['aim'][1],overview_ja=SPEC['aim'][0],homework_title='Improve your weather app',homework_title_ja='天気アプリを改善する',challenge_title='60-min hackathon',challenge_title_ja='60分ハッカソン')
    front=re.sub(r'^practice_mix(?:_ja)?:.*\n','',front,flags=re.M)
    for key,value in updates.items():
        if re.search(r'^'+key+':',front,re.M): front=re.sub(r'^'+key+r':.*$',key+': '+value,front,flags=re.M)
        else: front=front.rstrip()+'\n'+key+': '+value+'\n'
    text='---'+front+'---\n'
    panels=[('Lecture Flow',SPEC['flow']),('In-Class Notebook',('スターターは一つ、コードは2セル。都市名から場所を探し、APIで天気を取得。下に自分たちのセルを追加する。','One starter, two code cells: find a city, then get its weather. Add your own app below.')),('In-Class Challenge',(SPEC['brief'][0]+' [手順と教材](weeks/week-07/challenge.html)。',SPEC['brief'][1]+' [Instructions](weeks/week-07/challenge.html).')),('Student Work',('最後に全チームが実演。全員が一言話し、forと結果を説明する。','Every team demos. Everyone speaks briefly and explains their for loop and results.')),('Take-Home Assignment',SPEC['homework']),('Aha!',SPEC['aim']),('Takeaway',('APIのデータを、使う人に役立つ答えに変える。','Turn API data into an answer someone can use.'))]
    for name,(ja,en) in panels: text+=f'## {name}\nEN: {en}\nJP: {ja}\n'
    text+='## Resources\n- [Weather Hackathon — Briefing & Timers](weeks/week-07/lecture.html) {lecture}\n- [スターターNotebook（コード2セル） / Starter notebook (2 code cells)](weeks/week-07/challenge-starter.ipynb) {notebook}\n- [天気コード集・実行結果 / Weather code guide / outputs](weeks/week-07/weather-code.html) {experiment}\n- [ハッカソンの手順 / Hackathon instructions](weeks/week-07/challenge.html) {challenge}\n- [宿題・提出方法 / Homework and submission](weeks/week-07/challenge.html) {homework}\n'
    c.write(root/'content/weeks/07-logic-loops.md',text)
    c.write(folder/'README.txt','Week 07 · Weather Hackathon\n\nOne starter: challenge-starter.ipynb. Run its two code cells in order, check the city, then add your own app below. No custom functions, extra packages or API key required.\n\nRequired: API data, your own for loop and a clear visual answer. while is optional. Reference examples: weather-code.html. Instructions: challenge.html.\n\nData: Open-Meteo https://open-meteo.com/en/docs\nYesterday is model-estimated rainfall, not a confirmed observation. Forecast probability is not certainty. Dates use the chosen location’s time zone.\n\nBuild for 60 minutes in teams of 2–3. Every member contributes and explains a change. Demo in 60–90 seconds. Submit an executed .ipynb and any extra files actually used by 2026-11-18 23:59 JST.\n')
    import weather_examples
    weather_examples.build(root,c,LOCATION_CODE,WEATHER_CODE,VERSION,release)
