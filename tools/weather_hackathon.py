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

VERSION = '20261112-weather-parameters'
IMPORTS = '''import json
from urllib.request import urlopen
from urllib.parse import urlencode'''

METEO_SETTINGS = '''# Kashiwa, Japan — change these settings first
lat = 35.86224
lon = 139.97733
past_days = 1
forecast_days = 3
timezone = "auto"
daily_fields = (
    "temperature_2m_max,temperature_2m_min,"
    "precipitation_probability_max,rain_sum,showers_sum"
)
timeout = 10'''

METEO_REQUEST = '''url = "https://api.open-meteo.com/v1/forecast?" + urlencode({
    "latitude": lat, "longitude": lon,
    "daily": daily_fields,
    "past_days": past_days, "forecast_days": forecast_days,
    "timezone": timezone
})
with urlopen(url, timeout=timeout) as response:
    weather = json.load(response)
weather["daily"]'''

LOCATION_CODE = '''import json
from urllib.request import urlopen
from urllib.parse import urlencode

# Change these settings first
city = "Kashiwa"
match_count = 1
language = "en"
timeout = 10

url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode({
    "name": city, "count": match_count, "language": language
})
with urlopen(url, timeout=timeout) as response:
    locations = json.load(response)
place = locations["results"][0]
place["name"], place.get("admin1"), place["country"]'''

WEATHER_CODE = '''# Use the city found in the previous cell
lat = place["latitude"]
lon = place["longitude"]
past_days = 1
forecast_days = 3
timezone = "auto"
daily_fields = (
    "temperature_2m_max,temperature_2m_min,"
    "precipitation_probability_max,rain_sum,showers_sum"
)
timeout = 10

url = "https://api.open-meteo.com/v1/forecast?" + urlencode({
    "latitude": lat, "longitude": lon,
    "daily": daily_fields,
    "past_days": past_days, "forecast_days": forecast_days,
    "timezone": timezone
})
with urlopen(url, timeout=timeout) as response:
    weather = json.load(response)
weather["daily"]'''

READ_CODE = '''day_offset = 0  # 0 = today, 1 = tomorrow, -1 = yesterday

daily = weather["daily"]
i = past_days + day_offset
(daily["time"][i], daily["temperature_2m_max"][i],
 daily["precipitation_probability_max"][i])'''

FOR_CODE = '''start_day = 0  # 0 = start today, 1 = start tomorrow

daily = weather["daily"]
for i in range(past_days + start_day, len(daily["time"])):
    print(daily["time"][i],
          daily["temperature_2m_max"][i], "°C",
          daily["precipitation_probability_max"][i], "%")'''

METEO_CODE = IMPORTS + "\n\n" + METEO_SETTINGS + "\n\n" + METEO_REQUEST

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
    ('新しい空のNotebookを作り、weather-app.ipynbとして保存。Markdownでタイトル・氏名・問いを書く。', 'Create a new blank notebook, save it as weather-app.ipynb, and add a Markdown title, names and question.'),
    ('Webチュートリアルの「データ取得」をCode Cellで実行し、結果を確認する。', 'Run the web tutorial’s “Get the data” example in a Code cell and inspect the result.'),
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
        ('自分たちで空のNotebookを作成し、使う人と問いをMarkdownで書く。', 'Create your own notebook from scratch; explain the user and question in Markdown.'),
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
            ('設定を、先に決める','Set the parameters first'),
            ('設定を使って、APIへ','Use the settings to request data'),
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
    assert source['meteo_sha256'] == hashlib.sha256(METEO_CODE.encode()).hexdigest()
    loop_output, _ = execute_cell(FOR_CODE, {'weather':data,'past_days':source['parameters']['past_days']})
    guide_link = ('weather-code.html','Webチュートリアル・実行結果','Web tutorial / outputs')
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
        steps(BUILD_STEPS)+c.p('必要な例だけ、別ページのコード集から選べます。追加インストールは不要。','Use the web tutorial as a reference for your own notebook. No extra packages to install.')+c.links([guide_link]),
        c.list_html(SPEC['requirements']),
        c.p('1チーム60〜90秒。Notebookをそのまま見せる。別の発表スライドは不要。','60–90 seconds per team. Present from the notebook; no separate slide deck.','lesson-lead')+steps(DEMO_GUIDE),
        c.p('緯度・経度、日数、欲しい項目を変数にする。変更はここから。','Set the coordinates, day counts and weather fields first. This is where you make changes.')+c.code_html(METEO_SETTINGS)+c.p('lat / lon＝場所。past_days＝過去の日数。forecast_days＝今日を含む予報の日数。設定を変えたら、次のAPIセルも再実行。','lat / lon choose the place. past_days adds past dates; forecast_days includes today. After changing a setting, rerun the API cell too.'),
        c.p('前の設定をURLのパラメータに渡す。urlopenで接続し、json.loadで辞書に読む。','Pass the settings into the URL parameters. urlopen connects; json.load reads the response into a dictionary.')+'<div class="api-example">'+shown(IMPORTS+'\n\n'+METEO_REQUEST,source['meteo_output'])+'</div>'+source_line,
        c.p('start_dayで開始日を選ぶ。past_daysを足すと、設定に合わせて今日・明日の番号になる。','Choose where to start with start_day. Adding past_days keeps the date index aligned with your request settings.')+'<div class="api-example">'+shown(FOR_CODE,loop_output)+'</div>'+c.p('0＝今日から、1＝明日から。同じ番号iで日付・気温・降水確率を取り出す。','0 starts today; 1 starts tomorrow. Use the same index i for the date, temperature and precipitation probability.')+c.links([guide_link]),
        c.list_html(GROUP_GUIDE)+c.p(*AI_GUIDE,'weather-ai-note'),
        c.p('2〜3人で集まろう。空のNotebookを自分たちで作り、保存。Markdownのタイトルと問いを書き、Webチュートリアルを参考に制作開始。','Form groups of 2–3. Create and save your own blank notebook. Add a Markdown title and question, then use the web tutorial to begin.','lesson-lead')+timer('build',3600,'minutes')+c.links([('challenge.html','課題の手順','Challenge instructions'),guide_link]),
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

    # Students author their own notebook; do not regenerate distributed starters.
    for obsolete in ['challenge-starter.ipynb','practice.ipynb','week-07-in-class-logic-review.ipynb','starter-files.zip']:
        (folder/obsolete).unlink(missing_ok=True)

    body = c.p(*SPEC['brief'],'lesson-lead')+heading('完成品・必要なもの','Final deliverable and requirements')+c.list_html(SPEC['requirements'])
    body += heading('空のNotebookから始める','Create your own notebook from scratch')
    body += c.p('この課題では、配布ファイルを使わず、新しい空の.ipynbを自分たちで作成してください。','For this challenge, you must create your own new, blank .ipynb file.')
    body += steps([
        ('VS Codeのコマンドパレットで「Create: New Jupyter Notebook」を実行し、右上でPythonカーネルを選ぶ。', 'In VS Code’s Command Palette, run Create: New Jupyter Notebook, then select your Python kernel at the top right.'),
        ('weather-app.ipynbなど、作品に合う名前で保存する。', 'Save the file with a name such as weather-app.ipynb.'),
        ('最初のセルをMarkdownにし、作品名・チームの氏名・使う人・問いを書く。', 'Make the first cell Markdown: add your app title, team names, user and question.'),
        ('Code Cellを追加し、Webチュートリアルの「データ取得」を実行。結果と自分の説明を交互に置く。', 'Add a Code cell and run “Get the data” from the web tutorial. Alternate code/results with your own Markdown explanation.'),
    ])+c.links([guide_link])+c.p('<a href="https://code.visualstudio.com/docs/datascience/jupyter-notebooks">Notebookの作成・操作（VS Code公式）</a>', '<a href="https://code.visualstudio.com/docs/datascience/jupyter-notebooks">Create and edit notebooks (VS Code guide)</a>','weather-source')
    body += c.p('コード集は必要なテーマだけ使う参考ページ。すべて作る必要はありません。追加インストール・pandas・APIキーは不要。', 'Choose only the examples you need from the code guide; you do not need to build them all. No extra packages, pandas or API key.')
    body += heading('アイデアを選ぶ','Choose a question')+c.list_html(IDEAS)+c.p('予報は確率。昨日の雨量はモデル推定。日付は選んだ場所の現地時間で確認しよう。','Forecasts describe probabilities. Yesterday’s rainfall is a model estimate. Check dates in the selected location’s local time.')
    body += heading('今日の流れ','Today’s plan')+c.p(*SPEC['flow'])
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
    panels=[('Lecture Flow',SPEC['flow']),('In-Class Notebook',('新しい空のNotebookを自分で作り、保存する。Markdownで作品名・氏名・問いを書き、Webチュートリアルのデータ取得から始めよう。','Create and save your own blank notebook. Add a Markdown title, names and question, then begin with “Get the data” in the web tutorial.')),('In-Class Challenge',(SPEC['brief'][0]+' [手順と教材](weeks/week-07/challenge.html)。',SPEC['brief'][1]+' [Instructions](weeks/week-07/challenge.html).')),('Student Work',('最後に全チームが実演。全員が一言話し、forと結果を説明する。','Every team demos. Everyone speaks briefly and explains their for loop and results.')),('Take-Home Assignment',SPEC['homework']),('Aha!',SPEC['aim']),('Takeaway',('APIのデータを、使う人に役立つ答えに変える。','Turn API data into an answer someone can use.'))]
    for name,(ja,en) in panels: text+=f'## {name}\nEN: {en}\nJP: {ja}\n'
    text+='## Resources\n- [Weather Hackathon — Briefing & Timers](weeks/week-07/lecture.html) {lecture}\n- [Webチュートリアル・実行結果 / Web tutorial / outputs](weeks/week-07/weather-code.html) {experiment}\n- [ハッカソンの手順 / Hackathon instructions](weeks/week-07/challenge.html) {challenge}\n- [宿題・提出方法 / Homework and submission](weeks/week-07/challenge.html) {homework}\n'
    c.write(root/'content/weeks/07-logic-loops.md',text)
    c.write(folder/'README.txt','Week 07 · Weather Hackathon\n\nCreate your own blank notebook and save it as weather-app.ipynb. Start with a Markdown title, team names, user and question. Open weather-code.html and run the first API example in a Code cell. Alternate code/results with your own explanation. No custom functions, extra packages or API key required.\n\nRequired: API data, your own for loop and a clear visual answer. while is optional. Reference examples: weather-code.html. Instructions: challenge.html.\n\nData: Open-Meteo https://open-meteo.com/en/docs\nYesterday is model-estimated rainfall, not a confirmed observation. Forecast probability is not certainty. Dates use the chosen location’s time zone.\n\nBuild for 60 minutes in teams of 2–3. Every member contributes and explains a change. Demo in 60–90 seconds. Submit an executed .ipynb and any extra files actually used by 2026-11-18 23:59 JST.\n')
    import weather_examples
    weather_examples.build(root,c,METEO_CODE,LOCATION_CODE,WEATHER_CODE,VERSION,release)
