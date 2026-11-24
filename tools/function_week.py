"""Bilingual Week 9 functions lesson, with outputs evaluated in Python at build time."""
import contextlib
import html
import io
import json
import pprint
import re
import zipfile
from weather_hackathon import execute_cell

VERSION = '20261124-code-focus'
RELEASE = '2026-11-26T12:00:00+09:00'
SPEC = dict(title='One function, many calls', title_ja='関数を一つ、何度でも',
            date='2026-11-26', due='2026-12-02', slides=[None]*13)
DATE = '2026-11-12'
SOURCE = 'https://open-meteo.com/en/docs/historical-weather-api'
NAMES = 'names = ["Haru", "Yui", "Ren"]'
GREET = '''def greet():
    return "Hello!"'''
GREET_NAME = '''def greet_name(name):
    return f"Hello, {name}!"'''
NAME_LOOP = '''for student in names:
    message = greet_name(student)
    print(message)'''
LABEL = '''def weather_label(city, icon, high, low):
    return f"{icon} {city}\\n↑{high}°C  ↓{low}°C"'''
BADGE = '''from html import escape

def weather_badge(city, icon, high, low):
    label = weather_label(city, icon, high, low)
    safe_label = escape(label)
    style = ("padding:.75rem;background:#e8eff3;"
             "border-top:3px solid #315876;white-space:pre-line")
    return f'<div style="{style}">{safe_label}</div>' '''
BADGE = BADGE.rstrip()
PANEL = '''def weather_panel(cities, forecast):
    badges = []
    for city in cities:
        icon, high, low = forecast[city]
        badges.append(weather_badge(city, icon, high, low))

    style = "display:grid;grid-template-columns:repeat(2,1fr);gap:8px"
    return f'<div style="{style}">{"".join(badges)}</div>' '''
PANEL = PANEL.rstrip()
DISPLAY = 'from IPython.display import HTML, display\n'


def build(root, c):
    dest = root/'weeks/week-09'
    bi, p, links = c.bi, c.p, c.links
    saved = json.loads((dest/'weather-snapshot.json').read_text())
    assert saved['date'] == DATE
    names = saved['cities']
    icons = {3: '☁️', 51: '🌦️'}
    forecast = {}
    for name, response in zip(names, saved['responses'], strict=True):
        day = response['daily']
        assert day['time'] == [DATE]
        forecast[name] = (icons[day['weather_code'][0]], day['temperature_2m_max'][0], day['temperature_2m_min'][0])
    data_code = 'forecast = '+pprint.pformat(forecast, sort_dicts=False, width=68)+'\n\ncities = ["柏", "札幌", "大阪", "那覇"]'
    w7 = json.loads((root/'weeks/week-07/weather-response.json').read_text())['daily']
    day_index = w7['time'].index(DATE)
    daily_rows = ''.join(f'    "{key}": {value!r},\n' for key, value in w7.items())
    prior = 'daily = {\n'+daily_rows+'}'
    prior += f'\n\nday = {day_index}\nprint(daily["time"][day])\nprint(daily["temperature_2m_max"][day], daily["temperature_2m_min"][day])'
    scope = {}
    cells = [c.mdcell('# Week 09 · 関数を一つ、何度でも\n\n上から順に実行し、結果を予想してから値を変えよう。Run cells in order.')]
    slides = []

    def add(key, ja, en, body, layout='plain'):
        level = 'h1' if layout=='hero' else 'h2'
        slides.append(f'<section class="slide lesson-slide layout-{layout}" data-slide data-ink-id="w9-fn-{key}" hidden><{level}>'+bi(ja,en)+f'</{level}>'+body+'</section>')

    def run(source, heading, show=True, note=None):
        result, value = execute_cell(source, scope)
        if note:
            heading += '\n\n'+note[0]+'\n\n'+note[1]
        count = sum(cell['cell_type']=='code' for cell in cells)+1
        cell = c.codecell(source, result or None, count)
        if value is not None:
            cell['outputs'].append(dict(output_type='execute_result', execution_count=count,
                                        metadata={}, data={'text/plain':repr(value)}))
            result += repr(value)+'\n'
        cells.extend([c.mdcell('## '+heading), cell])
        return c.code_html(source, result if show else None)

    def pair(code, output):
        return '<div class="fn-pair">'+code+output+'</div>'

    def action(key, ja, en):
        return '<button type="button" data-fn-'+key+'>'+bi(ja,en)+'</button>'

    def text(ja,en):
        return p(ja,en,'lesson-lead')

    def rich(expression):
        value = eval(expression,scope)
        cell = c.codecell(DISPLAY+'display(HTML('+expression+'))', count=sum(cell['cell_type']=='code' for cell in cells)+1)
        cell['metadata']['tags'] = ['notebook-display']
        cell['outputs'] = [dict(output_type='display_data',metadata={},data={'text/html':value})]
        cells.append(cell)
        return value

    add('open','ひとこと、あいさつ','One small greeting', '<div class="fn-ticket">Hello!</div>'
        +text('あいさつを一つ用意して、好きなときに呼び出せるようにしよう。','Let’s make one greeting we can call whenever we want.'),'hero')
    add('syntax','関数を呼ぶには？','How do we call a function?',
        text('関数の名前は <code>greet</code>。実行するには、名前の後ろに何を付ける？',
             'Our function will be called <code>greet</code>. What goes after its name to run it?')
        +'<details class="answer"><summary>'+bi('呼び出し方を見る','Reveal the call')+'</summary>'
        +'<div class="fn-ticket"><code>greet<span class="fn-parens">()</span></code></div>'
        +p('<code>()</code> を付けると呼び出し。かっこの中が空なので、今回は何も渡しません。',
           '<code>()</code> makes the call. The parentheses are empty because this call needs no input.')+'</details>','question')
    note=('1行目：<code>def</code> で定義。<code>:</code> の次の行は右にずらす。2行目：<code>return</code> で結果を返す。',
          'Line 1: <code>def</code> starts the definition. After the colon, indent the next line. Line 2: <code>return</code> gives back a result.')
    add('define','greetを作る','Define greet',
        run(GREET,'関数を定義 / Define a function',
            note=tuple(re.sub('<[^>]+>','',line) for line in note))+text(*note)
        +'<details class="answer"><summary>'+bi('ここで何が表示される？','What appears if we run just this?')+'</summary>'
        +p('まだ何も表示されません。次のスライドで呼び出します。','Nothing yet. We call it on the next slide.')+'</details>')
    call_note=('Notebookでは、セルの最後の行の値がそのまま表示されます。',
               'A notebook shows the value of the last expression in the cell.')
    add('call','greetを呼ぶ','Call greet',
        run('greet()','最初の呼び出し / First call',note=call_note)+text(*call_note))
    add('argument','かっこの中に、名前を一つ','One name inside the parentheses',
        run(GREET_NAME+'\n\ngreet_name("Haru")','名前を渡す / Pass a name')
        +text('<code>"Haru"</code> が <code>name</code> に入る。<code>"Yui"</code> に変えたら、何が返る？',
              '<code>"Haru"</code> goes into <code>name</code>. What comes back if you change it to <code>"Yui"</code>?'))
    loop = run(NAMES+'\n\n'+NAME_LOOP,'forの中から呼ぶ / Call inside a loop',show=False)
    add('loop','3人なら、3回呼ぶ','Three names, three calls',
        pair(loop,'<div class="fn-trace" data-name-trace><output data-current>—</output>'
             +'<div class="fn-actions">'+action('next','次の1人','Next name')+action('reset','リセット','Reset')+'</div>'
             +'<ol class="fn-printed" aria-live="polite"></ol></div>')
        +text('<code>for</code> が次の名前を選ぶ。<code>greet_name</code> があいさつを返し、次の行で表示する。',
              '<code>for</code> picks the next name. <code>greet_name</code> returns a greeting, and the next line displays it.'))
    add('week7','Week 7で読んだ daily','The daily data from Week 7',
        run(prior,'Week 7の柏の保存データ / Saved Week 7 Kashiwa data')
        +p('各キーの値はリスト。どのリストでも <code>[1]</code> は同じ日。柏の保存予報で、次の都市比較とは別データです。',
           'Each key holds a list. Index <code>[1]</code> means the same day in every list. This saved Kashiwa forecast is separate from the city comparison.')
        +links([('../week-07/weather-code.html','Week 7のチュートリアル','Week 7 tutorial')]))
    weather_call = 'print(weather_label("柏", "☁️", 16.6, 6.1))'
    add('label','名前を、都市と天気に','A label for one city',
        run(LABEL+'\n\n'+weather_call,'都市ラベル / Weather label')
        +text('入力は4つ。順番を変えたら、何がどこに表示される？ ↑は最高、↓は最低。',
              'There are four inputs. What happens if you swap their order? ↑ is the daily high; ↓ is the low.')
        +p('2026-11-12 · Open-Meteo','2026-11-12 · Open-Meteo','simulation-note'))
    add('data','リストで順番、辞書で値','List for order, dictionary for values',
        run(data_code+'\n\nprint(forecast[cities[0]])','都市リストと気象データ / City list and weather data')
        +text('<code>cities[0]</code> は「柏」。<code>forecast["柏"]</code> から、アイコン・最高・最低を受け取る。',
              '<code>cities[0]</code> is 柏. <code>forecast["柏"]</code> gives the icon, high and low.')
        +p('<a href="'+SOURCE+'">Open-Meteo</a> の過去気象データ（2026-11-12、℃）。☁️ 曇り、🌦️ 弱い霧雨。',
           '<a href="'+SOURCE+'">Open-Meteo</a> historical weather (2026-11-12, °C). ☁️ Overcast; 🌦️ light drizzle.','simulation-note'))
    add('city-loop','名前のときと、同じfor','The same loop, with cities',
        run('for city in cities:\n    icon, high, low = forecast[city]\n    print(weather_label(city, icon, high, low))',
            '都市ごとに関数を呼ぶ / Call once per city')
        +text('名前リストのときと同じ。forが1都市を選び、weather_labelがその1都市分の文字列を返す。',
              'The pattern is the same as the name list. The loop picks a city; weather_label returns its text.'))
    code = run(BADGE,'バッジを組み立てる / Build a badge')
    badge = rich('weather_badge("柏", "☁️", 16.6, 6.1)')
    add('badge','文字列を、1枚のバッジに','One label becomes one badge',
        pair(code,'<div class="fn-reveal">'+action('reveal','バッジを表示','Reveal badge')+'<div data-fn-result hidden>'+badge+'</div></div>')
        +text('中で weather_label を呼び、見た目を付けてHTMLを返す。HTMLはここでは表示用。escapeは文字を安全に表示するため。',
              'The function calls weather_label, adds styling and returns HTML for display. escape keeps the label as text.'))
    code = run(PANEL,'都市をまとめて表示 / Compose a city panel')
    panel = rich('weather_panel(cities, forecast)')
    buttons = ''.join('<label><input type="checkbox" value="'+name+'" checked> '+name+'</label>' for name in names)
    add('panel','関数の中で、forが回る','A loop inside the panel function',
        pair(code,'<div class="fn-panel"><fieldset><legend>'+bi('表示する都市','Cities to show')+'</legend>'+buttons+'</fieldset>'
             +'<div class="fn-actions">'+action('build','パネルを実行','Build panel')+action('city','次の1都市','Next city')+'</div>'
             +'<div data-fn-cities></div><div data-fn-grid aria-live="polite"></div><template data-fn-template>'+panel+'</template></div>')
        +p('都市を選んで予想しよう。appendで1枚ずつ追加し、ループが終わってからパネル全体をreturnする。',
           'Select cities and predict the count. append adds one badge at a time. After the loop, return sends back the whole panel.','lesson-lead')
        +p('保存済みのPython出力を使ったシミュレーション。Notebookではdisplay(HTML(...))で表示。',
           'Browser simulation uses saved Python output. In the notebook, display(HTML(...)) renders the panel.','simulation-note'))
    add('try','1行変えると、何が変わる？','What changes if you edit one line?',
        text('まず都市を2つにする。次に weather_label で最低気温を先に表示。どの関数を変えれば、すべてのバッジに反映される？',
             'First use just two cities. Then show the low temperature first. Which function do you edit to update every badge?')
        +'<details class="answer"><summary>'+bi('ヒント','Hint')+'</summary>'+p('何枚作るかは cities。1枚に何を書くかは weather_label。','cities controls how many. weather_label controls what each badge says.')+'</details>'
        +links([('challenge.html','チャレンジの手順','Challenge instructions'),('practice.ipynb','実行例Notebook','Worked notebook')],9,'lecture.html'),'challenge')
    assert len(slides) == len(SPEC['slides'])
    note = '過去気象データ / Historical weather: '+saved['url']
    cells.insert(1,c.mdcell(note))
    cells.append(c.mdcell('## 自分で試す / Make it yours\n\n都市を2つにして、表示を一つ変更。予想と実際の結果をMarkdownに残そう。'))
    c.notebook(dest/'practice.ipynb',cells)
    for alias in ['fundamentals-functions.ipynb', 'week-09-in-class-functions.ipynb']:
        c.notebook(dest/alias,cells)
    header = '<header class="lecture-header"><a id="lecture-return" href="../../agenda.html?open=09#week-09">← '+bi('授業予定','Agenda')+'</a><span class="lecture-mark">PRG / 26–2 · W09</span><button id="language-toggle" class="language-toggle" type="button">EN</button></header>'
    head = c.page_head('Week 09 · '+SPEC['title'],'course-decks.css','course-decks.js',VERSION)
    head += f'<link rel="stylesheet" href="functions.css?v={VERSION}"><link rel="stylesheet" href="../../assets/slide-annotations.css"><script src="../../assets/slide-annotations.js" defer></script><script src="../../assets/slide-swipe.js" defer></script><script src="functions.js?v={VERSION}" defer></script></head>'
    nav = '<nav class="slide-controls" aria-label="Slide navigation"><div class="slide-nav-group"><button id="previous-slide" type="button">← '+bi('前へ','Previous')+'</button><span id="slide-count" aria-live="polite"></span><button id="next-slide" type="button">'+bi('次へ','Next')+' →</button></div><button id="slide-fullscreen" type="button" class="slide-fullscreen" aria-pressed="false">⛶</button></nav>'
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        exec(NAME_LOOP,scope)
    data = json.dumps(dict(nameTrace=[(f'greet_name({json.dumps(name)})', result)
                                     for name,result in zip(scope['names'],stream.getvalue().splitlines(),strict=True)]),
                      ensure_ascii=False).replace('</','<\\/')
    c.write(dest/'lecture.html',head+f'<body class="lecture-page course-deck functions-week" data-week="9" data-release="{RELEASE}">'+header+'<main><div id="slides-view" class="view">'+nav+'<div class="slide-stage">'+''.join(slides)+'</div></div></main><script id="lesson-data" type="application/json">'+data+'</script></body></html>')
    build_challenge(root, dest, c, header, data_code)


def build_challenge(root, dest, c, header, data_code):
    bi,p,links = c.bi,c.p,c.links
    aim = ('名前の名札から、複数都市の天気パネルへ。def・引数・returnを学び、forから同じ関数を呼びます。',
           'Go from name tags to a weather panel. Learn def, arguments and return, then call the same function from a for loop.')
    challenge = ('都市や表示を変えて、誰かに役立つパネルを作る。天気以外でもOK。',
                 'Change the city list and the badge display to make a useful panel. You can use a different topic.')
    submit = ('実行結果付きの.ipynbを12月2日（水）23:59 JSTまでにUNIPAへ提出。追加ファイルを使った場合は添付。',
              'Submit the .ipynb with saved outputs to UNIPA by Wednesday, December 2 at 23:59 JST. Attach any extra files you used.')
    bullets = [('1件分の値を返す関数を作る。forで3件以上に使い、一つのパネルや一覧にまとめる。',
                'Write a function that returns a result for one item. Call it in a for loop for at least three items and show the results together.'),
               ('都市を減らす、並びを変えるなど、2種類の入力で確認。何を変えたか、結果がどう変わったかをMarkdownに書く。',
                'Check two inputs, for example by changing the selection or its order. Explain what you changed and what happened in Markdown.')]
    body = '<h1>'+bi('自分のパネルを作る','Build your own panel')+'</h1>'+p(*challenge)+c.list_html(bullets)
    body += p('見本Notebookを上から実行し、最後の都市リストと表示を変えて始めよう。保存データ入り。API・pandasの設定は不要。',
              'Run the worked notebook in order, then try changing the last city list and its display. The data is included; no API or pandas setup is needed.')
    body += links([('practice.ipynb','実行例Notebook','Worked notebook')],9)
    body += '<h2 id="homework">'+bi('宿題・提出','Homework and submission')+'</h2>'+p(*submit)+links([('lecture.html','講義スライド','Slides')])
    c.write(dest/'challenge.html',c.page_head('Week 09 · Build your own panel','course-pages.css','course-page.js',VERSION)+f'</head><body class="course-challenge" data-release="{RELEASE}">'+header+'<main id="course-page" hidden>'+body+'</main></body></html>')
    agenda = next((root/'content/weeks').glob('09-*.md'))
    front = agenda.read_text().split('---',2)[1].strip()
    for key,value in [('overview',aim[1]),('overview_ja',aim[0])]:
        front=re.sub(r'^'+key+r':.*$',key+': '+value,front,flags=re.M)
    sections = [
        ('Lecture Flow',('greet()を呼ぶ → 名前を一つ渡す → forから呼ぶ → Week 7の天気データ → 都市パネル。',
                         'Call greet(), pass one name, repeat with for, then use Week 7 weather data to build a city panel.')),
        ('In-Class Notebook',('実行前に予想する。見本Notebookを上から動かし、名前や都市を変える。',
                              'Predict the output, run the worked notebook in order, then change its names or cities.')),
        ('In-Class Challenge',(challenge[0]+' [手順](weeks/week-09/challenge.html)。',challenge[1]+' [Instructions](weeks/week-09/challenge.html).')),
        ('Take-Home Assignment',(submit[0]+' [要件](weeks/week-09/challenge.html#homework)。',submit[1]+' [Requirements](weeks/week-09/challenge.html#homework).')),
    ]
    text='---\n'+front+'\n---\n'
    for title,(ja,en) in sections:
        text+=f'## {title}\nEN: {en}\nJP: {ja}\n'
    text+='''## Resources
- [Week 09 Lecture — One function, many calls](weeks/week-09/lecture.html) {lecture}
- [ミニ講義の実行例 / Worked Examples](weeks/week-09/practice.ipynb) {fundamentals}
- [チャレンジの手順 / Challenge Instructions](weeks/week-09/challenge.html) {challenge}
- [宿題・提出方法 / Homework and Submission](weeks/week-09/challenge.html#homework) {homework}
'''
    c.write(agenda,text)
    c.notebook(dest/'challenge-starter.ipynb',[
        c.mdcell('# Week 09 · 自分のパネルを作る\n\n氏名：\n\n誰が、何を知るために使うパネル？\n\n'+challenge[0]),
        c.codecell(data_code),
        c.mdcell('## 1件分の関数\n\n引数を受け取り、1件分のラベルをreturnする。'),
        c.codecell('# def で1件分の関数を書く。'),
        c.mdcell('## forで繰り返す\n\n少なくとも3件に同じ関数を使う。出力は一覧やパネルにまとめる。'),
        c.codecell('# for の中から関数を呼ぶ。'),
        c.mdcell('## 確認\n\n2種類の入力で、予想と実行結果を比べる。何を変えた？ 結果はどう変わった？'),
    ])
    with zipfile.ZipFile(dest/'starter-files.zip','w',compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in ('practice.ipynb','challenge-starter.ipynb','weather-snapshot.json'):
            entry = zipfile.ZipInfo('week-09/'+name,(2026,11,24,0,0,0))
            bundle.writestr(entry,(dest/name).read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
