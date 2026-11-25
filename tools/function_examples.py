"""Short Week 9 examples built from the course's saved public datasets."""
from collections import Counter
import csv
import html
import json

DOUBLE = '''def double(number):
    return number * 2'''
EVEN = '''def is_even(number):
    return number % 2 == 0'''
BAR = '''def bar(count, unit):
    return "█" * (count // unit)'''
SPRITE = '''def sprite_url(sprites, shiny):
    if shiny:
        return sprites["front_shiny"]
    return sprites["front_default"]'''
FILTER = '''def strong_quakes(quakes, minimum):
    selected = []
    for quake in quakes:
        magnitude, depth = quake
        if magnitude >= minimum:
            selected.append(quake)
    return selected'''
BIKE = r'''def theft_bar(city, counts):
    count = counts[city]
    return f"{city} ({count:,})\n" + bar(count, 100)'''
AGE = '''def senior_share(row):
    ratio = row["65+"] / row["total"]
    return round(ratio * 100, 1)'''


def example(definition='', call='', *, data='', data_note='データを用意する',
            function_note='関数を定義する', call_note='関数を呼び出す'):
    """Keep the shown and notebook source identical, with visible section comments."""
    parts = [(data_note, data), (function_note, definition), (call_note, call)]
    return '\n\n'.join('# '+note+'\n'+body for note, body in parts if body)


def depth_plot(data, c):
    """Depth increases downwards; both axes stay fixed when the cutoff changes."""
    x = lambda mag: 50 + (mag - 2) * 57
    y = lambda km: 30 + km * .85
    grid = ''.join(
        f'<path d="M50 {y(km):g}H335"/><text x="44" y="{y(km)+4:g}" text-anchor="end">{km}</text>'
        for km in range(0, 201, 50))
    ticks = ''.join(
        f'<text x="{x(mag):g}" y="217" text-anchor="middle">{mag}</text>' for mag in range(2, 8))
    points = ''.join(
        f'<circle cx="{x(magnitude):.2f}" cy="{y(depth):.2f}" r="4.2">'
        f'<title>M{magnitude:g} · {depth:g} km</title></circle>'
        for magnitude, depth in data)
    return (f'<figure class="fn-depth" data-quake-count="{len(data)}"><svg viewBox="0 0 352 237" role="img"'
            f' aria-label="Magnitude versus depth, {len(data)} recorded earthquakes">'
            f'<text x="50" y="14">Depth / 深さ (km)</text><g class="fn-gridlines">{grid}</g>'
            f'<path class="fn-chart-axis" d="M50 26V200H335"/>{ticks}{points}'
            '<text x="192" y="234" text-anchor="middle">Magnitude / 規模</text></svg>'
            f'<figcaption><strong>{len(data)}</strong> '+c.bi('件','records')+'</figcaption></figure>')


def add_examples(root, c, add, run, pair, scope, rich):
    bi, p = c.bi, c.p
    text = lambda ja, en: p(ja, en, 'lesson-lead')

    def choices(items):
        buttons = ''.join(f'<button type="button" data-fn-choice="{i}" aria-pressed="false">'+label+'</button>'
                          for i,(label, _) in enumerate(items))
        results = ''.join(f'<div data-fn-choice-result="{i}" hidden>'+out+'</div>'
                          for i,(_,out) in enumerate(items))
        return '<div data-fn-choices class="fn-demo"><div class="fn-actions">'+buttons+'</div><div aria-live="polite">'+results+'</div></div>'

    add('double','2倍にする','Double a number',
        run(example(DOUBLE,'double(8)',function_note='数を2倍にして返す'),'2倍 / Double')
        +text('<code>8</code> が <code>number</code> に入ります。<code>double(0)</code> は？',
              '<code>8</code> goes into <code>number</code>. What does <code>double(0)</code> return?'))
    add('even','偶数かどうか','Is it even?',
        run(example(EVEN,'is_even(7)',function_note='2で割った余りが0なら True'),'偶数の判定 / Check for even')
        +text('<code>%</code> は割り算の余り。8に変えたら <code>True</code> か <code>False</code>？',
              '<code>%</code> gives the remainder. If we change 7 to 8, do we get <code>True</code> or <code>False</code>?'),
        'question')
    add('text-bar','数を棒にする','Turn a number into a bar',
        run(example(BAR,'bar(7, 2)',function_note='1ブロックを unit 個として、文字の棒を返す'),'文字の棒 / A text bar')
        +text('2で割って、端数を切り捨てる <code>//</code>。<code>█</code> は2ずつ数えます。棒は何文字？',
              '<code>//</code> divides and rounds down. One <code>█</code> stands for 2. How many blocks will you see?'))

    snapshots = root/'weeks/week-03/explore-data'
    raw = json.loads((snapshots/'pokemon.json').read_text())
    pika = {key: raw['sprites'][key] for key in ('front_default','front_shiny')}
    root_url = 'https://raw.githubusercontent.com/'
    folder = pika['front_default'].rsplit('/',1)[0] + '/'
    repo, sprite_dir = folder.removeprefix(root_url).split('/master/',1)
    data = f'base_url = "{root_url}"\nbase_url += "{repo}/master/"\nbase_url += "{sprite_dir}"\n'
    data += 'pikachu = {\n'+''.join(f'    "{key}": base_url + "{url.removeprefix(folder)}",\n' for key,url in pika.items())+'}'
    code = run(example(SPRITE,'sprite_url(pikachu, False)',data=data,
                       data_note='保存データから、ピカチュウの画像URLを2つ用意',
                       call_note='通常の画像を選ぶ。True にすると色違い'),
               '画像URLを返す / Choose a sprite URL',show=False)
    assert scope['pikachu'] == pika
    sprites = []
    for flag,ja,en in [(False,'通常','Original'),(True,'色違い','Shiny')]:
        call = f'sprite_url(pikachu, {flag})'
        caption = f'<small>{html.escape(call)}</small>'
        mark = '<figure class="fn-sprite"><img width="216" height="216" alt="Pikachu '+en.lower()+' sprite" src="'
        end = '">'+caption+'</figure>'
        image = rich(f"{mark!r} + {call} + {end!r}")
        sprites.append((bi(ja,en),image))
    add('pokemon','ピカチュウの色違いスイッチ','Pikachu: standard or shiny?',
        pair(code,choices(sprites))
        +text('同じピカチュウ。<code>shiny</code> が <code>True</code> になると、どのキーを使う？',
              'Same Pikachu. Which key will the function use if <code>shiny</code> is <code>True</code>?')
        +p('Week 3 · PokéAPIの保存例','Week 3 · saved PokéAPI response','simulation-note'))

    raw = json.loads((snapshots/'earthquakes.geojson').read_text())
    quakes = [(row['properties']['mag'], round(row['geometry']['coordinates'][2],2)) for row in raw['features']]
    rows = '\n'.join('    '+', '.join(map(repr,quakes[i:i+5]))+',' for i in range(0,len(quakes),5))
    code = run(example(FILTER,'selected = strong_quakes(quakes, 5.0)\nlen(selected)',
                       data='quakes = [\n'+rows+'\n]', data_note=f'USGSの{len(quakes)}件。各組は (マグニチュード, 深さ km)',
                       call_note='M5以上を選び、件数を見る'),
               'マグニチュードで絞り込む / Filter by magnitude',show=False)
    cases = []
    for minimum in (2.5, 5.0, 6.0):
        call = f'strong_quakes(quakes, {minimum})'
        selection = scope['strong_quakes'](scope['quakes'], minimum)
        cases.append((f'M ≥ {minimum:g}','<code>'+call+'</code>'+depth_plot(selection,c)))
    add('earthquakes','地震の規模と深さ','Earthquake magnitude and depth',
        pair(code,choices(cases))
        +text('しきい値を上げると何件残る？ 深いほど、点は下に。規模が大きい点が一番深い？',
              'Raise the cutoff. How many dots are left? Deeper quakes plot lower. Is the biggest quake also the deepest?')
        +p('Week 3 · USGS保存例（2026年10月14日）。深さは小数第2位まで。','Week 3 · USGS snapshot, October 14, 2026. Depths are rounded to two decimals.','simulation-note'))

    cities = ['柏市','松戸市','船橋市']
    with (root/'weeks/week-08/bike.csv').open(encoding='cp932',newline='') as stream:
        counts = Counter(row['市区町村（発生地）'] for row in csv.DictReader(stream))
    add('bikes','同じ関数で、3市の棒グラフ','Three cities, one bar function',
        run(example(BAR+'\n\n'+BIKE,'for city in counts:\n    result = theft_bar(city, counts)\n    print(result)',
                    data='counts = '+repr({city: counts[city] for city in cities}),
                    data_note='bike.csvで数えた3市の自転車盗記録',
                    call_note='1市ずつ関数を呼び、改行を含む結果を表示'),
            '記録件数の棒グラフ / Bar chart of reported thefts')
        +text('さっきの <code>bar()</code> を再利用。<code>█</code> 一つは100件。棒の長さは概数、かっこの中は正確な件数。',
              'Reuse <code>bar()</code> from the warm-up. Each block is 100 reports. The bar is approximate; the count in parentheses is exact.')
        +p('Week 8 · 千葉県警の2025年自転車盗記録','Week 8 · Chiba Police 2025 reported bicycle thefts','simulation-note'))

    names = ['千葉県','東京都','秋田県','沖縄県']
    with (root/'weeks/week-05/japan.csv').open(encoding='utf-8-sig',newline='') as stream:
        rows = {row['都道府県']: row for row in csv.DictReader(stream)}
    ages = {name: {'65+': int(rows[name]['65歳以上人口']), 'total': int(rows[name]['総人口'])} for name in names}
    data = 'prefectures = {\n'+''.join(f'    "{name}": {row!r},\n' for name,row in ages.items())+'}'
    code = run(example(AGE,'shares = {}\nfor name, row in prefectures.items():\n    shares[name] = senior_share(row)\nshares',
                       data=data,data_note='japan.csvから4都県の65歳以上人口と総人口',
                       call_note='各都県の割合を辞書にまとめる'),
               '65歳以上の割合 / Share aged 65+',show=False)
    bars = ''.join(f'<li><span>{name}</span><strong>{share:g}%</strong>'
                   f'<meter min="0" max="100" value="{share:g}" aria-label="{name}: {share:g}%"></meter></li>'
                   for name,share in scope['shares'].items())
    add('japan-age','65歳以上は、何％？','How much of each prefecture is 65+?',
        pair(code,choices([(bi('4都県を比較','Compare four prefectures'),'<ul class="fn-age-chart">'+bars+'</ul>')]))
        +text('人口の大きさが違うときは、人数ではなく割合で比べる。<code>round(..., 1)</code> は小数第1位まで。',
              'Percentages let us compare places with different population sizes. <code>round(..., 1)</code> keeps one decimal.')
        +p('Week 5 · japan.csv。棒全体は100%。','Week 5 · japan.csv. Each track represents 100%.','simulation-note'))
