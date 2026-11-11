"""Week 7 weather hackathon, using the established course presentation shell."""
from pathlib import Path
from urllib.parse import urlencode
import contextlib
import html
import io
import json
import re
from datetime import datetime, timedelta, timezone

VERSION = '20261112-briefing'
API_URL = 'https://api.open-meteo.com/v1/forecast?' + urlencode({
    'latitude': 35.86, 'longitude': 139.97,
    'hourly': 'temperature_2m,precipitation_probability',
    'forecast_hours': 24, 'timezone': 'Asia/Tokyo',
})

API_REQUEST = '''import json
from urllib.request import urlopen
from urllib.parse import urlencode

url = "https://api.open-meteo.com/v1/forecast?" + urlencode({
    "latitude": 35.86, "longitude": 139.97,
    "hourly": "temperature_2m,precipitation_probability",
    "forecast_hours": 24, "timezone": "Asia/Tokyo"
})'''

API_EXAMPLE = API_REQUEST + '''
with urlopen(url, timeout=10) as response:
    data = json.load(response)
print(data["timezone"])
print(len(data["hourly"]["time"]), "hours")'''

LIVE_LOAD = API_REQUEST + '''
from datetime import datetime, timezone

try:
    with urlopen(url, timeout=10) as response:
        data = json.load(response)
    data["_source"] = {"url": url,
                       "retrieved_at": datetime.now(timezone.utc).isoformat()}
    with open("weather-response.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print("Live API / APIから取得")
except (OSError, ValueError):
    with open("weather-response.json", encoding="utf-8") as file:
        data = json.load(file)
    print("Saved JSON / 保存した予報を使用")

print("Retrieved:", data.get("_source", {}).get("retrieved_at", "see forecast dates"))'''

CACHE_LOAD = '''import json
with open("weather-response.json", encoding="utf-8") as file:
    data = json.load(file)
print("Saved forecast / 保存した予報")'''

NORMALIZE = '''forecast = []
hourly = data["hourly"]
for i in range(len(hourly["time"])):
    temp = hourly["temperature_2m"][i]
    rain = hourly["precipitation_probability"][i]
    if temp is not None and rain is not None:
        forecast.append({"time": hourly["time"][i],
                         "temp": temp, "rain": rain})
print(len(forecast), "hours / 時間分")
print("Forecast:", forecast[0]["time"], "to", forecast[-1]["time"])'''

FILTER_CODE = '''max_rain = 30
min_temp = 10
chosen = []
for hour in forecast:
    if hour["rain"] <= max_rain and hour["temp"] >= min_temp:
        chosen.append(hour)
print(len(chosen), "hours match")'''

VISUAL_SETUP = 'from html import escape\n\ndef weather_board(forecast, chosen, min_temp, max_rain):\n    board = f\'<div style="font:15px/1.5 system-ui;color:#203b2d"><h3 style="margin:0">{len(chosen)} / {len(forecast)} hours match · 条件に合う時間</h3>\'\n    board += f\'<p style="margin:4px 0 12px">Temperature ≥ {min_temp}°C · Precipitation ≤ {max_rain}% · Japan time · Matches first / 合う時間を先に表示</p>\'\n    board += \'<div style="max-height:340px;overflow:auto"><table style="border-collapse:collapse;width:100%;text-align:left"><thead><tr style="background:#315876;color:white"><th style="padding:8px">Time / 時刻</th><th>°C</th><th>Rain %</th><th>Your rule / 条件</th></tr></thead><tbody>\'\n    for hour in chosen + [item for item in forecast if item not in chosen]:\n        matches = hour in chosen\n        color = \'#dceee2\' if matches else \'#f1f3f2\'\n        label = \'✓ Match / 合う\' if matches else \'— / 合わない\'\n        time = escape(hour["time"].replace("T", " "))\n        board += f\'<tr style="background:{color};border-bottom:1px solid white"><td style="padding:7px 8px">{time}</td><td>{hour["temp"]}</td><td>{hour["rain"]}%</td><td>{label}</td></tr>\'\n    board += \'</tbody></table></div>\'\n    if not chosen:\n        board += \'<p>No hours match. Try another setting. / 条件を変えて試そう。</p>\'\n    return board + \'</div>\'\n'
VISUAL_CALL = 'from IPython.display import HTML, display\ndisplay(HTML(weather_board(forecast, chosen, min_temp, max_rain)))'

WHILE_CODE = '''command = ""
while command != "quit":
    command = input("show / warmer / quit: ").strip().lower()
    if command == "warmer":
        min_temp += 1
    if command in ["show", "warmer"]:
        print("Minimum temperature:", min_temp, "°C")
        matches = 0
        chosen = []
        for hour in forecast:
            if hour["rain"] <= max_rain and hour["temp"] >= min_temp:
                print(hour["time"], hour["temp"], "°C", hour["rain"], "%")
                matches += 1
                chosen.append(hour)
        display(HTML(weather_board(forecast, chosen, min_temp, max_rain)))
        if matches == 0:
            print("No matching hours / 条件に合う時間はありません")'''

WHILE_BRIEF = '''command = ""
while command != "quit":
    command = input("show / quit: ")
    if command == "show":
        # Put your for + if here
        print("Searching the forecast...")'''

SPEC = dict(
    title='Weather Hackathon', title_ja='天気ハッカソン',
    date='2026-11-12', due='2026-11-18', version=VERSION,
    aim=('API・辞書のリスト・if・for・whileを組み合わせ、天気を使う小さな道具を作る。',
         'Combine API data, dictionaries, if, for and while to build a small weather tool.'),
    brief=('天気予報を使って、誰かの「いつ・どうする？」に視覚的に答えるNotebookを作ろう。2〜3人で制作し、最後に全チームが実演する。',
           'Build a weather-assistant notebook with a visual answer to someone’s question. Work in teams of 2–3 and give a short demo at the end.'),
    flow=('13:10 説明10分 / 13:20 準備5分 / 13:25 チーム制作60分 / 14:25 発表20分 / 14:45 保存・まとめ5分。',
          '13:10 briefing 10 min / 13:20 setup 5 min / 13:25 team build 60 min / 14:25 demos 20 min / 14:45 save and wrap up 5 min.'),
    requirements=[
        ('誰が、何を決めるための道具かをMarkdownで書く。', 'Explain the user and the decision in Markdown.'),
        ('APIの予報をforとifで調べ、自分たちの条件で時間を選ぶ。', 'Use for and if to select forecast hours using your own rule.'),
        ('条件に合わせて変わる視覚表示を一つ。表・グラフ・地図など。', 'Include a visual that responds to the settings: a table, chart or map.'),
        ('whileで繰り返し使え、quitで終了できるようにする。', 'Use while to let the user try again and quit to finish.'),
        ('設定を2通り試し、結果に基づく提案とデータの出典を記す。', 'Try two settings. Add a recommendation and the data source.'),
    ],
    homework=('発表でもらった意見を使い、同じ道具を一つ改善する。各自のNotebookにチーム全員の氏名、自分の担当、改善点と設定2通りの確認を書く。実行済み.ipynbとweather-response.jsonをUNIPAへ提出。AIを使った場合は、用途と自分で確認したことを短く記す。',
              'Improve the same tool using demo feedback. Each student submits an executed notebook and weather-response.json to UNIPA. Name the team, your contribution, one improvement and two tested settings. Briefly note any AI help and what you checked yourself.'),
    slides=[('今日は、天気ハッカソン', 'Today: Weather Hackathon'),
            ('誰の、どんな判断を助ける？', 'Whose decision will you help?'),
            ('どう作る？', 'How will you build it?'),
            ('必要なもの', 'What is required?'),
            ('最後は、動くところを見せる', 'How will you present it?'),
            ('APIから予報をもらう', 'Get the forecast from an API'),
            ('1時間を、一つの辞書に', 'One hour, one dictionary'),
            ('条件で、表示が変わる', 'A rule changes the result'),
            ('グループで、うまく進める', 'Working well together'),
            ('グループで制作開始', 'Groups: build time'),
            ('全チーム、実演', 'Demo time'),
            ('保存して、改善する', 'Save it and improve it')],
)

GROUP_GUIDE = [
    ('最初に、使う人と目的を全員で決める。', 'Agree on the user and the question before coding.'),
    ('コードを書く・結果を確かめる・表示と説明を整える。得意なことを分担し、困ったら一緒に考える。', 'Share the coding, checking and visual explanation. Help each other when someone gets stuck.'),
    ('全員がコードの変更に参加し、その変更を説明できるようにする。', 'Everyone contributes a code change and understands what it does.'),
    ('まず小さく動かす。変更を一つずつ確かめ、発表前に全員で実行する。', 'Get a small version working. Check one change at a time and run the notebook together before presenting.'),
]
AI_GUIDE = ('AIはエラーの説明や小さなヒントに使ってよい。作品全体を任せず、使ったコードは全員で読み、結果を自分たちで確かめる。',
            'AI can explain an error or give a small hint. Keep the build in your hands: read the code together and check its results yourselves.')
BUILD_STEPS = [
    ('スターターでAPIの予報を読み込む。', 'Load the API forecast with the starter notebook.'),
    ('誰に役立つかを決め、for＋ifの条件を変える。', 'Choose a user and adapt the for + if rule.'),
    ('結果を見せ、whileで条件を変えて繰り返せるようにする。', 'Show the result and use while to let the user try again.'),
    ('動作を確かめ、Notebookに説明を書く。', 'Check it works and explain it in Markdown.'),
]
DEMO_GUIDE = [
    ('誰の、何を助ける？目的を一文で。', 'State whose decision your tool helps.'),
    ('視覚表示を見せ、条件を変えてもう一度動かす。', 'Show the visual, change a setting and run it again.'),
    ('for・if・whileの一行を説明し、分かったことを話す。全員が一言話す。', 'Explain a line using for, if or while and one finding. Everyone speaks briefly.'),
]


def build(root, c):
    folder = root / 'weeks/week-07'
    data = json.loads((folder/'weather-response.json').read_text())
    source = json.loads((folder/'weather-source.json').read_text())
    scope = {'data': data}
    normalized = io.StringIO()
    with contextlib.redirect_stdout(normalized):
        exec(NORMALIZE, scope)
    forecast = scope['forecast']
    retrieved = datetime.fromisoformat(source['retrieved_at']).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M JST')
    snapshot_note = f'Kashiwa · {retrieved} · Asia/Tokyo · Open-Meteo'
    # The shown API cell was executed live when this snapshot was captured.
    api_output = source['example_output']
    expected = f'{data["timezone"]}\n{len(data["hourly"]["time"])} hours\n'
    assert api_output == expected, 'Refresh weather-source.json and weather-response.json together.'
    rows = [('starter-files.zip', '教材をまとめてダウンロード', 'Download the starter pack'),
            ('challenge-starter.ipynb', '制作を始めるNotebook', 'Start-building notebook'),
            ('practice.ipynb', 'コードの実行例', 'Worked examples'),
            ('weather-response.json', '予報JSON（表でプレビュー）', 'Forecast JSON (table preview)')]
    files = c.links(rows, 7)
    source_line = c.p('実際のAPI実行結果：'+html.escape(retrieved)+'取得、柏の24時間予報。<a href="https://open-meteo.com/en/docs">Open-Meteo APIドキュメント</a>。今取得すると数値や時刻は変わります。',
                      'Actual API run: Kashiwa, retrieved '+html.escape(retrieved)+'. <a href="https://open-meteo.com/en/docs">Open-Meteo API docs</a>. A fresh request will return different times or values.', 'weather-source')
    def timer(key, seconds, unit):
        value = seconds/60 if unit == 'minutes' else seconds
        return f'''<div class="hackathon-clock" data-countdown="{key}" data-seconds="{seconds}" data-unit="{unit}">
<output role="timer" aria-live="off" data-clock>00:00</output>
<div class="clock-controls"><button type="button" data-clock-toggle aria-label="Start / 開始" aria-pressed="false">▶</button><button type="button" data-clock-reset aria-label="Reset / リセット">↺</button><label>{c.bi('時間','Time')} <input data-clock-duration type="number" min="1" max="{180 if unit=='minutes' else 600}" value="{value:g}" step="1"> {c.bi('分','min') if unit=='minutes' else c.bi('秒','sec')}</label><span data-clock-status role="status"></span></div></div>'''
    def steps(items):
        return '<ol class="weather-steps">'+''.join('<li>'+c.bi(*item)+'</li>' for item in items)+'</ol>'
    def shown_code(code, output):
        return c.code_html(code, output).replace('aria-expanded="false"','aria-expanded="true"').replace(' hidden aria-live',' aria-live')
    themes = c.list_html([
        ('自転車通学：「雨が少なく、寒すぎない時間は？」', 'Cycling to campus: “When is it dry enough and warm enough?”'),
        ('サークル：「外で練習するなら、何時がよさそう？」', 'A club: “What time looks good for outdoor practice?”'),
        ('自分たちで、別の使い方を考えてもよい。', 'Your team can choose another use for the forecast.'),
    ])
    demo = '''<div data-weather-demo><div class="weather-inputs"><label>max_rain (%) <input data-rain type="number" min="0" max="100" value="30" required></label><label>min_temp (°C) <input data-temp type="number" min="-40" max="50" step="0.5" value="10" required></label><button data-weather-run type="button">▶ '''+c.bi('実行','Run')+'''</button></div><pre data-language="python"><code data-weather-code></code></pre><div data-weather-board aria-live="polite"></div></div>'''
    list_code = NORMALIZE + '\nprint(forecast[0])'
    list_output = normalized.getvalue() + repr(forecast[0]) + '\n'
    bodies = [
        c.p('予報を、使える道具に。', 'Turn a forecast into something useful.', 'lesson-lead')
        + '<p class="large-stamp">60 MIN / 2–3 PEOPLE</p>'
        +c.p('最後は全チームが、動く作品を見せます。', 'Every team finishes with a working demo.')
        + '<p class="hackathon-plan">'+c.bi('説明10分 / 準備5分 / 制作60分 / 発表20分 / まとめ5分', 'Brief 10 / Setup 5 / Build 60 / Demos 20 / Wrap up 5')+'</p>',
        c.p('完成品は「天気を使って、判断を助けるNotebook」。結果が目で分かること。',
            'Your goal: a notebook that helps someone make a weather-related decision, with a result they can see.', 'lesson-lead')
        + themes,
        steps(BUILD_STEPS)
        +c.p('配布の表示コードはそのまま使える。表を見せるだけでもよい。追加インストールは不要。',
             'The display code is supplied. A clear table is enough. No extra packages to install.'),
        c.list_html(SPEC['requirements']),
        c.p('1チーム60〜90秒。完成したNotebookをそのまま見せる。発表用スライドは不要。',
            '60–90 seconds per team. Present from the notebook. No separate slide deck needed.', 'lesson-lead')
        +steps(DEMO_GUIDE),
        c.p('urlopenでデータを受け取り、json.loadでPythonの辞書にする。柏の気温と降水確率を、24時間分。',
            'urlopen gets the response. json.load reads it into a Python dictionary. Request 24 hours of temperature and rain probability for Kashiwa.')
        +'<div class="api-example">'+shown_code(API_EXAMPLE,api_output)+'</div>'
        +source_line,
        c.p('同じ番号iで、時刻・気温・降水確率を組にする。forecastは辞書のリスト。',
            'Use the same index i to pair the time, temperature and rain probability. forecast is a list of dictionaries.')
        +'<div class="api-example">'+shown_code(list_code,list_output)+'</div>'
        +c.p('time＝日本時間、temp＝°C、rain＝降水確率%。None（値なし）の時間は除く。',
             'time = Japan time; temp = °C; rain = probability %. Skip hours with missing values (None).'),
        c.p('min_tempを変えると、どの時間が選ばれる？これを自分たちの目的に合わせよう。',
            'Which hours will match if min_temp changes? Adapt this rule for your own user.')+demo
        +c.p('保存した実際の予報でPythonの処理をJavaScriptで再現。Notebookにはwhileの入力例もあります。',
             'JavaScript simulates the Python using the saved API response. The notebook also includes a while input example.', 'simulation-note'),
        c.list_html(GROUP_GUIDE)+c.p(*AI_GUIDE,'weather-ai-note'),
        c.p('2〜3人で集まろう。ZIPを解凍し、challenge-starter.ipynbの最初の2つのコードセルを実行。全員が予報を読めたら制作へ。',
            'Form groups of 2–3. Unzip the pack and run the first two code cells in challenge-starter.ipynb. Once everyone can load the forecast, start building.', 'lesson-lead')
        +timer('build',3600,'minutes')+c.links([rows[0],rows[1]],7,'lecture.html?slide=10')
        +c.links([('challenge.html','課題の手順・ヒント','Instructions and hints')]),
        c.p('14:25–14:45。全チームが実演。20分をチーム数で割り、1組60〜90秒を目安に調整。',
            '14:25–14:45. Every team demos. Divide 20 minutes among the teams, aiming for 60–90 seconds each.', 'lesson-lead')
        +timer('presentation',90,'seconds')+c.p('目的を一文。表示を見せる。条件を変える。コードを一行説明。全員が一言。',
                                              'State the purpose. Show the visual. Change a setting. Explain one line. Everyone speaks.'),
        c.p(*SPEC['homework'],'lesson-lead')
        +c.p('締切：2026年11月18日（水）23:59 JST。提出作品はクラスギャラリーへ。',
             'Due: Wednesday, November 18, 2026, 23:59 JST. Submitted projects go to the class gallery.')
        +c.links([('challenge.html','課題・提出方法','Assignment / submission')]),
    ]
    layouts = ['hero','question','plain','requirements','plain','api','api','interactive','pair','timer','presentation','exit']
    assert len(SPEC['slides']) == len(bodies) == len(layouts)
    sections = []
    for i,((ja,en),body,layout) in enumerate(zip(SPEC['slides'],bodies,layouts),1):
        sections.append(f'<section class="slide lesson-slide layout-{layout}" data-slide data-slide-number="{i}" data-ink-id="w7-weather-{i}" hidden><p class="slide-kicker">WEEK 07 · WEATHER HACKATHON</p><h{1 if i==1 else 2}>'+c.bi(ja,en)+f'</h{1 if i==1 else 2}>'+body+'</section>')
    release = SPEC['date']+'T12:00:00+09:00'
    head = c.page_head('Week 07 · Weather Hackathon','course-decks.css','course-decks.js',VERSION)
    head += f'<link rel="stylesheet" href="hackathon.css?v={VERSION}"><script src="hackathon.js?v={VERSION}" defer></script><link rel="stylesheet" href="../../assets/slide-annotations.css"><script src="../../assets/slide-annotations.js" defer></script><script src="../../assets/slide-swipe.js" defer></script></head>'
    payload = json.dumps(dict(weather=forecast,weatherSource=source),ensure_ascii=False).replace('</','<\\/')
    shell = f'<body class="lecture-page course-deck weather-hackathon" data-week="7" data-release="{release}"><header class="lecture-header"><a id="lecture-return" href="../../agenda.html?open=07#week-07">← '+c.bi('授業予定','Agenda')+'</a><span class="lecture-mark">PRG / 26–2</span><button id="language-toggle" class="language-toggle" type="button">EN</button></header><main><div id="slides-view" class="view"><nav class="slide-controls" aria-label="Slide navigation"><div class="slide-nav-group"><button id="previous-slide" type="button">← '+c.bi('前へ','Previous')+'</button><span id="slide-count" aria-live="polite"></span><button id="next-slide" type="button">'+c.bi('次へ','Next')+' →</button></div><button id="slide-fullscreen" type="button" class="slide-fullscreen" aria-pressed="false">⛶</button></nav><div class="slide-stage">'+''.join(sections)+'</div></div></main><script type="application/json" id="lesson-data">'+payload+'</script></body></html>'
    c.write(folder/'lecture.html',head+shell)

    intro = '# Week 07 · 天気ハッカソン / Weather Hackathon\n\nチーム全員の氏名 / Team members：\n自分の担当 / My contribution：\n\n'+SPEC['brief'][0]+'\n\n'+SPEC['brief'][1]
    setup = '## 1. 予報を読み込む / Load the forecast\n\n最初の2つのコードセルは準備用。そのまま実行。追加インストール・APIキーは不要。接続できなければ、同じフォルダのweather-response.jsonを使用。取得成功時はこのファイルを更新します。\n\nRun the first two code cells as provided. No extra packages or API key. Keep weather-response.json beside this notebook as a fallback. A successful request updates that file.\n\nSource: https://open-meteo.com/en/docs\nTime: Asia/Tokyo; temp: °C; rain: precipitation probability (%).'
    provided = c.codecell(VISUAL_SETUP)
    provided['metadata'] = {'tags':['provided-display'],'jupyter':{'source_hidden':True}}
    visual = c.codecell(VISUAL_CALL)
    visual['metadata'] = {'tags':['notebook-display']}
    interaction = c.codecell(WHILE_CODE)
    interaction['metadata'] = {'tags':['interactive']}
    group_md = '## グループの進め方 / Good group work\n\n'+ '\n'.join('- '+ja+'\n  '+en for ja,en in GROUP_GUIDE)+'\n\n'+AI_GUIDE[0]+'\n\n'+AI_GUIDE[1]
    starter = [c.mdcell(intro),c.mdcell(setup),c.codecell(LIVE_LOAD),
        c.mdcell('## 2. 辞書のリストへ / A list of dictionaries\n\n同じ番号iで時刻・気温・降水確率を組にしてforecastを作る。None（値なし）の時間は除きます。この準備セルもそのまま実行。\n\nPair time, temperature and rain probability at index i. Skip missing values. Run this setup cell as provided.'),c.codecell(NORMALIZE),
        c.mdcell('## 3. 条件を、自分たちの目的へ / Make the rule your own\n\n使う人 / Our user：\n助ける判断 / Our question：\n\nまず実行。次に、max_rain（降水確率の上限%）やmin_temp（最低気温°C）、ifの条件を変えよう。\n\nRun it, then adapt the values and condition to your user. Write a Markdown explanation of the rule.'),c.codecell(FILTER_CODE),
        c.mdcell('## 4. 結果を見せる / Show your result\n\n次の表示コードは配布用。そのまま実行してよい。関数の中身は今日の課題ではありません。\nThe display helper is provided. Run it unchanged. Defining the helper is not part of today’s task.'),provided,visual,
        c.mdcell('緑の行は、あなたのfor・ifが選んだ時間。条件を変え、条件セルと表示セルをもう一度実行しよう。表の代わりにグラフや地図を作ってもよい。\n\nGreen rows show the hours selected by your code. Change a rule and rerun both the filter and display. You can use a chart or map instead.'),
        c.mdcell('## 5. 繰り返し使う / Let the user try again\n\nshowで表示、warmerで最低気温を1°C上げて再表示、quitで終了。入力待ちの間は実行中です。設定を変えて結果が変わるか確かめ、使う人に合う操作へ変えよう。\n\nshow displays results, warmer raises the minimum temperature by 1°C, quit ends the loop. Adapt the commands for your user.'),interaction,
        c.mdcell('## 6. 確認と説明 / Check and explain\n\n設定1 / Setting 1：\n予想と実際の結果 / Prediction and result：\n\n設定2 / Setting 2：\n予想と実際の結果 / Prediction and result：\n\n条件に合う時間がない場合も試す（例：min_temp = 50）。quitで終了できるか確認。\nTry a no-match case too. Check that quit finishes.\n\n結果に基づく提案 / Our recommendation：\n\n## 出典と日付 / Source and dates\nOpen-Meteo: https://open-meteo.com/\nAPI取得か保存JSONか、取得日時・予報の日付を記す。保存データを今の予報とは呼ばない。\nState whether you used live API or saved data, its retrieval time and forecast dates.'),
        c.mdcell(group_md),
        c.mdcell('## 発表 / Demo\n\n60〜90秒。使う人と目的、視覚表示、条件を変えた結果を見せ、for・if・whileの一行を説明。全員が一言話す。別の発表スライドは不要。\n\nShow the visual, change a setting and explain a line of code. Everyone speaks briefly. Present from the notebook.\n\n## AIを使った場合 / If you used AI\n何を相談し、どの結果を自分で確かめた？使わなかった場合は「使っていない」。\nBriefly note the help you used and what you checked yourself.\n\n## 宿題 / Homework\n'+SPEC['homework'][0]+'\n\n'+SPEC['homework'][1]+'\n\n締切 / Due：2026-11-18 23:59 JST\n\n途中でも、自分で書いたコードと試した変更を残して提出する。\nIf unfinished, submit the code you wrote and explain what you tried.')]
    c.notebook(folder/'challenge-starter.ipynb',starter)
    worked = [c.mdcell('# 実行例 / Worked examples\n\n'+snapshot_note+'\n\n保存した実際の予報でコードを確認します。APIから取得するにはchallenge-starter.ipynbへ。\nUses the saved API response. Open challenge-starter.ipynb to fetch a fresh forecast.'),c.codecell(CACHE_LOAD),c.codecell(NORMALIZE),c.codecell('print(forecast[0])'),c.codecell(VISUAL_SETUP),c.codecell(FILTER_CODE),c.codecell(VISUAL_CALL),c.mdcell('## whileで試す / Interactive example\nshow / warmer / quit。終わるにはquit。'),c.codecell(WHILE_CODE)]
    worked[4]['metadata'] = provided['metadata']
    worked[6]['metadata'] = visual['metadata']
    worked[-1]['metadata'] = interaction['metadata']
    run_scope = {}; count = 0
    for cell in worked:
        if cell['cell_type'] != 'code' or 'interactive' in cell['metadata'].get('tags',[]):
            continue
        output = io.StringIO(); count += 1; rendered = []
        if 'notebook-display' in cell['metadata'].get('tags',[]):
            run_scope.update(HTML=lambda value:value,display=rendered.append)
        source_code = cell['source'].replace('from IPython.display import HTML, display\n','')
        with contextlib.chdir(folder),contextlib.redirect_stdout(output):
            exec(source_code,run_scope)
        if rendered:
            cell['outputs'] = [dict(output_type='display_data',data={'text/html':rendered[-1],'text/plain':'Weather forecast board'},metadata={})]
        if output.getvalue():
            cell['outputs'] = [dict(output_type='stream',name='stdout',text=output.getvalue())]
        cell['execution_count'] = count
    c.notebook(folder/'practice.ipynb',worked)

    def heading(ja,en): return '<h2>'+c.bi(ja,en)+'</h2>'
    hints = '<details class="weather-hints"><summary>'+c.bi('困ったときのヒント','Hints if you get stuck')+'</summary>'+c.list_html([
        ('通信エラー：ZIPの中身を同じフォルダに置き、保存JSONで続ける。','Connection error: keep the unzipped files together and use the saved JSON.'),
        ('結果が0件：条件を少し緩める。0件という結果も伝えよう。','No matches: relax a condition and explain when nothing matches.'),
        ('入力セルが終わらない：quitと入力する。','Input cell still running: enter quit.'),
        ('最初は値を一つだけ変える。条件と結果のつながりを説明しよう。','Change one value first and explain how it affects the result.'),
    ])+'</details>'
    body = c.p(*SPEC['brief'],'lesson-lead')
    body += heading('完成品・必要なもの','Final deliverable and requirements')+c.list_html(SPEC['requirements'])
    body += heading('今日の流れ','Today’s plan')+c.p(*SPEC['flow'])
    body += heading('作り方・教材','How to build / files')+steps(BUILD_STEPS)
    body += c.p('ZIPを解凍し、challenge-starter.ipynbの最初の2つのコードセルを実行。追加インストール・pandas・APIキーは不要。表示コードはそのまま使える。',
                'Unzip the pack and run the first two code cells in challenge-starter.ipynb. No extra packages, pandas or API key. Use the supplied display helper.')+files+source_line
    body += heading('アイデア','Ideas')+themes
    body += heading('グループの進め方','Good group work')+c.list_html(GROUP_GUIDE)+c.p(*AI_GUIDE)
    body += hints+heading('最後に、全チームが実演','Every team demos at the end')
    body += c.p('14:25から20分。1組60〜90秒を目安に調整。Notebookをそのまま見せる。別の発表スライドは不要。',
                'Twenty minutes from 14:25. Aim for 60–90 seconds per team, adjusted to the number of teams. Present from the notebook, with no separate slides.')+steps(DEMO_GUIDE)
    body += heading('宿題・提出','Homework / submission')+c.p(*SPEC['homework'])
    body += c.p('締切：2026年11月18日（水）23:59 JST。作品はクラスギャラリーへ。途中でも、自分で書いたコードと試したことを残して提出。',
                'Due: Wednesday, November 18, 2026, 23:59 JST. Work goes to the class gallery. If unfinished, submit your code and explain what you tried.')
    body += c.links([('lecture.html','講義・制作タイマー','Briefing and build timer')])
    body = body.replace('href="starter-files.zip" download','href="starter-files.zip" download="week-07-weather-starter.zip"')
    c.write(folder/'challenge.html',c.page_head('Week 07 · Weather Hackathon','course-pages.css','course-page.js',VERSION)+f'<link rel="stylesheet" href="hackathon.css?v={VERSION}"></head><body class="course-challenge weather-hackathon" data-release="{release}"><header class="lecture-header"><a href="../../agenda.html?open=07#week-07">← '+c.bi('授業予定','Agenda')+'</a><span class="lecture-mark">WEEK 07</span><button id="language-toggle" class="language-toggle" type="button">EN</button></header><main id="course-page" hidden><p class="slide-kicker">'+c.bi('授業内ハッカソン＋宿題','In-class hackathon + homework')+'</p><h1>'+c.bi(SPEC['title_ja'],SPEC['title'])+'</h1>'+body+'</main></body></html>')

    old = (root/'content/weeks/07-logic-loops.md').read_text(); front = old.split('---',2)[1]
    updates = dict(title=SPEC['title'],title_ja=SPEC['title_ja'],overview=SPEC['aim'][1],overview_ja=SPEC['aim'][0],homework_title='Improve your weather tool',homework_title_ja='天気の道具を改善する',challenge_title='60-min hackathon',challenge_title_ja='60分ハッカソン')
    front = re.sub(r'^practice_mix(?:_ja)?:.*\n','',front,flags=re.M)
    for key,value in updates.items():
        if re.search(r'^'+key+':',front,re.M):
            front = re.sub(r'^'+key+r':.*$',key+': '+value,front,flags=re.M)
        else:
            front = front.rstrip()+'\n'+key+': '+value+'\n'
    text = '---'+front+'---\n'
    panels = [('Lecture Flow',SPEC['flow']),('In-Class Notebook',('最初の2つのコードセルで予報を準備。APIが使えなくても保存JSONで全員スタートできる。','Run the first two code cells to load the forecast. The saved JSON lets everyone start if the API is unavailable.')),
              ('In-Class Challenge',(SPEC['brief'][0]+' [手順と教材](weeks/week-07/challenge.html)。',SPEC['brief'][1]+' [Instructions and files](weeks/week-07/challenge.html).')),
              ('Student Work',('最後の20分で全チームが実演。全員が一言話し、コードと結果を説明する。','Every team demos at the end. Everyone speaks briefly and explains the code and results.')),
              ('Take-Home Assignment',SPEC['homework']),('Aha!',SPEC['aim']),('Takeaway',('APIのデータを、自分の条件と繰り返しで使える道具にする。','Turn API data into a tool using your own rules and a repeating interaction.'))]
    for name,(ja,en) in panels:
        text += f'## {name}\nEN: {en}\nJP: {ja}\n'
    text += '## Resources\n- [Weather Hackathon — Briefing & Timers](weeks/week-07/lecture.html) {lecture}\n- [制作を始めるNotebook / Start-building notebook](weeks/week-07/challenge-starter.ipynb) {notebook}\n- [コードの実行例 / Worked examples](weeks/week-07/practice.ipynb) {fundamentals}\n- [ハッカソンの手順 / Hackathon instructions](weeks/week-07/challenge.html) {challenge}\n- [宿題・提出方法 / Homework and submission](weeks/week-07/challenge.html) {homework}\n- [天気予報JSON / Forecast JSON](weeks/week-07/weather-response.json) {data}\n'
    c.write(root/'content/weeks/07-logic-loops.md',text)
    c.write(folder/'README.txt','Weather Hackathon · Week 07\n\nUnzip these files into one folder. Open challenge-starter.ipynb and run the first two code cells. Only Python standard-library modules are used for fetching and processing data.\n\nLive API first; weather-response.json is the fallback and is updated when fetching succeeds. The data preview shows this JSON as a table. practice.ipynb uses the bundled snapshot. The visual display uses the notebook’s built-in IPython support.\n\nWeather data: Open-Meteo https://open-meteo.com/\n'+snapshot_note+'\nUnits: temp °C; rain probability %.\n\nBuild in teams of 2–3 for 60 minutes. Share coding, checking and visual explanation. Everyone contributes a code change and understands it. AI may explain errors or offer small hints; check its suggestions yourselves. Every team demos and every member speaks.\n\nEach student submits an executed notebook and the JSON used. Include your contribution, one improvement and two tested settings. Due 2026-11-18 23:59 JST.\n')
