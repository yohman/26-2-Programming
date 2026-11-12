"""Small, function-free student examples for the Week 7 weather reference."""
import hashlib
import html
import json
from datetime import datetime, timedelta, timezone

TODAY = '''# ① 調べる日と、傘を勧める基準を決める

# 0＝今日、1＝明日
day_offset = 0

# 降水確率の基準（%）
umbrella_threshold = 50

# ② 対象の日の降水確率を取り出す
daily = weather["daily"]
i = past_days + day_offset
chance = daily["precipitation_probability_max"][i]
print(daily["time"][i])

# Noneはデータなし。0%とは区別する
if chance is None:
    print("Rain probability is unavailable.")
else:
    print("Maximum precipitation probability:", chance, "%")

    # ③ 自分たちで決めた基準と比べ、メッセージを変える
    if chance >= umbrella_threshold:
        print("An umbrella may be useful.")
    else:
        print("A lower rain chance, but not a guarantee.")'''

YESTERDAY = '''# ① 昨日を選ぶ（取得セルのpast_daysは1以上にする）

# -1＝昨日、0＝今日
day_offset = -1

# ② 日付の番号を計算し、2種類の雨量を取り出す（mm）
daily = weather["daily"]
i = past_days + day_offset
rain = daily["rain_sum"][i]
showers = daily["showers_sum"][i]
print(daily["time"][i])

# どちらかの値がないときは、合計を計算しない
if rain is None or showers is None:
    print("Rainfall estimate is unavailable.")
else:

    # ③ 雨量を合計する。昨日の値は観測ではなくモデルの推定
    amount = rain + showers
    print("Model-estimated rainfall:", amount, "mm")
    if amount > 0:
        print("The model suggests some rain.")
    else:
        print("The model estimates no rain.")'''

DAYS = '''# ① 表示を始める日を選ぶ（0＝今日、1＝明日）
start_day = 0

# ② 指定した日から、取得済みの最後の日まで繰り返す
daily = weather["daily"]
for i in range(past_days + start_day, len(daily["time"])):

    # 日付・最低気温・最高気温・降水確率を、同じiで取り出す
    print(daily["time"][i],
          daily["temperature_2m_min"][i], "to",
          daily["temperature_2m_max"][i], "°C |",
          daily["precipitation_probability_max"][i], "%")'''

CITIES = '''# ① 比べる都市と、APIの取得条件を先に設定する
cities = ["Tokyo", "Osaka", "Naha"]

# 日本の都市に絞る
country_code = "JP"

# 地名の表示言語
language = "en"

# 各都市の検索候補数
match_count = 1

# 過去何日分を含めるか
past_days = 1

# 今日を含む取得日数
forecast_days = 3

# 各都市の現地時間
timezone = "auto"
daily_fields = "precipitation_probability_max"

# 0＝今日、1＝明日
day_offset = 1

# 通信を待つ最大秒数
timeout = 10

# ② 都市ごとに「場所の検索→天気の取得→表示」を繰り返す
for city in cities:

    # 都市名から、最初の候補の場所を調べる
    url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode({
        "name": city, "count": match_count,
        "language": language, "countryCode": country_code
    })
    with urlopen(url, timeout=timeout) as response:
        city_place = json.load(response)["results"][0]

    # 見つかった緯度・経度を、天気APIに渡す
    lat = city_place["latitude"]
    lon = city_place["longitude"]
    url = "https://api.open-meteo.com/v1/forecast?" + urlencode({
        "latitude": lat, "longitude": lon, "daily": daily_fields,
        "past_days": past_days, "forecast_days": forecast_days,
        "timezone": timezone
    })
    with urlopen(url, timeout=timeout) as response:
        city_weather = json.load(response)

    # ③ 指定した日の日付と降水確率を表示する
    daily = city_weather["daily"]
    i = past_days + day_offset
    chance = daily["precipitation_probability_max"][i]
    print(city_place["name"], daily["time"][i], chance, "%")'''

BARS = '''# ① 表示する日と、文字の棒の見た目を決める

# 0＝今日から、1＝明日から
start_day = 0

# 棒全体の文字数（正の整数）
bar_width = 20

# 確率に応じて塗る部分
filled = "█"

# 残りの部分
empty = "░"

# ② 100%を棒の長さで割り、1文字分の割合を求める
daily = weather["daily"]
points_per_block = 100 / bar_width
print("Maximum precipitation probability")
print("Each block is about", points_per_block, "percentage points.")

# ③ 各日の降水確率を、文字の棒で表示する
for i in range(past_days + start_day, len(daily["time"])):
    chance = daily["precipitation_probability_max"][i]
    if chance is None:
        print(daily["time"][i], "No data")
    else:

        # 文字数を丸め、塗る部分と残りの部分をつなぐ
        blocks = round(chance / points_per_block)
        bar = filled * blocks + empty * (bar_width - blocks)

        # 丸める前の正確な%も、棒の横に表示する
        print(f'{daily["time"][i]} |{bar}| {chance:3}%')'''

REPEAT = '''# ① 選べる日と、終了用の入力を決める

# 0＝今日、1＝明日
day_options = ["0", "1"]

# この文字を入力したら終了
quit_command = "q"
prompt = f"Days ahead {day_options}, {quit_command} = quit: "

# ② 取得済みのデータを使い、最初の入力を受け取る
daily = weather["daily"]
choice = input(prompt)

# ③ 終了コマンドが入力されるまで繰り返す
while choice != quit_command:
    if choice in day_options:

        # 入力は文字列なので、計算する前にintで整数にする
        i = past_days + int(choice)
        print(daily["time"][i],
              daily["temperature_2m_max"][i], "°C")
    else:
        print("Choose from", day_options, "or", quit_command)

    # 入力を更新し、次のwhileの条件で確かめる
    choice = input(prompt)'''

EXAMPLES = [
    dict(id='today', title='今日、雨は？ / Rain today', code=TODAY,
         note='<code>day_offset</code>と<code>umbrella_threshold</code>を先に決める。<code>i = past_days + day_offset</code>で日付の番号を計算。<code>if</code>で表示を変える。50%はこの例の目安なので、自分たちの目的に合わせて変えよう。降水確率は降る時間の割合ではなく、雪も含みます。雪が予想される場所では雨量も確認。 / Set the day offset and umbrella threshold first; add past_days to find the matching date. The 50% umbrella rule is our choice, not an API recommendation. Probability is not the fraction of the day it will rain. It includes snow; check the rain amount too in snowy weather.'),
    dict(id='yesterday', title='昨日、雨だった？ / Yesterday’s rain', code=YESTERDAY,
         note='<code>day_offset = -1</code>で昨日を選ぶ。<code>past_days</code>は1以上必要。<code>rain_sum + showers_sum</code>で液体の雨量（mm）。<code>None</code>はデータなし。0と区別しよう。昨日の値は過去予報のモデル推定で、実際の雨を確認する観測記録ではありません。 / Set day_offset to -1 and request at least one past day. Add rain and showers in mm. These past-day model values are not confirmed station observations.'),
    dict(id='days', title='日ごとにfor / Loop over days', code=DAYS,
         note='<code>start_day</code>で開始日を指定。0は今日、1は明日。<code>past_days + start_day</code>から、取得した最後の日まで読む。同じ番号<code>i</code>のデータを組にする。<code>print()</code>はループ内の各行の表示に必要です。 / Set start_day first, then pair each date with the values at the same index.'),
    dict(id='cities', title='街を比べる / Compare cities', code=CITIES,
         note='選んだ3都市の「明日の降水確率」をforで比べる。<code>countryCode="JP"</code>は日本の街に限定。<code>cities</code>・国・日数を最初に設定。<code>day_offset = 1</code>で明日を選び、<code>i = past_days + day_offset</code>で番号を計算。各地の現地日付を表示します。 / Compare the chosen cities, not every place in the world. Choose the cities, country and day settings first. day_offset = 1 selects tomorrow; its index is past_days + day_offset. The displayed date is local to each city.'),
    dict(id='visual', title='見える予報 / A visual forecast', code=BARS,
         note='文字の棒なら追加ライブラリ不要。<code>bar_width</code>は正の整数にし、記号も最初に決める。<code>filled * blocks</code>で文字を繰り返し、<code>round()</code>で棒の長さを丸める。<code>{chance:3}</code>は3文字分の幅で数字をそろえる。数値も一緒に出して丸めた量を明確に。 / Repeat a character to make a bar. Set a positive bar_width and choose the symbols first. With width 20, each block represents about five percentage points; keep the exact percentage beside it.'),
    dict(id='repeat', title='任意：while / Optional while', code=REPEAT,
         note='<code>day_options</code>と<code>quit_command</code>を最初に設定。新しい通信はせず、取得済みのデータを繰り返し見る例。入力をループの最後で更新し、<code>q</code>で終了。コード集の出力例では入力を<code>0 → 1 → q</code>としています。必須ではありません。 / Reuse the loaded weather and update the choice each time. Set the allowed days and quit command first. Sample inputs: 0, 1, q. This extension is optional.'),
]


def build(root,c,meteo_code,location_code,weather_code,version,release):
    folder=root/'weeks/week-07'
    source=json.loads((folder/'weather-source.json').read_text())
    recorded=json.loads((folder/'weather-examples.json').read_text())
    compared=datetime.fromisoformat(recorded['retrieved_at']).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M JST')
    when=datetime.fromisoformat(source['retrieved_at']).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M JST')
    bi,p=c.bi,c.p
    def text_pair(value):return bi(*value.split(' / ',1))
    def code(value):return '<pre data-language="python"><code>'+html.escape(value)+'</code></pre>'
    def output(value):return '<div class="sample-output" data-no-copy>'+p('Pythonの実行結果','PYTHON OUTPUT','eyebrow')+'<pre>'+html.escape(value)+'</pre></div>'
    def topic(number,id,ja,en,active=False):
        return f'<a href="#{id}"'+(' aria-current="page"' if active else '')+f'><span class="topic-number">{number:02}</span> '+bi(ja,en)+'</a>'
    toc=topic(1,'data','データ取得','Get the data',True)+topic(2,'city','街の天気','Weather by city')
    for number,example in enumerate(EXAMPLES,3):
        toc+=topic(number,example['id'],*example['title'].split(' / ',1))
    sections=[
        '<section id="data" data-topic>'+p('01 / はじめに','01 / START HERE','eyebrow')+'<h2>'+bi('Open-Meteoのデータ取得','Get data from Open-Meteo')+'</h2>'
        +p('先に<code>lat</code>・<code>lon</code>・<code>past_days</code>・<code>forecast_days</code>などの設定を決め、Code Cellで実行します。設定を変えたらこのセルを再実行。<code>urlopen</code>で接続し、<code>json.load</code>でJSONをPythonの辞書に読み込みます。',
           'Set <code>lat</code>, <code>lon</code>, day counts and other inputs up front, then run the cell. After changing a setting, rerun this cell to fetch matching data. <code>json.load</code> turns the JSON response into a Python dictionary.')
        +code(meteo_code)+output(source['meteo_output'])
        +p('APIの応答には位置・単位・天気データが含まれます。ここでは最後の<code>weather["daily"]</code>で、日別データの部分を表示しています。各項目は、同じ日付順に並んだリストです。',
           'The response contains location, units and weather data. The final <code>weather["daily"]</code> shows its daily data: one list for each field, aligned by date.')
        +p('<code>lat</code>＝緯度、<code>lon</code>＝経度。<code>past_days</code>＝過去の日数。<code>forecast_days</code>＝今日を含む予報の日数。<code>daily_fields</code>＝欲しい項目。<code>timezone="auto"</code>＝その場所の現地時間。<br><strong>この設定では 0＝昨日、1＝今日、2＝明日、3＝明後日。</strong><br>temperature_2m_max / min＝最高・最低気温（°C）。precipitation_probability_max＝最大降水確率（%）。rain_sum + showers_sum＝雨量（mm）。<br><code>i = past_days + day_offset</code>で、day_offsetが0なら今日、1なら明日、-1なら昨日。取得した範囲内の日を選ぼう。昨日の雨量はモデル推定値です。',
           '<code>lat</code> and <code>lon</code> set the coordinates. <code>past_days</code> adds past dates; <code>forecast_days</code> includes today. <code>daily_fields</code> chooses the weather fields; <code>timezone="auto"</code> uses local time.<br><strong>With these settings: 0 yesterday, 1 today, 2 tomorrow, 3 the next day.</strong><br>temperature_2m_max / min: high / low (°C); precipitation_probability_max: maximum probability (%); rain_sum + showers_sum: rainfall (mm).<br>If past_days changes, today’s index changes too. Use <code>i = past_days + day_offset</code> (0 today, 1 tomorrow, -1 yesterday) within the dates you loaded. Yesterday’s rainfall is model-estimated; probability is not certainty.','reading')
        +p('都市名で場所を選ぶなら、次の <a href="#city">街の天気</a> を参考に。ほかの例もこのデータから始められます。',
           'To choose a location by city name, use <a href="#city">Weather by city</a>. Other topics can continue directly from this data.')+'</section>',
        '<section id="city" data-topic hidden>'+p('02 / 場所を選ぶ','02 / CHOOSE A LOCATION','eyebrow')+'<h2>'+bi('街の天気','Weather by city')+'</h2>'
        +p('都市名を選びたいときの例。新しいCode Cellで①→②の順に実行すると、<code>weather</code>がその街の日別データに変わります。',
           'To choose a city, run ① then ② in new Code cells. <code>weather</code> will then contain that city’s daily data.')
        +'<h3>'+bi('① 都市名から場所を探す','① Find the city')+'</h3>'
        +p('都市名・候補数・言語・待ち時間を先に設定し、最初の候補<code>results[0]</code>の地域・国を確認。',
           'Set the city, match count, language and timeout first, then check the first match’s region and country.')
        +code(location_code)+output(source['outputs'][0][0]['data']['text/plain'])
        +'<details><summary>'+bi('入力して街を選ぶ','Let the user enter a city')+'</summary>'
        +p('①の<code>city = "Kashiwa"</code>の行をこれに置き換え、①と②を再実行。',
           'Replace the <code>city = "Kashiwa"</code> line in ① with this, then rerun ① and ②.')
        +code('# 都市名の入力を受け取る（例：Tokyo）\ncity = input("City: ")')
        +p('入力例：<code>Tokyo</code>。該当なしなら別の表記を試す。検索の辞書に<code>"countryCode": "JP"</code>を加えると日本に絞れます。',
           'Example input: <code>Tokyo</code>. Try another spelling if needed; adding <code>"countryCode": "JP"</code> to the lookup parameters restricts matches to Japan.')+'</details>'
        +'<h3>'+bi('② その場所の天気を取得する','② Get its weather')+'</h3>'
        +p('①の<code>place</code>の緯度・経度を使い、項目・日数などを先に設定して取得。',
           'Set lat and lon from the <code>place</code> found in ①, then choose the fields, day counts, timezone and timeout before requesting data.')
        +code(weather_code)+output(source['outputs'][1][0]['data']['text/plain'])+'</section>',
    ]
    for number,example in enumerate(EXAMPLES,3):
        result=recorded['examples'][example['id']]
        assert result['sha256']==hashlib.sha256(example['code'].encode()).hexdigest(), 'Refresh helper outputs after changing sample code.'
        sections.append(f'<section id="{example["id"]}" data-topic hidden>'+p(f'{number:02} / コードと実行結果',f'{number:02} / PYTHON → OUTPUT','eyebrow')+'<h2>'+text_pair(example['title'])+'</h2>'
            +p('先に <a href="#data">データ取得</a> を実行。','Run <a href="#data">Get the data</a> first.','prerequisite')
            +'<p>'+text_pair(example['note'])+'</p>'+code(example['code'])+output(result['output'])+'</section>')
    page=f'''<!doctype html><html lang="ja" data-language="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>天気コード集 · Week 07 プログラミング</title><link rel="icon" href="../../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="weather-code.css?v={version}"><link rel="stylesheet" href="../../assets/copy-blocks.css"><script src="weather-code.js?v={version}" defer></script><script src="../../assets/copy-blocks.js" defer></script></head><body data-release="{release}"><a class="skip" href="#examples">{bi('コード例へ移動','Skip to examples')}</a><div id="weather-guide" hidden><aside><div class="guide-tools"><a class="back" href="challenge.html">{bi('← 課題','← Challenge')}</a><button id="language-toggle" type="button" aria-label="Switch to English">EN</button></div><nav aria-label="コードの目次" data-label-ja="コードの目次" data-label-en="Code topics">{p('目次','CHOOSE A TOPIC','eyebrow')}{toc}</nav><div class="related-links"><a href="challenge.html">{bi('課題・提出方法','Challenge instructions')}</a><a href="../../agenda.html?open=07#week-07">{bi('授業予定 ↗','Agenda ↗')}</a></div></aside><main id="examples"><header>{p('第7週 / Webチュートリアル','WEEK 07 / WEB TUTORIAL','eyebrow')}<h1>{bi('天気を、コードで。','Weather, in Python.')}</h1>{p('自分のNotebookを作り、最初の「データ取得」から始めよう。ほかのテーマは、作品に必要なものだけ選べます。','Create your own notebook and start with “Get the data.” Use other topics as needed for your app.')}{p('Pythonの保存出力：'+when+'（柏市）。都市比較：'+compared+'（東京・大阪・那覇）。再実行すると値は更新されます。','Recorded Python output: Kashiwa, Japan · '+when+'. City comparison: Tokyo / Osaka / Naha · '+compared+'. Fresh requests return updated values.','source-note')}{p('データ：<a href="https://open-meteo.com/en/docs">Open-Meteo</a> · <a href="https://open-meteo.com/en/docs/geocoding-api">都市検索API</a> · 追加インストール不要。','Data: <a href="https://open-meteo.com/en/docs">Open-Meteo</a> · <a href="https://open-meteo.com/en/docs/geocoding-api">City lookup docs</a> · No extra packages.','source-note')}</header>{''.join(sections)}<footer><a href="challenge.html">{bi('課題・提出方法に戻る →','Back to the challenge →')}</a>{p('コードを貼るだけで終わらず、何を変え、何が分かったかをMarkdownで書こう。','Explain your changes and findings in Markdown.')}</footer></main></div></body></html>'''
    c.write(folder/'weather-code.html',page)
