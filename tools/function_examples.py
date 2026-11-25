"""Short Week 9 examples built from the course's saved public datasets."""
from collections import Counter
import csv
import html
import json
import pprint

DOUBLE = '''def double(number):
    return number * 2'''
EVEN = '''def is_even(number):
    return number % 2 == 0'''
BAR = '''def bar(count, unit):
    return "█" * (count // unit)'''
SPRITE = '''def sprite_url(pokemon, shiny):
    if shiny:
        return pokemon["sprites"]["front_shiny"]
    return pokemon["sprites"]["front_default"]'''
FILTER = '''def strong_quakes(quakes, minimum):
    selected = []
    for quake in quakes:
        if quake["mag"] >= minimum:
            selected.append(quake)
    return selected'''
BIKE = r'''def theft_bar(city, counts):
    count = counts[city]
    return f"{city} ({count:,})\n" + bar(count, 100)'''
AGE = '''def senior_share(row):
    ratio = row["65+"] / row["total"]
    return round(ratio * 100, 1)'''


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
        f'<circle cx="{x(q["mag"]):.2f}" cy="{y(q["depth"]):.2f}" r="4.2">'
        f'<title>{html.escape(q["place"])} · M{q["mag"]:g} · {q["depth"]:g} km</title></circle>'
        for q in data)
    return (f'<figure class="fn-depth" data-quake-count="{len(data)}"><svg viewBox="0 0 352 237" role="img"'
            f' aria-label="Magnitude versus depth, {len(data)} recorded earthquakes">'
            f'<text x="50" y="14">Depth / 深さ (km)</text><g class="fn-gridlines">{grid}</g>'
            f'<path class="fn-chart-axis" d="M50 26V200H335"/>{ticks}{points}'
            '<text x="192" y="234" text-anchor="middle">Magnitude / 規模</text></svg>'
            f'<figcaption><strong>{len(data)}</strong> '+c.bi('件','records')+'</figcaption></figure>')


def add_examples(root, c, add, run, pair, scope, rich):
    bi, p = c.bi, c.p
    text = lambda ja, en: p(ja, en, 'lesson-lead')

    def data(source, ja, en):
        return ('<details class="fn-input-data"><summary>'+bi('使うデータを見る','Show the input data')+'</summary>'
                +run(source,ja+' / '+en,show=False)+'</details>')

    def choices(items):
        buttons = ''.join(f'<button type="button" data-fn-choice="{i}" aria-pressed="false">'+label+'</button>'
                          for i,(label, _) in enumerate(items))
        results = ''.join(f'<div data-fn-choice-result="{i}" hidden>'+out+'</div>'
                          for i,(_,out) in enumerate(items))
        return '<div data-fn-choices class="fn-demo"><div class="fn-actions">'+buttons+'</div><div aria-live="polite">'+results+'</div></div>'

    add('double','2倍にする','Double a number',
        run(DOUBLE+'\n\ndouble(8)','2倍 / Double')
        +text('<code>8</code> が <code>number</code> に入ります。<code>double(0)</code> は？',
              '<code>8</code> goes into <code>number</code>. What does <code>double(0)</code> return?'))
    add('even','偶数かどうか','Is it even?',
        run(EVEN+'\n\nis_even(7)','偶数の判定 / Check for even')
        +text('<code>%</code> は割り算の余り。8に変えたら <code>True</code> か <code>False</code>？',
              '<code>%</code> gives the remainder. If we change 7 to 8, do we get <code>True</code> or <code>False</code>?'),
        'question')
    add('text-bar','数を棒にする','Turn a number into a bar',
        run(BAR+'\n\nbar(7, 2)','文字の棒 / A text bar')
        +text('2で割って、端数を切り捨てる <code>//</code>。<code>█</code> は2ずつ数えます。棒は何文字？',
              '<code>//</code> divides and rounds down. One <code>█</code> stands for 2. How many blocks will you see?'))

    snapshots = root/'weeks/week-03/explore-data'
    raw = json.loads((snapshots/'pokemon.json').read_text())
    pika = {'name': raw['name'], 'sprites': {key: raw['sprites'][key] for key in ('front_default','front_shiny')}}
    prep = data('pikachu = '+pprint.pformat(pika, sort_dicts=False, width=80),'保存したピカチュウのデータ','Saved Pikachu data')
    code = run(SPRITE,'画像URLを返す / Choose a sprite URL')
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
        +p('Week 3 · PokéAPIの保存例','Week 3 · saved PokéAPI response','simulation-note')+prep)

    raw = json.loads((snapshots/'earthquakes.geojson').read_text())
    quakes = [{'mag': row['properties']['mag'], 'depth': row['geometry']['coordinates'][2], 'place': row['properties']['place']}
              for row in raw['features']]
    prep = data('quakes = '+pprint.pformat(quakes, width=88, sort_dicts=False),'USGSの保存データ','Saved USGS data')
    code = run(FILTER,'マグニチュードで絞り込む / Filter by magnitude')
    cases = []
    for minimum in (2.5, 5.0, 6.0):
        call = f'strong_quakes(quakes, {minimum})'
        selection = scope['strong_quakes'](scope['quakes'], minimum)
        cases.append((f'M ≥ {minimum:g}','<code>'+call+'</code>'+depth_plot(selection,c)))
    run('selected = strong_quakes(quakes, 5.0)\nlen(selected), selected[:2]',
        'M5以上の件数と最初の2件 / M5+ count and first two records',show=False)
    add('earthquakes','地震の規模と深さ','Earthquake magnitude and depth',
        pair(code,choices(cases))
        +text('しきい値を上げると何件残る？ 深いほど、点は下に。規模が大きい点が一番深い？',
              'Raise the cutoff. How many dots are left? Deeper quakes plot lower. Is the biggest quake also the deepest?')
        +p('Week 3 · USGS保存例（2026年10月14日）。関数が返した地震を描画。','Week 3 · USGS snapshot, October 14, 2026. The chart plots the records returned by the function.','simulation-note')+prep)

    cities = ['柏市','松戸市','船橋市']
    with (root/'weeks/week-08/bike.csv').open(encoding='cp932',newline='') as stream:
        counts = Counter(row['市区町村（発生地）'] for row in csv.DictReader(stream))
    prep = data('counts = '+repr({city: counts[city] for city in cities}),
                'bike.csvで数えた3市の件数','Counts for three cities from bike.csv')
    add('bikes','同じ関数で、3市の棒グラフ','Three cities, one bar function',
        run(BIKE+'\n\nfor city in counts:\n    print(theft_bar(city, counts))','記録件数の棒グラフ / Bar chart of reported thefts')
        +text('さっきの <code>bar()</code> を再利用。<code>█</code> 一つは100件。棒の長さは概数、かっこの中は正確な件数。',
              'Reuse <code>bar()</code> from the warm-up. Each block is 100 reports. The bar is approximate; the count in parentheses is exact.')
        +p('Week 8 · 千葉県警の2025年自転車盗記録','Week 8 · Chiba Police 2025 reported bicycle thefts','simulation-note')+prep)

    names = ['千葉県','東京都','秋田県','沖縄県']
    with (root/'weeks/week-05/japan.csv').open(encoding='utf-8-sig',newline='') as stream:
        rows = {row['都道府県']: row for row in csv.DictReader(stream)}
    ages = {name: {'65+': int(rows[name]['65歳以上人口']), 'total': int(rows[name]['総人口'])} for name in names}
    prep = data('prefectures = '+pprint.pformat(ages,width=76,sort_dicts=False),'japan.csvから4都県','Four prefectures from japan.csv')
    code = run(AGE+'\n\nfor name in prefectures:\n    share = senior_share(prefectures[name])\n    print(name, share)', '65歳以上の割合 / Share aged 65+',show=False)
    bars = ''.join(f'<li><span>{name}</span><strong>{share:g}%</strong>'
                   f'<meter min="0" max="100" value="{share:g}" aria-label="{name}: {share:g}%"></meter></li>'
                   for name in names for share in [scope['senior_share'](scope['prefectures'][name])])
    add('japan-age','65歳以上は、何％？','How much of each prefecture is 65+?',
        pair(code,choices([(bi('4都県を比較','Compare four prefectures'),'<ul class="fn-age-chart">'+bars+'</ul>')]))
        +text('人口の大きさが違うときは、人数ではなく割合で比べる。<code>round(..., 1)</code> は小数第1位まで。',
              'Percentages let us compare places with different population sizes. <code>round(..., 1)</code> keeps one decimal.')
        +p('Week 5 · japan.csv。棒全体は100%。','Week 5 · japan.csv. Each track represents 100%.','simulation-note')+prep)
