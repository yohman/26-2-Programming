"""Week 7 weather hackathon, using the established course presentation shell."""
from pathlib import Path
from urllib.parse import urlencode
import contextlib
import html
import io
import json
import re
from datetime import datetime, timedelta, timezone

VERSION = '20261111-visual'
API_URL = 'https://api.open-meteo.com/v1/forecast?' + urlencode({
    'latitude': 35.86, 'longitude': 139.97,
    'hourly': 'temperature_2m,precipitation_probability',
    'forecast_hours': 24, 'timezone': 'Asia/Tokyo',
})

LIVE_LOAD = '''import json
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime, timezone

latitude = 35.86
longitude = 139.97
url = "https://api.open-meteo.com/v1/forecast?" + urlencode({
    "latitude": latitude, "longitude": longitude,
    "hourly": "temperature_2m,precipitation_probability",
    "forecast_hours": 24, "timezone": "Asia/Tokyo"
})

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
    brief=('天気予報を使って、誰かの「いつ・どうする？」に視覚的に答えるNotebookを作ろう。2〜3人で作り、最後に全チームが実演する。',
           'Build a working weather-assistant notebook with a visual answer to a user’s question. Work in teams of 2–3; every team gives a short demo at the end.'),
    flow=('13:10 説明10分 → 13:20 準備5分 → 13:25 自力10分・チーム制作35分・自力15分 → 14:25 発表20分 → 14:45 保存・まとめ5分。',
          '13:10 briefing 10 min → 13:20 setup 5 min → 13:25 solo 10 / team build 35 / solo 15 min → 14:25 demos 20 min → 14:45 save and wrap up 5 min.'),
    requirements=[
        ('誰が、何を決めるための道具かをMarkdownで一文書く。', 'Name the user and the decision your tool helps them make.'),
        ('forとifで予報を調べ、自分たちの条件で役立つ結果を出す。', 'Use for and if to process the forecast with your own useful rule.'),
        ('選んだ時間が分かる視覚表示を一つ作る。条件を変えると表示も変わること。結果からの提案を一文添える。', 'Include one visual display that changes with your rule: a highlighted forecast table, chart or map. Add a one-sentence recommendation based on it.'),
        ('whileで繰り返し使え、quitで終了できるようにする。', 'Use while so the user can try again and enter quit to finish.'),
        ('条件を2通り試し、結果の違いと使ったデータを説明する。', 'Test two settings and explain the results and the data you used.'),
        ('各自がAIなしのチェックA・Bを書き、実演で自分のコードを説明する。', 'Each person completes solo checks A and B without AI and explains their own code during the demo.'),
    ],
    homework=('発表でもらった意見を使い、同じ道具を一つ改善する。各自のNotebookにチーム全員の氏名、自分の担当、改善点と確認2件を書く。自力チェックA・Bの元のコードを残し、改善を追記する。実行済み.ipynbとweather-response.jsonをUNIPAへ提出。',
              'Improve the same tool using demo feedback. Each student submits a notebook naming the team, their contribution, one improvement and two checks. Keep the original solo-check code and add revisions below it. Submit the executed .ipynb and weather-response.json to UNIPA.'),
    slides=[('天気ハッカソン', 'Weather Hackathon'),
            ('自分で書く時間をつくる', 'Show what you can code yourself'),
            ('まず、予報を読み込む', 'Get the forecast running'),
            ('条件を変えて、試す', 'Change a rule and try it'),
            ('繰り返し使える道具に', 'Let the user try again'),
            ('60分、作ろう', 'Build time'),
            ('全チーム、実演', 'Every team gives a demo'),
            ('保存して、次につなぐ', 'Save it and improve it')],
)


def build(root, c):
    folder = root / 'weeks/week-07'
    data = json.loads((folder/'weather-response.json').read_text())
    source = json.loads((folder/'weather-source.json').read_text())
    scope = {'data': data}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(NORMALIZE, scope, scope)
    forecast = scope['forecast']
    retrieved=datetime.fromisoformat(source['retrieved_at']).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M JST')
    snapshot_note = f'Kashiwa · {retrieved} · Asia/Tokyo · Open-Meteo'
    rows = [('starter-files.zip', '教材をまとめてダウンロード', 'Download the starter pack'),
            ('challenge-starter.ipynb', '制作を始めるNotebook', 'Start-building notebook'),
            ('practice.ipynb', 'コードの実行例', 'Worked examples'),
            ('weather-response.json', '予報JSON（表でプレビュー）', 'Forecast JSON (table preview)')]
    files = c.links(rows, 7)
    source_line = c.p('天気データ：<a href="https://open-meteo.com/">Open-Meteo</a>。保存予報の取得：'+html.escape(retrieved)+'。予報も日本時間。',
                      'Weather data: <a href="https://open-meteo.com/">Open-Meteo</a>. Saved forecast retrieved '+html.escape(retrieved)+'. Forecast times are Japan time.', 'weather-source')
    def timer(key, seconds, unit):
        value=seconds/60 if unit=='minutes' else seconds
        return f'''<div class="hackathon-clock" data-countdown="{key}" data-seconds="{seconds}" data-unit="{unit}">
<output role="timer" aria-live="off" data-clock>00:00</output>
<div class="clock-controls"><button type="button" data-clock-toggle aria-label="Start / 開始" aria-pressed="false">▶</button><button type="button" data-clock-reset aria-label="Reset / リセット">↺</button><label>{c.bi('時間','Time')} <input data-clock-duration type="number" min="1" max="{180 if unit=='minutes' else 600}" value="{value:g}" step="1"> {c.bi('分','min') if unit=='minutes' else c.bi('秒','sec')}</label><span data-clock-status role="status"></span></div></div>'''
    themes = c.list_html([
        ('自転車で帰る人：雨の確率が低い時間を探す。', 'Someone cycling home: find hours with a low chance of rain.'),
        ('サークル：雨と気温から、外で活動したい時間を選ぶ。', 'A club: find hours that match its preferences for rain and temperature.'),
        ('自分：自分で決めた条件に合う時間を探す。', 'You: search for hours that match a rule you choose.'),
    ])
    rain_example = c.p('max_rainは降水確率の上限（%）、min_tempは気温の下限（°C）。入力を変え、結果を予想して実行。',
                       'max_rain is the rain-probability limit (%); min_temp is the minimum temperature (°C). Change a value, predict, then run.')
    demo = '''<div data-weather-demo><div class="weather-inputs"><label>max_rain (%) <input data-rain type="number" min="0" max="100" value="30" required></label><label>min_temp (°C) <input data-temp type="number" min="-40" max="50" step="0.5" value="10" required></label><button data-weather-run type="button">▶ '''+c.bi('実行','Run')+'''</button></div><pre data-language="python"><code data-weather-code></code></pre><div data-weather-board aria-live="polite"></div><details><summary>Text output / テキスト出力</summary><pre class="lesson-output" data-weather-output></pre></details></div>'''
    first = c.code_html('print(forecast[0])', repr(forecast[0])+'\n')
    bodies = [
        c.p('天気を使う道具を作り、結果を見える形に。2〜3人のチームで、最後に動くところを見せよう。',
            'Build a weather assistant with a visual result. Teams of 2–3; finish by showing it working.', 'lesson-lead')
        + '<p class="hackathon-plan">'+c.bi('説明10分 / 準備5分 / 制作60分 / 発表20分 / まとめ5分', 'Brief 10 / Setup 5 / Build 60 / Demos 20 / Wrap up 5')+'</p>',
        c.list_html([('最初の10分：各自で予想し、for＋ifを書く。AI・相談なし。','First 10 minutes: predict and write your own for + if. No AI or teammate help.'),
                     ('次の35分：チームで制作。AIはエラーの説明・小さな提案・表示の整形に使える。','Next 35 minutes: build as a team. AI may explain errors, suggest small changes or help style the display.'),
                     ('最後の15分：その場で出る変更を各自で書き、確かめる。AI・相談なし。','Last 15 minutes: each person codes and checks a change announced in class. No AI or teammate help.')])
        +c.p('自力チェック中はAIコード補完も止める。授業資料・自分のメモ・通常の構文補完は使える。',
             'For solo checks, turn off AI code completion too. Course materials, your notes and ordinary syntax completion are allowed.'),
        c.p('ZIPを解凍し、challenge-starter.ipynbを開く。最初の2つのコードセルを実行。パッケージの追加は不要。',
            'Unzip the pack, open challenge-starter.ipynb, and run the first two code cells. No extra packages to install.', 'lesson-lead')
        +c.links([rows[0], rows[1]],7,'lecture.html?slide=3')+first
        +c.p('time＝日本時間、temp＝気温°C、rain＝降水確率%。APIに接続できなければ同じJSONファイルから続ける。',
             'time = Japan time; temp = °C; rain = probability %. If the API is unreachable, the notebook uses the saved JSON.')
        +source_line,
        rain_example+demo+c.p('表示は保存した実際の予報を使用。Pythonの処理をJavaScriptで再現。',
                              'The demo uses the actual saved forecast. JavaScript simulates the Python logic.', 'simulation-note'),
        c.p('showで結果を表示し、quitで終わる。スターターのwarmerは気温の下限を1°C上げる。自分たちの使い方に変えよう。',
            'show displays results; quit finishes. The starter’s warmer command raises the minimum by 1°C. Adapt the interaction for your user.', 'lesson-lead')
        +c.code_html(WHILE_BRIEF)+c.p('完成条件：自分たちの目的 / for＋if＋while / 視覚表示 / 条件2通りの確認 / 結果の説明。',
                                     'Finish with: your own purpose / for + if + while / a visual / two tested settings / an explanation of the result.'),
        c.p('13:25–14:25。まず動くものを一つ。その後、使う人に合わせて改善しよう。',
            '13:25–14:25. Get one version working, then improve it for your user.', 'lesson-lead')
        +timer('build',3600,'minutes')
        +'<p class="build-phase" data-build-phase></p>'
        +c.p('自力10分 → チーム35分（役割交代10分×3＋統合5分）→ 自力15分。',
             'Solo 10 → team 35 (three 10-min role rotations + 5-min integration) → solo 15.')
        +'<button class="solo-reveal" data-solo-reveal type="button">'+c.bi('教員：変更課題を出す','Instructor: reveal a change')+'</button><p data-solo-prompt hidden></p>'
        +c.links([('challenge.html','手順・ヒントを開く','Open instructions and hints')]),
        c.p('14:25–14:45。全チームが実演。持ち時間は20分÷チーム数で調整（目安60〜90秒）。',
            '14:25–14:45. Every team demos. Divide 20 minutes among the teams; aim for 60–90 seconds each.', 'lesson-lead')
        +timer('presentation',90,'seconds')
        +c.list_html([('誰の何を助ける表示かを話し、条件を変えて見せる。','Show the visual and explain whose decision it helps.'),
                      ('全員が、自分で書いた行と変更の理由を説明する。','Every member explains a line they wrote and why they changed it.'),
                      ('教員が説明する順番・確認する行を指定する。AIは閉じる。','The instructor chooses the speaking order and a line to check. Close AI tools.')]),
        c.p(*SPEC['homework'], 'lesson-lead')
        +c.p('締切：2026年11月18日（水）23:59 JST。提出作品はクラスギャラリーへ。',
             'Due: Wednesday, November 18, 2026, 23:59 JST. Submitted projects go to the class gallery.')
        +c.links([('challenge.html','課題・提出方法','Assignment / submission')]),
    ]
    layouts=['hero','plain','setup','interactive','code','timer','presentation','exit']
    sections=[]
    for i,((ja,en),body,layout) in enumerate(zip(SPEC['slides'],bodies,layouts),1):
        sections.append(f'<section class="slide lesson-slide layout-{layout}" data-slide data-slide-number="{i}" data-ink-id="w7-weather-{i}" hidden><p class="slide-kicker">WEEK 07 · WEATHER HACKATHON</p><h{1 if i==1 else 2}>'+c.bi(ja,en)+f'</h{1 if i==1 else 2}>'+body+'</section>')
    release=SPEC['date']+'T12:00:00+09:00'
    head=c.page_head('Week 07 · Weather Hackathon','course-decks.css','course-decks.js',VERSION)
    head+=f'<link rel="stylesheet" href="hackathon.css?v={VERSION}"><script src="hackathon.js?v={VERSION}" defer></script><link rel="stylesheet" href="../../assets/slide-annotations.css"><script src="../../assets/slide-annotations.js" defer></script><script src="../../assets/slide-swipe.js" defer></script></head>'
    payload=json.dumps(dict(weather=forecast,weatherSource=source),ensure_ascii=False).replace('</','<\\/')
    shell=f'<body class="lecture-page course-deck weather-hackathon" data-week="7" data-release="{release}"><header class="lecture-header"><a id="lecture-return" href="../../agenda.html?open=07#week-07">← '+c.bi('授業予定','Agenda')+'</a><span class="lecture-mark">PRG / 26–2</span><button id="language-toggle" class="language-toggle" type="button">EN</button></header><main><div id="slides-view" class="view"><nav class="slide-controls" aria-label="Slide navigation"><div class="slide-nav-group"><button id="previous-slide" type="button">← '+c.bi('前へ','Previous')+'</button><span id="slide-count" aria-live="polite"></span><button id="next-slide" type="button">'+c.bi('次へ','Next')+' →</button></div><button id="slide-fullscreen" type="button" class="slide-fullscreen" aria-pressed="false">⛶</button></nav><div class="slide-stage">'+''.join(sections)+'</div></div></main><script type="application/json" id="lesson-data">'+payload+'</script></body></html>'
    c.write(folder/'lecture.html',head+shell)

    intro='# Week 07 · 天気ハッカソン / Weather Hackathon\n\nチーム全員の氏名：\n自分の担当：\n\n'+SPEC['brief'][0]+'\n\n'+SPEC['brief'][1]
    setup='## 1. 予報を読み込む / Load the forecast\n\n最初の2つのコードセルは準備用。そのまま実行できます。追加インストール・APIキーは不要です。ネット接続に失敗したら、同じフォルダのweather-response.jsonを使います。取得成功時はこのファイルを更新するので、提出するデータと結果をそろえられます。\n\nLive API first; the saved JSON is the fallback. Keep the JSON beside this notebook. A successful fetch updates that same file.\n\nSource: https://open-meteo.com/en/docs\nTime: Asia/Tokyo; temp: °C; rain: precipitation probability (%).'
    starter=[c.mdcell(intro),c.mdcell(setup),c.codecell(LIVE_LOAD),
             c.mdcell('## 2. 辞書のリストへ / A list of dictionaries\n\ntime・temp・rainの3つの値を持つリストforecastを作ります。この準備セルもそのまま実行。'),c.codecell(NORMALIZE),
             c.mdcell('## 3. 条件を、自分たちの目的へ / Make the rule your own\n\nまず実行。次に、誰の何を助けるかを一文書き、max_rainやmin_temp、ifの条件、表示内容を変えよう。30は30％、10は10°C。値は自分たちの基準です。\n\nOur user / 使う人：\nOur question / 助ける判断：'),c.codecell(FILTER_CODE),
             c.mdcell('## 4. 繰り返し使う / Let the user try again\n\nshowで表示、warmerで最低気温を1°C上げて再表示、quitで終了。入力待ちの間はセルが実行中です。終わるにはquit。設定を変えると結果が変わるか確かめ、使う人に合う操作へ変えよう。'),c.codecell(WHILE_CODE),
             c.mdcell('## 5. 2通り試す / Two checks\n\n設定1 → 予想 → 実際の結果：\n設定2 → 予想 → 実際の結果：\n\n条件に合う時間がない場合も試す（例：min_temp = 50）。quitで終了できるか確認。\n\n## 発表 / Demo\n1. 誰の何を助ける？\n2. 条件を変えて動くところを見せる。\n3. ifかwhileの一行を説明する。\n\n## 宿題 / Homework\n'+SPEC['homework'][0]+'\n\n締切：2026-11-18 23:59 JST\n\n## 出典・データ / Source and data\nOpen-Meteo: https://open-meteo.com/\nAPI取得か保存JSONか、取得日時・予報の日付を記す。保存データを今の予報とは呼ばない。\n\n## AIを使った場合 / If you used AI\n何に使い、どの結果を自分で確認した？')]
    for cell in starter:
        if cell['cell_type']=='code' and cell['source']==WHILE_CODE:cell['metadata']={'tags':['interactive']}
    starter[1:1]=[c.mdcell('## AIの使い方 / Working with AI\n\n自力チェックA・Bは各自で、AIチャット・AI補完・他人の入力なし。授業資料、自分のメモ、Python公式文書、通常の構文補完は使えます。制作の時間は、エラーの説明・調べ方・小さな提案にAIを使えます。自分で書いた条件とループを、AIやエージェントに一括で置き換えさせない。\n\nSolo checks A and B: work individually without AI chat, AI completion or someone else typing. Course materials, your notes, official Python docs and ordinary syntax completion are allowed. During team building, AI may help explain errors or suggest a small change. Keep and understand the conditions and loops you write yourself.\n\n各自でNotebookを保存。チームの完成品だけでなく、自分のチェックと説明を残します。')]
    position=next(i for i,cell in enumerate(starter) if cell['cell_type']=='markdown' and cell['source'].startswith('## 3.'))
    check_a=c.codecell('# AIなしで、自分のforとifを書く。 / Write your own for and if.\n')
    check_a['metadata']={'tags':['solo-check'],'checkpoint':'A'}
    starter[position:position]=[c.mdcell('## 自力チェックA · 最初の10分 / Solo check A · first 10 minutes\n\n次の3件で、rainが30以下、tempが10以上のtimeを表示する。先に出力を予想してMarkdownに書き、次にforとifを自分で書いて確かめる。\n\n予想（実行前）／なぜ？：\n\nWrite your predicted output before running. Then write your own for and if; print time when rain <= 30 and temp >= 10.'),
        c.codecell('check_hours = [\n    {"time": "A", "temp": 10, "rain": 30},\n    {"time": "B", "temp": 9, "rain": 0},\n    {"time": "C", "temp": 18, "rain": 60}\n]'),check_a,
        c.mdcell('実際の結果／予想との違い／自分のifの説明：\n\nActual result / difference from prediction / explain your if:')]
    position=next(i for i,cell in enumerate(starter) if cell['cell_type']=='markdown' and cell['source'].startswith('## 5.'))
    check_b=c.codecell('# その場で指定された変更を、AIなしで書く。 / Code the announced change without AI.\n')
    check_b['metadata']={'tags':['solo-check'],'checkpoint':'B'}
    starter[position:position]=[c.mdcell('## 自力チェックB · 最後の15分 / Solo check B · last 15 minutes\n\n教員がその場で指定する条件へ変更し、合う時間数を数えて表示する。AI・相談なしで各自が書く。条件、予想、変更したコード、結果と理由を残す。\n\nAnnounced condition / 変更条件：\nPrediction / 予想：'),check_b,
        c.mdcell('Result / 結果：\nWhy / なぜ？：\nThe line I changed / 自分で変えた行：')]
    starter.append(c.mdcell('## AIメモ / AI note\n\n使わなかった場合は「使っていない」。使った場合は短く記録：\n- 相談したこと：\n- 採用・修正した小さな提案：\n- 自分で確かめた入力と結果：\n\nIf you did not use AI, say so. Otherwise name the help, the small suggestion you used or changed, and a result you checked yourself.\n\n## 自分が示すもの / My evidence\n自力チェックA・B、自分で書いた条件とループ、発表で説明する一行。まだ動かなくても、自分で書いた部分と試した変更を残して提出する。\n\nKeep your own two checks, the condition and loop you wrote, and a line you can explain in the demo. If unfinished, submit your own attempt and the changes you tried.'))
    position=next(i for i,cell in enumerate(starter) if cell['cell_type']=='code' and cell['source']==FILTER_CODE)
    provided=c.codecell(VISUAL_SETUP);provided['metadata']={'tags':['provided-display'],'jupyter':{'source_hidden':True}}
    starter[position:position]=[c.mdcell('### 表示用コード（配布） / Provided display code\nこのセルはそのまま実行してよい。表示する内容を選ぶfor・ifと、繰り返すwhileは自分で書き、説明する。表示コードの作成は今日の評価対象ではありません。\nThe display helper is supplied. Your own filtering loop, condition and repeating interaction are what you must understand.'),provided]
    position=next(i for i,cell in enumerate(starter) if cell['cell_type']=='code' and cell['source']==FILTER_CODE)+1
    visual=c.codecell(VISUAL_CALL);visual['metadata']={'tags':['notebook-display']}
    starter[position:position]=[c.mdcell('### 結果を見せる / Show your result\n緑の行が、自分たちの条件で選んだ時間。min_tempやmax_rainを変え、上の条件セルとこのセルを再実行して表示を比べよう。別のグラフや地図にしてもよい。\nGreen rows show the hours selected by your Python code. Change a setting, rerun your filter and this cell, and compare the visual.'),visual]
    starter.append(c.mdcell('## 3人チームの進め方 / Three-person team\n\n最初にA・B・Cへ名前を割り当てる。チーム制作35分：10分×3回、最後の5分で統合。毎回、役割を交代する。\n\n| 役割 | すること |\n|---|---|\n| コーダー / Coder | Pythonの条件・ループを書き、操作する。 |\n| テスター / Tester | 実行前に予想し、通常・0件の条件で確かめる。 |\n| 表示・説明 / Visual editor | 表示のラベル・単位・分かりやすさを整え、使う人に伝わるか確認する。 |\n\n| 人 | 1回目 | 2回目 | 3回目 |\n|---|---|---|---|\n| A | コーダー | テスター | 表示・説明 |\n| B | テスター | 表示・説明 | コーダー |\n| C | 表示・説明 | コーダー | テスター |\n\n最後の5分で統合し、全員が実行。2人チームはテスターと表示を兼任して交代。自力チェックA・Bは各自で行う。\n\n発表90秒：1人目は目的と表示、2人目は条件変更とコード、3人目は確認結果を示す。全員が、教員の指定する自分の行を説明できるようにする。\n\nTeam build: rotate coder, tester and visual editor every 10 minutes, then integrate for 5 minutes. Every member takes every role. Solo checks stay individual. In the demo, share the user/visual, code change and testing across the three speakers.'))
    c.notebook(folder/'challenge-starter.ipynb',starter)
    worked=[c.mdcell('# 実行例 / Worked examples\n\n'+snapshot_note+'\n\nこのNotebookは保存済みの実際の予報でコードを確認します。今の予報を取得して制作するにはchallenge-starter.ipynbを開きます。'),c.codecell(CACHE_LOAD),c.codecell(NORMALIZE),c.codecell('print(forecast[0])'),c.codecell(FILTER_CODE),c.mdcell('## whileで試す / Interactive example\nshow、warmer、quitを入力。終わるにはquit。'),c.codecell(WHILE_CODE)]
    position=next(i for i,cell in enumerate(worked) if cell['cell_type']=='code' and cell['source']==FILTER_CODE)
    provided=c.codecell(VISUAL_SETUP);provided['metadata']={'tags':['provided-display'],'jupyter':{'source_hidden':True}}
    worked.insert(position,provided)
    visual=c.codecell(VISUAL_CALL);visual['metadata']={'tags':['notebook-display']}
    worked.insert(position+2,visual)
    worked[-1]['metadata']={'tags':['interactive']}
    run_scope={};count=0
    for cell in worked:
        if cell['cell_type']!='code' or 'interactive' in cell['metadata'].get('tags',[]):continue
        output=io.StringIO();count+=1
        rendered=[]
        if 'notebook-display' in cell['metadata'].get('tags',[]):
            run_scope['HTML']=lambda value:value
            run_scope['display']=rendered.append
        source_code=cell['source'].replace('from IPython.display import HTML, display\n','')
        with contextlib.chdir(folder),contextlib.redirect_stdout(output):exec(source_code,run_scope)
        if rendered:cell['outputs']=[dict(output_type='display_data',data={'text/html':rendered[-1],'text/plain':'Weather forecast board'},metadata={})]

        cell['execution_count']=count
        if output.getvalue():cell['outputs']=[dict(output_type='stream',name='stdout',text=output.getvalue())]
    c.notebook(folder/'practice.ipynb',worked)

    hints='<details class="weather-hints"><summary>'+c.bi('困ったときのヒント','Hints if you get stuck')+'</summary>'+c.list_html([
        ('通信エラー：ZIPの中身を同じフォルダに置き、保存JSONで続ける。','Connection error: keep the unzipped files together and use the saved JSON.'),
        ('結果が0件：条件を少し緩める。0件という結果も伝えよう。','No matches: relax a condition and explain when nothing matches.'),
        ('入力セルが終わらない：quitと入力する。','Input cell still running: enter quit.'),
        ('まず値を一つ変える。その後、気温と雨の条件を組み合わせる。','Change one value first; then combine rain and temperature conditions.'),
    ])+'</details>'
    ai_policy=c.list_html([('チェックA（10分）：各自が出力を予想し、forとifを書く。','Check A (10 min): each person predicts an output and writes for and if.'),
        ('制作（35分）：チームで作る。AIはエラーの説明・小さな提案・表示の整形に使える。相談内容と自分で確かめた結果を短く残す。','Build (35 min): work as a team. AI may explain errors or suggest a small change; briefly record its help and your own check.'),
        ('チェックB（15分）：その場で指定される条件へ各自が変更し、合う時間数を数える。','Check B (15 min): each person codes the newly announced condition and counts the matching hours.')])
    body=c.p(*SPEC['brief'])+'<h2>'+c.bi('今日の流れ','Today’s plan')+'</h2>'+c.p(*SPEC['flow'])+'<h2>'+c.bi('自分で書く時間・AIを使える時間','Solo coding and AI help')+'</h2>'+ai_policy+c.p('チェックA・Bは、AIチャット・AIコード補完・他人の入力なし。授業資料、自分のメモ、Python公式文書、通常の構文補完は使える。各自のNotebookに予想・自分のコード・結果を残す。チーム作品の完成だけでは、自力チェックの代わりにならない。','For checks A and B: no AI chat, AI code completion or someone else typing. Course materials, your notes, official Python docs and ordinary syntax completion are allowed. Each notebook keeps the prediction, the student’s own code and the result; the team’s finished tool does not replace these checks.')+'<h2>'+c.bi('始める','Get started')+'</h2>'+c.p('ZIPを解凍し、challenge-starter.ipynbを開く。最初の2つのコードセルを実行してforecastを作る。新しい空のNotebookにコードをコピーして始めてもよい。',
        'Unzip the pack and open challenge-starter.ipynb. Run the first two code cells to create forecast. You can also copy them into a new blank notebook.')+files+source_line+'<h2>'+c.bi('作るもの','Your build')+'</h2>'+themes+c.list_html(SPEC['requirements'])+c.p('追加インストール・pandas・APIキーは不要。操作する人を途中で交代し、全員がコードを一行説明できるように。','No extra installs, pandas or API keys. Swap the keyboard during the build; everyone explains one line.')+hints+'<h2>'+c.bi('最後に、全チームが実演','Every team demos at the end')+'</h2>'+c.p('14:25から20分。1組60〜90秒を目安に、チーム数で調整。まず動くところを見せ、全員が自分で書いた行を説明する。説明する順番と確認する行は教員が指定。AIは閉じる。別の発表スライドは不要。','Twenty minutes from 14:25. Allow roughly 60–90 seconds per team, adjusted to the team count. Show it working; every member explains a line they wrote. The instructor chooses the order and a line to check. Close AI tools. No separate presentation slides needed.')+'<h2>'+c.bi('確認すること','What you demonstrate')+'</h2>'+c.p('動くか／各自が条件とループを書き、変更できるか／結果を説明できるか。途中でも、自分で書いたコードと試した変更を残そう。','Does it run? Can each person write and change the condition and loop? Can they explain the result? If unfinished, keep your own code and the changes you tried.')+'<h2>'+c.bi('宿題・提出','Homework / submission')+'</h2>'+c.p(*SPEC['homework'])+c.p('締切：2026年11月18日（水）23:59 JST。作品はクラスギャラリーへ。AIを使った場合は、使った箇所と自分で確認した結果を書く。','Due: Wednesday, November 18, 2026, 23:59 JST. Work goes to the class gallery. If you used AI, name its contribution and a result you checked yourself.')+c.links([('lecture.html','講義・制作タイマー','Briefing and build timer')])
    deliverable='<h2>'+c.bi('完成品・提出物','Final deliverable')+'</h2>'+c.p('実行できる天気アシスタントNotebookを一つ。使う人と問い、APIデータ、自分たちのfor・if・while、条件に応じて変わる視覚表示、確認2件と短い説明を含める。各自の自力チェックA・BとAIメモも残す。.ipynbとweather-response.jsonを提出。','One working weather-assistant notebook containing the user and question, API data, your for/if/while, a visual that responds to the settings, two checks and a short explanation. Keep your individual solo checks and AI note. Submit the executed .ipynb and weather-response.json.')
    teamwork='<h2>'+c.bi('3人チームの進め方','Working as a team of three')+'</h2>'+c.p('制作35分は、10分×3回＋統合5分。コーダー（条件・ループを書く）、テスター（予想・動作確認）、表示・説明（ラベル・単位・見やすさ）を毎回交代。A：コード→テスト→表示、B：テスト→表示→コード、C：表示→コード→テスト。最後の5分で全員が実行し、発表を合わせる。2人チームは確認と表示を兼任して交代。','Use three 10-minute rounds plus 5 minutes to integrate. Rotate coder (write conditions and loops), tester (predict and check) and visual editor (labels, units and readability). A: code → test → visual; B: test → visual → code; C: visual → code → test. In the final 5 minutes, everyone runs it and prepares the demo. With two people, combine testing and visual editing and swap.')+c.p('90秒の発表は、目的と表示／条件変更とコード／確認結果を3人で分担。説明する行と順番は教員が指定するので、全員が自分のコードを理解しておく。','Share the 90-second demo across purpose/visual, code/settings and test results. The instructor may select a line and speaking order, so everyone understands their own code.')
    target='<h2>'+c.bi('今日の流れ','Today’s plan')+'</h2>'
    body=body.replace(target,deliverable+teamwork+target,1)
    body=body.replace('href="starter-files.zip" download','href="starter-files.zip" download="week-07-weather-starter.zip"')
    c.write(folder/'challenge.html',c.page_head('Week 07 · Weather Hackathon','course-pages.css','course-page.js',VERSION)+f'<link rel="stylesheet" href="hackathon.css?v={VERSION}"></head><body class="course-challenge weather-hackathon" data-release="{release}"><header class="lecture-header"><a href="../../agenda.html?open=07#week-07">← '+c.bi('授業予定','Agenda')+'</a><span class="lecture-mark">WEEK 07</span><button id="language-toggle" class="language-toggle" type="button">EN</button></header><main id="course-page" hidden><p class="slide-kicker">'+c.bi('授業内ハッカソン＋宿題','In-class hackathon + homework')+'</p><h1>'+c.bi(SPEC['title_ja'],SPEC['title'])+'</h1>'+body+'</main></body></html>')

    old=(root/'content/weeks/07-logic-loops.md').read_text();front=old.split('---',2)[1]
    updates=dict(title=SPEC['title'],title_ja=SPEC['title_ja'],overview=SPEC['aim'][1],overview_ja=SPEC['aim'][0],homework_title='Improve your weather tool',homework_title_ja='天気の道具を改善する',challenge_title='60-min hackathon',challenge_title_ja='60分ハッカソン')
    front=re.sub(r'^practice_mix(?:_ja)?:.*\n','',front,flags=re.M)
    for key,value in updates.items():
        if re.search(r'^'+key+':',front,re.M):front=re.sub(r'^'+key+r':.*$',key+': '+value,front,flags=re.M)
        else:front=front.rstrip()+'\n'+key+': '+value+'\n'
    text='---'+front+'---\n'
    sections=[('Lecture Flow',SPEC['flow']),('In-Class Notebook',('ZIPを解凍し、最初の2つのコードセルで予報を準備。APIが使えなくても保存JSONで全員スタートできる。','Unzip the pack and run the first two code cells. The saved JSON lets everyone start if the API is unavailable.')),
              ('In-Class Challenge',(SPEC['brief'][0]+' [手順と教材](weeks/week-07/challenge.html)。',SPEC['brief'][1]+' [Instructions and files](weeks/week-07/challenge.html).')),
              ('Student Work',('最後の20分で全チームが実演し、全員が自分で書いた行を説明する。','Every team demos at the end; every member explains a line they wrote.')),
              ('Take-Home Assignment',SPEC['homework']),('Aha!',SPEC['aim']),('Takeaway',('APIのデータを、自分の条件と繰り返しで使える道具にする。','Turn API data into a tool using your own rules and a repeating interaction.'))]
    for heading,(ja,en) in sections:text+=f'## {heading}\nEN: {en}\nJP: {ja}\n'
    text+='## Resources\n- [Weather Hackathon — Briefing & Timers](weeks/week-07/lecture.html) {lecture}\n- [制作を始めるNotebook / Start-building notebook](weeks/week-07/challenge-starter.ipynb) {notebook}\n- [コードの実行例 / Worked examples](weeks/week-07/practice.ipynb) {fundamentals}\n- [ハッカソンの手順 / Hackathon instructions](weeks/week-07/challenge.html) {challenge}\n- [宿題・提出方法 / Homework and submission](weeks/week-07/challenge.html) {homework}\n- [天気予報JSON / Forecast JSON](weeks/week-07/weather-response.json) {data}\n'
    c.write(root/'content/weeks/07-logic-loops.md',text)
    c.write(folder/'README.txt','Weather Hackathon · Week 07\n\nUnzip these files into one folder. Open challenge-starter.ipynb and run the first two code cells. Only Python standard-library modules are used.\n\nLive API first; weather-response.json is the fallback and is updated when fetching succeeds. The data preview shows this same JSON as a table. practice.ipynb uses the bundled snapshot.\n\nWeather data: Open-Meteo https://open-meteo.com/\n'+snapshot_note+'\nUnits: temp °C; rain probability %.\n\nBuild: solo 10 minutes (no AI), team 35 (limited AI help), solo 15 (no AI). Each student keeps two original coding checks. Every team demos; every member explains their code. Submit your executed notebook and the JSON used. Due 2026-11-18 23:59 JST.\n')
