"""Build the Week 10 terminal lesson from its runnable Python examples."""
from pathlib import Path
import html
import json
import re
import subprocess
import sys
import zipfile

VERSION = '20261127-ascii-terminal'
RELEASE = '2026-12-03T12:00:00+09:00'
DUE = '2026-12-09'
SLIDES = ['open', 'save', 'run', 'frame', 'loop', 'train', 'rain', 'challenge', 'share']
SCRIPTS = ['hello.py', 'train.py', 'rain.py']
SPEC = dict(title='ASCII Studio', title_ja='ASCIIスタジオ', date='2026-12-03', due=DUE, slides=SLIDES)
GOAL = (
    '文字と空白で絵を作り、自分の .py ファイルをターミナルから動かす。',
    'Make pictures with text and spaces, then run your own .py file from a terminal.',
)
BRIEF = (
    '文字だけで、自分のシーンを作ろう。動く作品でも、ループで行を増やす一枚絵でもOK。',
    'Make an original scene out of text. Animate it, or use a loop to build a still picture one row at a time.',
)
REQUIREMENTS = [
    ('入力を受け取って1フレーム（または1行）の文字列を返す関数を作る。',
     'Write a function that takes an argument and returns the text for one frame or row.'),
    ('for ループで違う値を関数に渡し、位置・形・文字などを変えて表示する。',
     'Call it in a for loop with different values so the position, shape, or text changes.'),
    ('ターミナルで実行できて、自然に終了することを確かめる。追加パッケージは不要。',
     'Check that it runs in a terminal and ends on its own. No extra packages are needed.'),
]
HOMEWORK = (
    '作品を仕上げて、ascii.py を UNIPA に提出。先頭のコメントに作品名・氏名・実行コマンド・何が変化するかを短く書く。Notebookは不要。',
    'Polish your piece and submit ascii.py to UNIPA. In comments at the top, include the title, your name, the run command, and what changes. No notebook is needed.',
)
SAVE = (
    'VS Codeで作業フォルダを開く。新規ファイルを作り、hello.py という名前で保存。Pythonコードだけを書く（``` や .py.txt は不要）。',
    'Open your working folder in VS Code. Create a new file and save it as hello.py. Write only Python code: no backtick fences or .py.txt.',
)
RUN = (
    'VS Codeの「Terminal → New Terminal」を開き、hello.py を保存したフォルダで実行する。',
    'Open Terminal → New Terminal in VS Code. Run the command from the folder that contains hello.py.',
)
FIX = (
    '「ファイルが見つからない」？ macOSなら ls、Windowsなら dir で hello.py があるか確認。&gt;&gt;&gt; が出ていたら exit() でターミナルに戻る。Windowsで python が使えなければ py hello.py を試す。',
    'File not found? Use ls on macOS or dir on Windows to check for hello.py. If you see &gt;&gt;&gt;, type exit() to return to the terminal. If python is unavailable on Windows, try py hello.py.',
)
COMMANDS = '# macOS\npython3 hello.py\n\n# Windows\npython hello.py'
TRAIN_HINT = (
    r'<code>\r</code> は行の先頭へ戻る。<code>end=""</code> で改行せず、<code>flush=True</code> で今すぐ表示。<code>sleep(0.12)</code> は次のコマまでの待ち時間（秒）。',
    r'<code>\r</code> returns to the start of the line. <code>end=""</code> skips the newline and <code>flush=True</code> displays immediately. <code>sleep(0.12)</code> waits 0.12 seconds.',
)
RAIN_HINT = (
    r'雨の行だけを変えて、屋根は固定。<code>\033[2J\033[H</code> はターミナルを消去して左上に戻す合図。複数行を描き直したいときだけ使う。',
    r'Change the rain while the roof stays still. <code>\033[2J\033[H</code> clears the terminal and moves the cursor to the top left. Use it only when you want to redraw several lines.',
)


def output(source):
    """Run a trusted example in a fresh interpreter and capture its stdout."""
    return subprocess.run([sys.executable, '-c', source], capture_output=True,
                          check=True, timeout=10).stdout.decode('utf-8')


def frames(source, separator):
    """Keep the frame text and timing from the same code the students receive."""
    text = output(source)
    args = re.findall(r'^ +sleep\(([\d.]+)\)$', source, re.M)
    assert len(args) == 1
    return {'frames': text.split(separator)[1:], 'delay': round(float(args[0]) * 1000)}


def build(root: Path, c):
    dest = root/'weeks/week-10'
    hello, train, rain = [(dest/name).read_text(encoding='utf-8').rstrip() for name in SCRIPTS]
    hello_output = output(hello)
    demos = {'train': frames(train, '\r'), 'rain': frames(rain, '\x1b[2J\x1b[H')}
    demos['train']['frames'][-1] = demos['train']['frames'][-1].rstrip('\n')
    frame_def = train[train.index('# 空白'):train.index('# 1コマずつ')].rstrip()
    one_frame = frame_def + '\n\n# 右に6文字分ずらして表示\nprint(train_frame(6))'
    frame_loop = frame_def + '\n\n# 位置を変えて、1コマずつ別の行に表示\nfor position in range(0, 10, 3):\n    print(train_frame(position))'
    examples = [(hello, hello_output), (one_frame, output(one_frame)), (frame_loop, output(frame_loop))]
    bi, p = c.bi, c.p
    heading = lambda ja, en: '<h2>'+bi(ja, en)+'</h2>'
    cmd = '<pre class="ascii-terminal-command" data-language="shell"><code>'+html.escape(COMMANDS)+'</code></pre>'
    links = lambda items: c.links(items)
    assets = f'<link rel="stylesheet" href="ascii.css?v={VERSION}"><script src="ascii.js?v={VERSION}" defer></script>'
    header = '<header class="lecture-header"><a id="lecture-return" class="return-link" href="../../agenda.html?open=10#week-10">← '+bi('授業予定','Agenda')+'</a><span class="lecture-mark">PRG / 26–2</span><button id="language-toggle" class="language-toggle" type="button" aria-label="Switch language">EN</button></header>'
    slides = []

    def demo(name, mode=''):
        example = demos[name]
        first = html.escape(example['frames'][0].rstrip('\n'))
        return (f'<div class="ascii-demo {mode}" data-ascii-demo="{name}"><div class="ascii-preview">'
                f'<pre id="ascii-{name}-{mode}" class="ascii-output" tabindex="0">{first}</pre></div>'
                '<div class="ascii-actions"><button data-ascii-play type="button" '
                f'aria-controls="ascii-{name}-{mode}">▶ '+bi('再生','Play')+'</button>'
                f'<button data-ascii-step type="button" aria-controls="ascii-{name}-{mode}">'+bi('1コマ進む','Next frame')+'</button>'
                f'<span data-ascii-index>01 / {len(example["frames"]):02d}</span></div></div>')

    def add(key, ja, en, body, layout=''):
        index = len(slides)+1
        tag = 'h1' if layout == 'curtain' else 'h2'
        slides.append(f'<section class="slide lesson-slide ascii-slide ascii-{layout or "plain"}" data-slide data-ink-id="w10-ascii-{key}" hidden><{tag}>{bi(ja,en)}</{tag}>{body}</section>')
        assert key == SLIDES[index-1]

    note = p('Pythonで実行した出力をブラウザで再生。','The browser replays output captured from Python.','simulation-note')
    add('open','文字だけで、雨','Rain, made of text',
        demo('rain','opening')+p('今日は .py ファイルを作って、ターミナルで動かす。','Today you’ll make a .py file and run it in a terminal.','ascii-caption'), 'curtain')
    add('save','最初のファイル：hello.py','The first file: hello.py',
        c.code_html(*examples[0])+p(*SAVE,'ascii-caption'), 'code')
    add('run','ターミナルから起動','Running from the terminal',
        p(*RUN)+cmd+'<pre class="ascii-hello-output">'+html.escape(hello_output.strip())+'</pre>'
        +p('Notebookと違い、最後に値を書くだけでは表示されない。ターミナルに出すときは print()。','A script won’t display a bare value like a notebook cell does. Use print() to show it.','ascii-caption')
        +'<details><summary>'+bi('うまく動かないとき','If it doesn’t run')+'</summary>'+p(*FIX)+'</details>', 'command')
    add('frame','空白も絵の一部','Spaces are part of the picture',
        c.code_html(*examples[1])+p('6 を 0 や 12 に変えたら、列車はどこに出る？','Where will the train be if you change 6 to 0 or 12?','ascii-caption'), 'code')
    add('loop','ループで位置を変える','The loop changes the position',
        c.code_html(*examples[2])+p('関数は1コマを作る。for は位置を変えて、同じ関数を何度も呼ぶ。','The function makes one frame. The loop calls it again with a different position.','ascii-caption'), 'code')
    add('train','同じ行で動く列車','A train on one line',
        demo('train','compact')+c.code_html(train)+p(*TRAIN_HINT,'ascii-caption')
        +p('動いているプログラムを止めるには Ctrl+C。','Press Ctrl+C in the terminal to stop a running script.','ascii-caption')+note, 'example')
    add('rain','屋根はそのまま、雨だけ動く','A still roof, moving rain',
        demo('rain','compact')+c.code_html(rain)+p(*RAIN_HINT,'ascii-caption')+note, 'example')
    add('challenge','30分：ASCIIチャレンジ','30 minutes: ASCII challenge',
        p(*BRIEF,'lesson-lead')+c.list_html(REQUIREMENTS)
        +p('たとえば、柏駅の発車案内、点滅するゲームのタイトル、行ごとに模様が変わるポスター。自分のアイデアも歓迎。','Try a Kashiwa Station departure board, a blinking game title, or a poster that changes pattern row by row. Your own idea is welcome.')
        +links([('challenge.html','チャレンジの手順・コード例','Challenge instructions and examples')]), 'challenge')
    add('share','上映と提出','Showtime and submission',
        p('友だちに実行コマンドだけを渡し、動くか確認。発表は30秒：ターミナルで実行し、ループが何を変えるか一言。','Give a classmate the run command and see if it works. For the 30-second share-out, run the script and say what the loop changes.','lesson-lead')
        +p(*HOMEWORK)+links([('challenge.html#homework','宿題・提出方法','Homework and submission')])
        +p('最後に、最終作品のアイデアを一つメモ。今日の作品から発展させてもOK。','Before you leave, jot down one final-project idea. You can build on today’s piece.','ascii-caption'), 'share')
    nav = ('<nav class="slide-controls" aria-label="Slide navigation"><div class="slide-nav-group">'
           '<button id="previous-slide" type="button">←</button><span id="slide-count" aria-live="polite"></span>'
           '<button id="next-slide" type="button">→</button></div><button id="slide-fullscreen" type="button" '
           'class="slide-fullscreen" aria-pressed="false" aria-label="Fullscreen">⛶</button></nav>')
    payload = json.dumps(demos).replace('</','<\\/')
    data = f'<script type="application/json" id="ascii-data">{payload}</script>'
    head = c.page_head('Week 10 · ASCII Studio','course-decks.css','course-decks.js',VERSION)
    head += '<link rel="stylesheet" href="../../assets/slide-annotations.css"><script src="../../assets/slide-annotations.js" defer></script><script src="../../assets/slide-swipe.js" defer></script>'
    c.write(dest/'lecture.html',head+assets+f'</head><body class="lecture-page course-deck ascii-week" data-week="10" data-release="{RELEASE}">'
            +header+'<main><div id="slides-view" class="view">'+nav+'<div class="slide-stage">'+''.join(slides)+'</div></div></main>'
            +'<script type="application/json" id="lesson-data">{}</script>'+data+'</body></html>\n')

    body = p(*BRIEF)+'<section id="first-file">'+heading('最初の .py','Your first .py')+p(*SAVE)+c.code_html(hello)+p(*RUN)+cmd
    body += '<pre class="ascii-hello-output">'+html.escape(hello_output.strip())+'</pre>'
    body += ('<details><summary>'+bi('うまく動かないとき','If it doesn’t run')+'</summary>'+p(*FIX)
             +p('<a href="https://code.visualstudio.com/docs/python/run">VS Code公式：Pythonを実行する</a>',
                '<a href="https://code.visualstudio.com/docs/python/run">VS Code documentation: Running Python code</a>')
             +'</details></section>')
    body += '<section id="examples">'+heading('動くサンプル','Animation examples')
    body += p('コードをコピーして、自分で .py として保存。hello.py と同じように、コマンドのファイル名を train.py や rain.py に変えて実行する。','Copy the code and save it as a .py file. Run it like hello.py, replacing the file name in the command with train.py or rain.py.')
    for name, code, hint in [('train',train,TRAIN_HINT),('rain',rain,RAIN_HINT)]:
        body += f'<h3>{name}.py</h3>'+demo(name,'page')+c.code_html(code)+p(*hint)+note
    body += links([('starter-files.zip','サンプル .py（ZIP）','Example scripts (ZIP)')])+'</section>'
    body += '<section id="make">'+heading('30分：自分の作品','30 minutes: your own piece')+c.list_html(REQUIREMENTS)
    body += p('新しい ascii.py を作る。まず1コマ（または1行）だけ表示し、次にループで変化させる。最後に相手のターミナルでも試す。','Create a new ascii.py. Get one frame or row to print, then use a loop to make it change. Finally, try it on a classmate’s terminal.')+'</section>'
    body += '<section id="homework">'+heading('宿題・提出','Homework and submission')+p(*HOMEWORK)+p(f'締切：{DUE} 23:59 JST',f'Due: {DUE}, 23:59 JST')+'</section>'
    head = c.page_head('Week 10 challenge · ASCII Studio','course-pages.css','course-page.js',VERSION)
    c.write(dest/'challenge.html',head+assets+f'</head><body class="course-challenge ascii-week" data-release="{RELEASE}">'+header
            +'<main id="course-page" hidden><h1>'+bi(SPEC['title_ja'],SPEC['title'])+'</h1>'+body
            +links([('lecture.html','講義スライド','Lecture slides')])+'</main>'+data+'</body></html>\n')

    cells = [c.mdcell('# ASCII Studio\n\n授業の提出形式は .py です。スライドとチャレンジページの手順に沿ってターミナルで実行しましょう。\n\nThis notebook is a reference. Save and run your own .py in a terminal for the assignment.')]
    cells += [c.codecell(code,result,i) for i,(code,result) in enumerate(examples,1)]
    cells += [c.mdcell('## Terminal examples\n\n'+''.join(f'### {name}\n\n```python\n{code}\n```\n\n' for name,code in [('train.py',train),('rain.py',rain)]))]
    for name in ['practice.ipynb','week-10-in-class-systems.ipynb']:
        c.notebook(dest/name,cells)
    with zipfile.ZipFile(dest/'starter-files.zip','w') as pack:
        for name in SCRIPTS:
            item=zipfile.ZipInfo('week-10/'+name,date_time=(2026,11,27,0,0,0))
            item.compress_type=zipfile.ZIP_DEFLATED
            pack.writestr(item,(dest/name).read_bytes())

    source = root/'content/weeks/10-systems.md'
    front = source.read_text().split('---',2)[1].rstrip()
    values = dict(title=SPEC['title'], title_ja=SPEC['title_ja'], overview=GOAL[1], overview_ja=GOAL[0],
                  homework_title='Your terminal ASCII piece', homework_title_ja='ターミナルで動くASCII作品',
                  notebook_title='First .py file', notebook_title_ja='最初の .py ファイル',
                  challenge_title='ASCII challenge', challenge_title_ja='ASCIIチャレンジ')
    for key,value in values.items():
        front = re.sub(r'^'+key+r':.*$',key+': '+value,front,flags=re.M) if re.search(r'^'+key+r':',front,re.M) else front+'\n'+key+': '+value
    sections = [
        ('Lecture Flow', ('0–20分：.pyを作って実行、20–40分：1コマ・ループ・アニメーション、40–70分：制作、70–90分：動作確認と上映、90–100分：最終作品のアイデア。',
                          '0–20 min: save and run a .py file. 20–40: frames, loops, animation. 40–70: build. 70–90: test and share. 90–100: final project idea.')),
        ('In-Class Notebook', ('hello.py を作り、ターミナルで実行。列車と雨のコード例を試す。','Save and run hello.py in your terminal. Try the train and rain examples.')),
        ('In-Class Challenge', BRIEF),
        ('Take-Home Assignment', HOMEWORK),
        ('Aha!', ('関数が1コマを作り、ループが次のコマを作る。','A function makes one frame. The loop asks for the next.')),
    ]
    agenda = '---'+front+'\n---\n'+''.join(f'## {name}\nEN: {en}\nJP: {ja}\n' for name,(ja,en) in sections)
    agenda += '''## Resources
- [Week 10 Lecture — ASCII Studio](weeks/week-10/lecture.html) {lecture}
- [最初の .py とコード例 / First .py and examples](weeks/week-10/challenge.html#first-file) {fundamentals}
- [チャレンジの手順 / Challenge Instructions](weeks/week-10/challenge.html) {challenge}
- [宿題・提出方法 / Homework and Submission](weeks/week-10/challenge.html#homework) {homework}
- [Final Project Requirements](content/final-project.md) {support}
'''
    c.write(source,agenda)
