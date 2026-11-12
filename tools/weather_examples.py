"""Small, function-free student examples for the Week 7 weather reference."""
import hashlib
import html
import json
from datetime import datetime, timedelta, timezone

TODAY = '''daily = weather["daily"]
i = 1  # Today with the starter's settings
chance = daily["precipitation_probability_max"][i]
print(place["name"], daily["time"][i])
if chance is None:
    print("Rain probability is unavailable.")
else:
    print("Maximum precipitation probability:", chance, "%")
    if chance >= 50:
        print("An umbrella may be useful.")
    else:
        print("A lower rain chance, but not a guarantee.")'''

YESTERDAY = '''daily = weather["daily"]
i = 0  # Yesterday with past_days = 1
rain = daily["rain_sum"][i]
showers = daily["showers_sum"][i]
print(place["name"], daily["time"][i])
if rain is None or showers is None:
    print("Rainfall estimate is unavailable.")
else:
    amount = rain + showers
    print("Model-estimated rainfall:", amount, "mm")
    if amount > 0:
        print("The model suggests some rain.")
    else:
        print("The model estimates no rain.")'''

DAYS = '''daily = weather["daily"]
for i in range(1, len(daily["time"])):
    print(daily["time"][i],
          daily["temperature_2m_min"][i], "to",
          daily["temperature_2m_max"][i], "°C |",
          daily["precipitation_probability_max"][i], "%")'''

CITIES = '''cities = ["Tokyo", "Osaka", "Naha"]
for city in cities:
    url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode({
        "name": city, "count": 1, "language": "en", "countryCode": "JP"
    })
    with urlopen(url, timeout=10) as response:
        city_place = json.load(response)["results"][0]

    url = "https://api.open-meteo.com/v1/forecast?" + urlencode({
        "latitude": city_place["latitude"],
        "longitude": city_place["longitude"],
        "daily": "precipitation_probability_max",
        "past_days": 1, "forecast_days": 3, "timezone": "auto"
    })
    with urlopen(url, timeout=10) as response:
        city_weather = json.load(response)

    # Same settings as the starter: 2 = tomorrow
    tomorrow = city_weather["daily"]
    chance = tomorrow["precipitation_probability_max"][2]
    print(city_place["name"], tomorrow["time"][2], chance, "%")'''

BARS = '''daily = weather["daily"]
print(place["name"], "| Maximum precipitation probability")
print("Each block is about 5 percentage points.")
for i in range(1, len(daily["time"])):
    chance = daily["precipitation_probability_max"][i]
    if chance is None:
        print(daily["time"][i], "No data")
    else:
        blocks = round(chance / 5)
        bar = "█" * blocks + "░" * (20 - blocks)
        print(f'{daily["time"][i]} |{bar}| {chance:3}%')'''

REPEAT = '''daily = weather["daily"]
choice = input("1 = today, 2 = tomorrow, q = quit: ")
while choice != "q":
    if choice in ["1", "2"]:
        i = int(choice)
        print(daily["time"][i],
              daily["temperature_2m_max"][i], "°C")
    else:
        print("Please enter 1, 2 or q.")
    choice = input("1 = today, 2 = tomorrow, q = quit: ")'''

EXAMPLES = [
    dict(id='today', title='今日、雨は？ / Rain today', code=TODAY,
         note='<code>i = 1</code>はスターターで取得した「今日」。<code>if</code>で表示を変える。50%はこの例の目安なので、自分たちの目的に合わせて変えよう。降水確率は降る時間の割合ではなく、雪も含みます。雪が予想される場所では雨量も確認。 / Index 1 is today in the starter. The 50% umbrella rule is our choice, not an API recommendation. Probability is not the fraction of the day it will rain. It includes snow; check the rain amount too in snowy weather.'),
    dict(id='yesterday', title='昨日、雨だった？ / Yesterday’s rain', code=YESTERDAY,
         note='<code>rain_sum + showers_sum</code>で液体の雨量（mm）。<code>None</code>はデータなし。0と区別しよう。昨日の値は過去予報のモデル推定で、実際の雨を確認する観測記録ではありません。 / Add rain and showers in mm. These past-day model values are not confirmed station observations.'),
    dict(id='days', title='日ごとにfor / Loop over days', code=DAYS,
         note='<code>range(1, len(...))</code>で昨日を飛ばし、今日からの3日分を読む。同じ番号<code>i</code>のデータを組にする。<code>print()</code>はループ内の各行の表示に必要です。 / Skip yesterday and pair each date with the values at the same index.'),
    dict(id='cities', title='街を比べる / Compare cities', code=CITIES,
         note='選んだ3都市の「明日の降水確率」をforで比べる。<code>countryCode="JP"</code>は日本の街に限定。スターターと同じ設定なので<strong>2＝明日</strong>。各地の現地日付を表示します。 / Compare the chosen cities, not every place in the world. The starter’s date indexes still apply: 2 is tomorrow. The displayed date is local to each city.'),
    dict(id='visual', title='見える予報 / A visual forecast', code=BARS,
         note='文字の棒なら追加ライブラリ不要。<code>"█" * blocks</code>で文字を繰り返し、<code>round()</code>で棒の長さを丸める。<code>{chance:3}</code>は3文字分の幅で数字をそろえる。数値も一緒に出して丸めた量を明確に。 / Repeat a character to make a bar. Each block represents about five percentage points; keep the exact percentage beside it.'),
    dict(id='repeat', title='任意：while / Optional while', code=REPEAT,
         note='新しい通信はせず、取得済みのデータを繰り返し見る例。入力をループの最後で更新し、<code>q</code>で終了。コード集の出力例では入力を<code>1 → 2 → q</code>としています。必須ではありません。 / Reuse the loaded weather and update the choice each time. Sample inputs: 1, 2, q. This extension is optional.'),
]


def build(root,c,location_code,weather_code,version,release):
    folder=root/'weeks/week-07'
    source=json.loads((folder/'weather-source.json').read_text())
    recorded=json.loads((folder/'weather-examples.json').read_text())
    compared=datetime.fromisoformat(recorded['retrieved_at']).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M JST')
    when=datetime.fromisoformat(source['retrieved_at']).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M JST')
    def code(source): return '<pre data-language="python"><code>'+html.escape(source)+'</code></pre>'
    def output(text): return '<div class="sample-output" data-no-copy><p class="eyebrow">PYTHON OUTPUT / 実行結果</p><pre>'+html.escape(text)+'</pre></div>'
    toc='<a href="#city" aria-current="page"><span>01</span> 街の天気 / Weather by city</a>'
    for i,example in enumerate(EXAMPLES,2): toc+=f'<a href="#{example["id"]}"><span>{i:02}</span> {example["title"]}</a>'
    sections=['<section id="city" data-topic><p class="eyebrow">01 / START HERE</p><h2>街の天気 / Weather by city</h2><p>スターターと同じコードです。新しいNotebookで①→②の順に実行。ほかのテーマはこの準備の後に試そう。 / These are the starter’s two code cells. Run ① then ② in a notebook before trying another topic.</p><h3>① 都市名 → 場所 / Find the city</h3><p><code>city</code>を書き換える。<code>urlencode</code>で検索用のURLを作り、<code>json.load</code>で結果を辞書として読む。最初の候補<code>results[0]</code>の地域・国を必ず確認。 / Edit city and check the first match’s region and country.</p>'+code(location_code)+output(source['outputs'][0][0]['data']['text/plain'])+'<details><summary>入力して街を選ぶ / Let the user enter a city</summary><p>①の<code>city = "Kashiwa"</code>の行をこれに置き換え、①と②を再実行。 / Replace that line in ①, then rerun ① and ②.</p>'+code('city = input("City: ")')+'<p>入力例：<code>Tokyo</code>。該当なしなら別の表記を試す。国が違う場合は検索の辞書に<code>"countryCode": "JP"</code>を追加すると日本に絞れます。 / Example input: Tokyo. Try another spelling if no result is found; countryCode can restrict results to Japan.</p></details><h3>② 場所 → 天気 / Get its weather</h3><p><code>latitude</code>・<code>longitude</code>は①の場所。<code>daily</code>は日別の項目、<code>past_days=1</code>は昨日も含める設定。 / Use the coordinates from ①, request daily fields and include yesterday.</p>'+code(weather_code)+output(source['outputs'][1][0]['data']['text/plain'])+'<p class="reading"><strong>この設定では 0＝昨日、1＝今日、2＝明日、3＝明後日。</strong><br>°C＝気温、%＝最大降水確率、mm＝雨量。日付はその街の現地時間。昨日はモデル推定値。<br>With these settings: 0 yesterday, 1 today, 2 tomorrow, 3 the next day. Dates are local; yesterday’s values are model estimates.</p></section>']
    for number,example in enumerate(EXAMPLES,2):
        result=recorded['examples'][example['id']]
        assert result['sha256']==hashlib.sha256(example['code'].encode()).hexdigest(), 'Refresh helper outputs after changing sample code.'
        sections.append(f'<section id="{example["id"]}" data-topic hidden><p class="eyebrow">{number:02} / PYTHON → OUTPUT</p><h2>{example["title"]}</h2><p class="prerequisite">先に <a href="#city">街の天気の①と②</a> を実行。 / Run the <a href="#city">two setup cells</a> first.</p><p>{example["note"]}</p>'+code(example['code'])+output(result['output'])+'</section>')
    page=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Weather code guide · Week 07 Programming</title><link rel="icon" href="../../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="weather-code.css?v={version}"><link rel="stylesheet" href="../../assets/copy-blocks.css"><script src="weather-code.js?v={version}" defer></script><script src="../../assets/copy-blocks.js" defer></script></head><body data-release="{release}"><a class="skip" href="#examples">本文へ / Skip to examples</a><div id="weather-guide" hidden><aside><a class="back" href="challenge.html">← 天気ハッカソン / Challenge</a><nav aria-label="コードの目次 / Code topics"><p class="eyebrow">CHOOSE A TOPIC / 目次</p>{toc}</nav><div class="downloads"><a href="../../viewer.html?file=weeks%2Fweek-07%2Fchallenge-starter.ipynb&amp;title=Weather+starter&amp;return=weeks%2Fweek-07%2Fweather-code.html">スターターのプレビュー / Preview</a><a href="challenge-starter.ipynb" download>↓ スターター / Starter .ipynb</a><a href="../../agenda.html?open=07#week-07">授業予定 / Agenda ↗</a></div></aside><main id="examples"><header><p class="eyebrow">WEEK 07 / CODE REFERENCE</p><h1>天気を、コードで。<br><span>Weather, in Python.</span></h1><p>左からテーマを選び、コードと結果を見比べよう。必要な例だけ使い、自分たちのアプリに変えてください。<br>Choose a topic. Compare code and output, then adapt only what your app needs.</p><p class="source-note">Pythonで実行した保存結果 / Recorded Python outputs · {when} · Kashiwa, Japan · 都市比較 / City comparison: {compared} (Tokyo / Osaka / Naha)。再実行すると変わります。<br>Data: <a href="https://open-meteo.com/en/docs">Open-Meteo</a> · <a href="https://open-meteo.com/en/docs/geocoding-api">City lookup docs</a> · 標準ライブラリのみ / No extra packages.</p></header>{''.join(sections)}<footer><a href="challenge.html">課題・提出方法に戻る / Back to the challenge →</a><p>コードを貼るだけで終わらず、何を変え、何が分かったかをMarkdownで書こう。 / Explain your changes and findings in Markdown.</p></footer></main></div></body></html>'''
    c.write(folder/'weather-code.html',page)
