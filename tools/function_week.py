"""Bilingual Week 9 functions lesson, with outputs evaluated in Python at build time."""
import contextlib
import html
import io
import json
import pprint
import re
import zipfile
import quiz_package
from weather_hackathon import execute_cell

VERSION = '20261125-quiz-ab'
RELEASE = '2026-11-26T12:00:00+09:00'
SPEC = dict(title='One function, many calls', title_ja='関数を一つ、何度でも',
            date='2026-11-26', due='2026-12-02', slides=[None]*17)
CHALLENGE = (
    '自分で選んだデータを使っても、データなしで小さなツールや遊びを作ってもOK。役に立つ、意外な発見がある、思わず笑える。関数で「何かができる」Notebookを作ろう。',
    'Choose a dataset, or build a small tool or game with your own inputs. Use a function to make a notebook that does something useful, surprising, or funny.')
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

    add('recap','先週の自転車盗データ','Last week: the bike hackathon',
        '<div class="fn-recap-stat"><strong>68.4%</strong><span>'+bi('盗難記録のうち「施錠せず」','of recorded thefts involved unlocked bikes')+'</span></div>'
        +text('10,054件のうち6,879件。みんなのNotebookでは、<code>for</code> で何を数えた？ この数字から盗まれる確率は分かる？',
              '6,879 out of 10,054 reports. What did your notebook count with <code>for</code>? Does this number tell us the chance of a bike being stolen?')
        +links([('../week-08/challenge.html#data-guide','先週のデータを見る','Revisit last week’s data')]),'hero')
    add('quiz','小テスト①','Pop quiz 01',
        '<div class="quiz-score"><span>6 '+bi('問','questions')+'</span><span>30 '+bi('点','pts')+' × 2</span></div>'
        +text('個人で解きます。授業中に案内するパスワードでNotebookを開き、氏名を書いて開始の合図を待ちます。',
              'Work individually. Use the password announced in class to get the notebook, add your name, and wait for the start signal.')
        +links([('quiz.html','小テストを開く','Open the quiz')]),'hero')
    clock = '<div class="quiz-clock" data-quiz-clock><div class="quiz-phases">'
    for index,(ja,en) in enumerate([('A：AIなし','A: Without AI'),('B：AI利用OK','B: AI allowed')]):
        clock += f'<button type="button" data-phase="{index}" aria-pressed="{str(index == 0).lower()}">'+bi(ja,en)+'</button>'
    clock += '</div><output data-clock aria-live="off">06:00</output><div><button type="button" data-clock-toggle aria-label="Start timer">▶</button><button type="button" data-clock-reset aria-label="Reset timer">↺</button><span data-clock-status role="status">'+bi('開始待ち','Ready')+'</span></div></div>'
    add('quiz-clock','6分 ＋ 6分','6 minutes + 6 minutes',clock
        +text('Aは問題文とヒントだけ。6分で保存し、Aはそのまま。Bでは、AIを使って解答の修正や未回答の問題に取り組めます。どちらも相談は不可。',
              'In A, use only the quiz and its hints. Save at six minutes and leave A untouched. In B, you may use AI to revise or finish answers. Work individually in both rounds.'))
    add('quiz-save','提出はNotebook 1ファイル','One notebook to submit',
        '<p class="big-filename">week09_quiz_氏名.ipynb</p>'
        +text('変更しない問題はBを空欄に。「すべて実行」はせず、出力を残して保存します。終了の合図で、途中でもUNIPAへ1回だけ提出。',
              'Leave B blank for answers you keep. Save your outputs without using Run All. At the signal, submit once to UNIPA, even if unfinished.'))

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
    add('try','その関数で、何ができる？','What will your function do?',
        text(*CHALLENGE)
        +c.list_html([
            ('<code>def</code> で一つ、入力を受け取り結果を返す関数を作る。','Use <code>def</code> to write one function that takes input and returns a result.'),
            ('入力を2通り試して、結果を見せる。','Show what it does with two different inputs.'),
            ('誰のために何をするのか、Markdownで一言。','In Markdown, say what it does and who it’s for.')])
        +links([('challenge.html','チャレンジの手順','Challenge instructions')]),'challenge')
    assert len(slides) == len(SPEC['slides'])
    note = '過去気象データ / Historical weather: '+saved['url']
    cells.insert(1,c.mdcell(note))
    cells.append(c.mdcell('## 自分で試す / Make it yours\n\n都市を2つにして、表示を一つ変更。予想と実際の結果をMarkdownに残そう。'))
    c.notebook(dest/'practice.ipynb',cells)
    for alias in ['fundamentals-functions.ipynb', 'week-09-in-class-functions.ipynb']:
        c.notebook(dest/alias,cells)
    header = '<header class="lecture-header"><a id="lecture-return" href="../../agenda.html?open=09#week-09">← '+bi('授業予定','Agenda')+'</a><span class="lecture-mark">PRG / 26–2 · W09</span><button id="language-toggle" class="language-toggle" type="button">EN</button></header>'
    head = c.page_head('Week 09 · '+SPEC['title'],'course-decks.css','course-decks.js',VERSION)
    head += f'<link rel="stylesheet" href="../week-08/bicycle-week.css?v={VERSION}"><link rel="stylesheet" href="functions.css?v={VERSION}"><link rel="stylesheet" href="../../assets/slide-annotations.css"><script src="../../assets/slide-annotations.js" defer></script><script src="../../assets/slide-swipe.js" defer></script><script src="../week-08/bicycle-week.js?v={VERSION}" defer></script><script src="functions.js?v={VERSION}" defer></script></head>'
    nav = '<nav class="slide-controls" aria-label="Slide navigation"><div class="slide-nav-group"><button id="previous-slide" type="button">← '+bi('前へ','Previous')+'</button><span id="slide-count" aria-live="polite"></span><button id="next-slide" type="button">'+bi('次へ','Next')+' →</button></div><button id="slide-fullscreen" type="button" class="slide-fullscreen" aria-pressed="false">⛶</button></nav>'
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        exec(NAME_LOOP,scope)
    data = json.dumps(dict(nameTrace=[(f'greet_name({json.dumps(name)})', result)
                                     for name,result in zip(scope['names'],stream.getvalue().splitlines(),strict=True)]),
                      ensure_ascii=False).replace('</','<\\/')
    c.write(dest/'lecture.html',head+f'<body class="lecture-page course-deck functions-week" data-week="9" data-release="{RELEASE}">'+header+'<main><div id="slides-view" class="view">'+nav+'<div class="slide-stage">'+''.join(slides)+'</div></div></main><script id="lesson-data" type="application/json">'+data+'</script></body></html>')
    quiz_package.build(root,c)
    quiz_package.build_page(root,c,header,VERSION)
    build_challenge(root, dest, c, header)


def build_challenge(root, dest, c, header):
    bi,p,links = c.bi,c.p,c.links
    aim = ('自転車盗ハッカソンの振り返り → 小テスト① → 関数のミニ講義 → 自分のNotebookを制作。',
           'Bike hackathon recap → pop quiz → functions mini-lecture → build your own notebook.')
    submit = ('実行結果付きの.ipynbを12月2日（水）23:59 JSTまでにUNIPAへ提出。追加ファイルを使った場合は添付。',
              'Submit the .ipynb with saved outputs to UNIPA by Wednesday, December 2 at 23:59 JST. Attach any extra files you used.')
    bullets = [('空のNotebookを作り、タイトル・氏名・「誰のために何をするか」をMarkdownに書く。',
                'Start a blank notebook. In Markdown, add your title, name, and what the notebook does for whom.'),
               ('<code>def</code> で入力を受け取り、<code>return</code> で結果を返す関数を一つ作る。',
                'Write at least one function with <code>def</code> that takes an input and uses <code>return</code> to give back a result.'),
               ('同じ関数を違う入力で2回試して、結果を保存する。何件も処理するときは <code>for</code> から呼んでみよう。',
                'Call the same function with two different inputs and save the results. If you have many items, try calling it from a <code>for</code> loop.')]
    body = '<h1>'+bi('その関数で、何ができる？','What will your function do?')+'</h1>'+p(*CHALLENGE)
    body += '<h2>'+bi('Notebookに入れるもの','What to put in your notebook')+'</h2>'+c.list_html(bullets)
    body += '<h2>'+bi('例えば','For example')+'</h2>'+c.list_html([
        ('自転車盗データと市名を渡して、その市の記録件数を返す。','Give your function the bike data and a city name; get back the city’s reported theft count.'),
        ('都市名を渡して、天気と最高・最低気温のバッジを返す。','Give your function a city name; get back a badge with the weather and temperatures.'),
        ('残り時間を渡して、休み時間にできることを提案する。','Give your function the minutes left in your break; get back a suggestion for what to do.')])
    body += p('見本は天気で実演しています。APIやpandasは必須ではありません。','The worked notebook uses weather as an example. No API or pandas is required.')
    body += links([('practice.ipynb','天気の実行例Notebook','Worked weather notebook'),('challenge-starter.ipynb','Notebookの構成例','Notebook outline')],9)
    body += '<h2 id="homework">'+bi('宿題・提出','Homework and submission')+'</h2>'+p(*submit)+links([('lecture.html','講義スライド','Slides')])
    c.write(dest/'challenge.html',c.page_head('Week 09 · What will your function do?','course-pages.css','course-page.js',VERSION)+f'</head><body class="course-challenge" data-release="{RELEASE}">'+header+'<main id="course-page" hidden>'+body+'</main></body></html>')
    agenda = next((root/'content/weeks').glob('09-*.md'))
    front = agenda.read_text().split('---',2)[1].strip()
    for key,value in [('overview',aim[1]),('overview_ja',aim[0]),
                      ('practice_mix','Individual quiz · Build with functions'),('practice_mix_ja','個人の小テスト・関数で制作'),
                      ('homework_title','Make a notebook that does something'),('homework_title_ja','関数で「何かができる」Notebook')]:
        front=re.sub(r'^'+key+r':.*$',key+': '+value,front,flags=re.M)
    sections = [
        ('Lecture Flow',('先週の自転車盗レポートを振り返る → 小テスト① → 関数：greet()から天気パネルへ → Notebook制作。',
                         'Recap the bike reports → pop quiz → functions, from greet() to a weather panel → build a notebook.')),
        ('In-Class Notebook',('小テスト①は個人で6問。AはAIなしで6分。保存してAを残し、BはAI利用OKで6分。得点は各30点満点、提出はNotebook 1ファイル。パスワードは授業で案内します。',
                              'Six questions, worked individually. Take six minutes without AI in A, then save and leave A unchanged. You may use AI in B for six minutes. Each round is scored out of 30. Submit one notebook. Get the password in class.')),
        ('In-Class Challenge',(CHALLENGE[0]+' [手順](weeks/week-09/challenge.html)。',CHALLENGE[1]+' [Instructions](weeks/week-09/challenge.html).')),
        ('Take-Home Assignment',(submit[0]+' [要件](weeks/week-09/challenge.html#homework)。',submit[1]+' [Requirements](weeks/week-09/challenge.html#homework).')),
    ]
    text='---\n'+front+'\n---\n'
    for title,(ja,en) in sections:
        text+=f'## {title}\nEN: {en}\nJP: {ja}\n'
    text+='''## Resources
- [Week 09 Lecture — One function, many calls](weeks/week-09/lecture.html) {lecture}
- [小テスト①・パスワードで開く / Open Graded Quiz 01](weeks/week-09/quiz.html) {notebook}
- [ミニ講義の実行例 / Worked Examples](weeks/week-09/practice.ipynb) {fundamentals}
- [チャレンジの手順 / Challenge Instructions](weeks/week-09/challenge.html) {challenge}
- [宿題・提出方法 / Homework and Submission](weeks/week-09/challenge.html#homework) {homework}
'''
    c.write(agenda,text)
    c.notebook(dest/'challenge-starter.ipynb',[
        c.mdcell('# 作品タイトル / Project title\n\n氏名 / Name：\n\n誰のために、何をするNotebook？ / What does it do, and who is it for?'),
        c.codecell('# 自分のデータや入力値を用意する / Set up your data or inputs'),
        c.mdcell('## 関数 / Function\n\nどんな入力を受け取り、何を返す？ / What does it take in and give back?'),
        c.codecell('# def で関数を定義する / Define your function'),
        c.mdcell('## 入力を変えて試す / Try two different inputs'),
        c.codecell('# 1つ目の入力で呼び出す / Call it with the first input'),
        c.codecell('# 2つ目の入力で呼び出す / Call it with the second input'),
        c.mdcell('## 結果 / Results\n\n入力を変えたら、結果はどう変わった？ / How did the result change?'),
    ])
    with zipfile.ZipFile(dest/'starter-files.zip','w',compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in ('practice.ipynb','challenge-starter.ipynb','weather-snapshot.json'):
            entry = zipfile.ZipInfo('week-09/'+name,(2026,11,24,0,0,0))
            bundle.writestr(entry,(dest/name).read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
