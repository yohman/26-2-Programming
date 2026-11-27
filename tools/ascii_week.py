"""Build the Week 10 terminal lesson from its runnable Python examples."""
from pathlib import Path
import html
import json
import re
import subprocess
import sys
import zipfile

VERSION = '20261127-ascii-code-copy'
RELEASE = '2026-12-03T12:00:00+09:00'
DUE = '2026-12-09'
SLIDES = ['save', 'run', 'open', 'spaces', 'frame', 'loop', 'timer', 'train', 'parameters', 'route',
          'challenge', 'feedback', 'share', 'spinner', 'dot', 'emoji', 'rain', 'skyline', 'signal', 'launch']
SCRIPTS = ['hello.py', 'tiny.py', 'spinner.py', 'dot.py', 'emoji.py', 'train.py', 'route.py', 'rain.py', 'skyline.py', 'signal.py', 'launch.py']
TRAIN_CALLS = [('train', 18, 0.12), ('train-short', 8, 0.12), ('train-slow', 18, 0.25)]
SPEC = dict(title='ASCII Studio', title_ja='ASCIIスタジオ', date='2026-12-03', due=DUE, slides=SLIDES)
GOAL = (
    '.py ファイルを作り、ターミナルで実行。関数に渡す値を変えて、アニメーションを動かす。',
    'Create and run a .py file from the terminal, then change an animation by passing different values to a function.',
)
BRIEF = (
    'ターミナルで30秒の上映会。文字だけで、自分の場面と、見てわかる変化を作ろう。短いアニメでも、ループで描く一枚絵でもOK。',
    'Make a text-only scene for a 30-second terminal show-and-tell. Give it a change the audience can spot, in a short animation or a still built by a loop.',
)
REQUIREMENTS = [
    ('入力を受け取って1フレーム（または1行）の文字列を返す関数を作る。',
     'Write a function that takes an argument and returns the text for one frame or row.'),
    ('for ループで違う値を関数に渡し、位置・形・文字などを変えて表示する。',
     'Call it in a for loop with different values so the position, shape, or text changes.'),
    ('見どころを一つ作る。動画なら登場・点灯・到着など。静止画なら模様や形が切り替わる場所を作る。',
     'Give the audience one moment to notice: a character arrives, a sign lights up, or a still picture changes pattern at a chosen row.'),
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
    r'<code>train_frame()</code> は絵を1コマ返す。<code>animate_train()</code> はループで表示し、<code>sleep(delay)</code> で待つ。<code>\r</code> と <code>end=""</code> で同じ行に上書きし、<code>flush=True</code> ですぐに表示する。',
    r'<code>train_frame()</code> returns one drawing. <code>animate_train()</code> loops, displays each drawing, and waits at <code>sleep(delay)</code>. <code>\r</code> and <code>end=""</code> reuse the same line; <code>flush=True</code> shows it immediately.',
)
PARAMETER_HINT = (
    '<code>steps</code> は <code>range(steps)</code> に渡すコマ数。<code>delay</code> は <code>sleep(delay)</code> に渡す秒数。ボタンを押す前に、変わるのは距離か速さか予想しよう。',
    '<code>steps</code> supplies the frame count to <code>range(steps)</code>. <code>delay</code> supplies seconds to <code>sleep(delay)</code>. Before clicking, predict what changes: distance or speed?',
)
ROUTE_HINT = (
    '<code>stops</code> は停留所のリスト。外側の <code>for</code> で次の停留所へ。関数内の <code>if</code> が、いまの停留所にだけ <code>&gt;</code> を付ける。リストに「Cafeteria」を足すと？',
    '<code>stops</code> is a list. The outer <code>for</code> moves to the next stop; the <code>if</code> inside the function marks only the current one with <code>&gt;</code>. What happens if you add “Cafeteria” to the list?',
)
SPIN_HINT = (
    r'<code>\r</code> で行の先頭に戻り、次の記号で上書きする。<code>end=""</code> は改行なし、<code>flush=True</code> は待つ前に表示。最後の <code>print()</code> だけが改行する。',
    r'<code>\r</code> moves the cursor to the start of the line so the next symbol replaces the last one. <code>end=""</code> skips the newline, and <code>flush=True</code> shows the frame before the pause. The final <code>print()</code> adds a newline.',
)
TIME_HINT = (
    '<code>from time import sleep</code> で待つ関数を使える。<code>sleep(0.2)</code> はループの中で、表示するたびに0.2秒（200ミリ秒）待つ。0.8秒にすると、絵もコマ数も同じまま、動きが遅くなる。',
    '<code>from time import sleep</code> brings in the pause function. Inside the loop, <code>sleep(0.2)</code> waits 0.2 seconds (200 ms) after each print. At 0.8 seconds the frames stay the same, but the animation is slower.',
)
DOT_HINT = (
    '<code>position</code> が 0 から 11 へ増え、ドットの前の空白が1つずつ増える。<code>range(12)</code> はコマ数、<code>sleep(0.2)</code> はコマ間の待ち時間。',
    '<code>position</code> goes from 0 to 11, adding one blank before the dot each time. <code>range(12)</code> sets the number of frames. <code>sleep(0.2)</code> sets the pause between them.',
)
EMOJI_HINT = (
    '位置は固定。リストの次の表情に置き換える。絵文字は Unicode なので、ターミナルで絵文字が見えなければ <code>":)"</code> などでも試せる。',
    'The position stays fixed while the next face in the list replaces the previous one. Emoji are Unicode. If your terminal can’t display them, try faces like <code>":)"</code>.',
)
TINY_HINT = (
    'スピナーは <code>| / - \\</code> を順番に出す。ドットは空白の数、絵文字はリストの何番目を選ぶかで変わる。絵文字はASCIIではなく、端末によって幅が違うことがある。',
    'The spinner cycles through <code>| / - \\</code>. Spaces move the dot, and a list supplies the faces. Emoji are Unicode and may take up different widths in different terminals.',
)
RAIN_HINT = (
    r'雨の行だけを変えて、屋根は固定。<code>\033[2J\033[H</code> はターミナルを消去して左上に戻す合図。複数行を描き直したいときだけ使う。',
    r'Change the rain while the roof stays still. <code>\033[2J\033[H</code> clears the terminal and moves the cursor to the top left. Use it only when you want to redraw several lines.',
)
SKYLINE_HINT = (
    '<code>level</code> は今描く段。ループは各ビルの高さを調べ、届くなら <code>[#]</code>、届かないなら空白にする。',
    '<code>level</code> is the row being drawn. For each building, the loop adds <code>[#]</code> if the building reaches that level, or spaces if it doesn’t.',
)
SIGNAL_HINT = (
    '位置は変えず、<code>active</code> と同じ行だけに <code>*</code> を表示する。リストの順番を変えると、何が変わる？',
    'Nothing moves across the screen. Only the row that matches <code>active</code> gets a <code>*</code>. What happens if you change the order of the states?',
)
LAUNCH_HINT = (
    '外側の <code>for step</code> が時間を進める。<code>flight_frame</code> の中の <code>for y</code> は一コマを上から1行ずつ描き、必要な行にだけロケットを重ねる。',
    'The outer <code>for step</code> advances time. Inside <code>flight_frame</code>, <code>for y</code> builds one frame top to bottom and overlays the rocket only on the rows it occupies.',
)
PITCHES = (
    'たとえば、終電の発車案内、3秒で変身するキャラクター、1軒だけ明かりがつく夜の街。テーマは自由。サンプルを使うなら文字を置き換えるだけでなく、変化のルールを一つ変える。',
    'Try a last-train departure board, a character that transforms on cue, or a skyline with one lit window. Your own idea is welcome. If you start from an example, change a rule that controls what we see.',
)
FEEDBACK = (
    '完成前でOK。近くの人とペアになり、手元のターミナルで作品を動かして見せる。',
    'Works in progress are welcome. Pair up with someone nearby and run your work in your own terminal.',
)
FEEDBACK_STEPS = [
    ('<strong>4分：</strong> Aさんが実行。Bさんは「何が変わったか」と「もっと見やすくする案」を一つずつ伝える。',
     '<strong>4 min:</strong> A runs their script. B says what changed and suggests one way to make it clearer.'),
    ('<strong>4分：</strong> 交代。Bさんが実行し、Aさんが感想と提案を伝える。',
     '<strong>4 min:</strong> Switch. B runs their script and A gives feedback.'),
    ('<strong>2分：</strong> 上映までに直すことを、各自一つ決める。',
     '<strong>2 min:</strong> Each pick one thing to revise before the show-and-tell.'),
]
STRETCH = (
    '発展：背景と動くものを別々の関数で作る。位置が端に着いたら、台詞や次の場面を切り替える。',
    'Stretch: draw the background and moving object in separate functions, or switch the caption or scene when the object reaches an edge.',
)


def output(source):
    """Run a trusted example in a fresh interpreter and capture its stdout."""
    return subprocess.run([sys.executable, '-c', source], capture_output=True,
                          check=True, timeout=10).stdout.decode('utf-8')


def frames(source, separator, *, delay_seconds=None):
    """Keep the frame text and timing from the same code the students receive."""
    text = output(source)
    if delay_seconds is None:
        args = re.findall(r'^ +sleep\(([\d.]+)\)$', source, re.M)
        assert len(args) == 1
        delay_seconds = float(args[0])
    pictures = text.split(separator)[1:]
    if separator == '\r':
        pictures[-1] = pictures[-1].rstrip('\n')
    return {'frames': pictures, 'delay': round(delay_seconds * 1000)}


def build(root: Path, c):
    dest = root/'weeks/week-10'
    hello, tiny, spinner, dot, emoji, train, route, rain, skyline, signal, launch = [
        (dest/name).read_text(encoding='utf-8').rstrip() for name in SCRIPTS
    ]
    hello_output = output(hello)
    train_body, default_call = train.rsplit('\n', 1)
    train_calls = [(name, f'animate_train({steps}, {delay})') for name, steps, delay in TRAIN_CALLS]
    assert default_call == train_calls[0][1]
    demos = {
        name: frames(train_body + '\n' + call, '\r', delay_seconds=delay)
        for (name, call), (_, _, delay) in zip(train_calls, TRAIN_CALLS)
    }
    demos.update(route=frames(route, '\x1b[2J\x1b[H'), rain=frames(rain, '\x1b[2J\x1b[H'))
    demos.update(tiny=frames(tiny, '\x1b[2J\x1b[H'), signal=frames(signal, '\x1b[2J\x1b[H'),
                 launch=frames(launch, '\x1b[2J\x1b[H'))
    demos.update(spinner=frames(spinner, '\r'), dot=frames(dot, '\r'), emoji=frames(emoji, '\r'))
    frame_def = train[train.index('# 空白'):train.index('# 1コマずつ')].rstrip()
    one_frame = frame_def + '\n\n# 同じ関数に違う値を渡して表示\nprint(train_frame(0))\nprint(train_frame(6))'
    frame_loop = frame_def + '\n\n# 位置を変えて、1コマずつ別の行に表示\nfor position in range(0, 10, 3):\n    print(train_frame(position))'
    one_dot = 'print(".")\nprint("🙂")'
    dots = 'print("." * 5)\nprint(" " * 4 + ".")'
    spin_steps = 'for symbol in ["|", "/", "-", "\\\\"]:\n    print(symbol)'
    skyline_output = output(skyline)
    examples = [(hello, hello_output), (one_dot, output(one_dot)), (dots, output(dots)), (spin_steps, output(spin_steps)),
                (one_frame, output(one_frame)), (frame_loop, output(frame_loop)), (skyline, skyline_output)]
    launch_code = launch[launch.index('def flight_frame'):launch.index('\n\nfor step')]
    bi, p = c.bi, c.p
    heading = lambda ja, en: '<h2>'+bi(ja, en)+'</h2>'
    cmd = c.code_html(COMMANDS, language='shell')
    links = lambda items: c.links(items)
    assets = f'<link rel="stylesheet" href="ascii.css?v={VERSION}"><script src="ascii.js?v={VERSION}" defer></script>'
    header = '<header class="lecture-header"><a id="lecture-return" class="return-link" href="../../agenda.html?open=10#week-10">← '+bi('授業予定','Agenda')+'</a><span class="lecture-mark">PRG / 26–2</span><button id="language-toggle" class="language-toggle" type="button" aria-label="Switch language">EN</button></header>'
    slides = {}

    def demo(name, mode='', delays=(), variants=()):
        example = demos[name]
        first = html.escape(example['frames'][0].rstrip('\n'))
        target = f'ascii-{name}-{mode}'
        if variants:
            controls = ''.join(
                f'<button data-ascii-play data-ascii-variant="{variant}" type="button" aria-controls="{target}" aria-pressed="false">▶ <code>{call}</code></button>'
                for variant, call in variants
            )
            label = ''
        elif delays:
            controls = ''.join(f'<button data-ascii-play="{ms}" type="button" aria-controls="{target}">▶ {ms/1000:g} s</button>'
                               for ms in delays)
            label = f'<code class="ascii-delay" data-ascii-delay>sleep({example["delay"]/1000:g})</code>'
        else:
            controls = f'<button data-ascii-play type="button" aria-controls="{target}">▶ '+bi('再生','Play')+'</button>'
            label = ''
        return (f'<div class="ascii-demo {mode}" data-ascii-demo="{name}"><div class="ascii-preview">'
                f'<pre id="{target}" class="ascii-output" tabindex="0">{first}</pre></div>'
                '<div class="ascii-actions">'+controls
                +f'<button data-ascii-step type="button" aria-controls="{target}">'+bi('1コマ進む','Next frame')+'</button>'
                +f'<span data-ascii-index>01 / {len(example["frames"]):02d}</span>{label}</div></div>')

    def add(key, ja, en, body, layout=''):
        assert key not in slides
        tag = 'h1' if key == SLIDES[0] or layout == 'curtain' else 'h2'
        slides[key] = f'<section class="slide lesson-slide ascii-slide ascii-{layout or "plain"}" data-slide data-ink-id="w10-ascii-{key}" hidden><{tag}>{bi(ja,en)}</{tag}>{body}</section>'

    note = p('Pythonで実行した出力をブラウザで再生。','The browser replays output captured from Python.','simulation-note')
    add('open','回る、動く、表情が変わる','A spinner, a dot, an emoji',
        demo('tiny','opening')
        +p('hello.py が動いた。次は「1回表示する」を「変えながら何回か表示する」に。変わったのは、記号？ 位置？ 表情？',
           'You ran hello.py. Now go from showing something once to showing it several times with a change. What changed: the symbol, the position, or the face?','ascii-caption'), 'curtain')
    add('save','最初のファイル：hello.py','The first file: hello.py',
        c.code_html(*examples[0])+p(*SAVE,'ascii-caption'), 'code')
    add('run','ターミナルから起動','Running from the terminal',
        p(*RUN)+cmd+'<pre class="ascii-hello-output">'+html.escape(hello_output.strip())+'</pre>'
        +p('Notebookと違い、最後に値を書くだけでは表示されない。ターミナルに出すときは print()。','A script won’t display a bare value like a notebook cell does. Use print() to show it.','ascii-caption')
        +'<details><summary>'+bi('うまく動かないとき','If it doesn’t run')+'</summary>'+p(*FIX)+'</details>', 'command')
    add('spaces','ドットはどこに出る？','Where will the dot land?',
        c.code_html(one_dot,output(one_dot))+c.code_html(dots,output(dots))
        +p('文字 × 数は繰り返し。空白も1文字。2つ目のコードは、何でドットを右に動かしている？',
           'A string times a number repeats it. A space is a character too. In the second example, what moves the dot to the right?','ascii-caption'), 'code')
    add('spinner','4文字で回転','Four characters make a spinner',
        demo('spinner','single')+c.code_html(spinner)+p(*SPIN_HINT,'ascii-caption')+note, 'example')
    add('timer','タイマー：1コマごとの待ち時間','The timer: a pause between frames',
        p('1コマを表示し、少し待ってから次のコマへ。','Draw a frame, pause, then draw the next one.','lesson-lead')
        +demo('spinner','timing',(200,800))+p(*TIME_HINT,'ascii-caption')
        +p('予想：sleep をループの外に出すと？','Prediction: what changes if you move sleep outside the loop?','ascii-caption'), 'timing')
    add('dot','空白が1つ増えるたびに','One more space moves the dot',
        demo('dot','single')+c.code_html(dot)+p(*DOT_HINT,'ascii-caption')+note, 'example')
    add('emoji','同じ場所、違う表情','One spot, changing faces',
        demo('emoji','single')+c.code_html(emoji)+p(*EMOJI_HINT,'ascii-caption')+note, 'example')
    add('frame','空白の数で列車を置く','Spaces place the train',
        c.code_html(one_frame,output(one_frame))+p('<code>position</code> は値を受け取る引数の名前。呼び出すときに渡す <code>0</code> と <code>6</code> が空白の数になる。<code>return</code> はできた文字列を返し、<code>print</code> が画面に出す。',
                                                 '<code>position</code> is the parameter: the name in the definition. <code>0</code> and <code>6</code> are the arguments: the values passed in. <code>return</code> gives back the string; <code>print</code> puts it on screen.','ascii-caption'), 'code')
    add('loop','ループで位置を変える','The loop changes the position',
        c.code_html(frame_loop,output(frame_loop))+p('関数は1コマを作る。for は位置を変えて、同じ関数を何度も呼ぶ。まず別々の行に描いてみよう。',
                                                     'The function makes one frame. The loop calls it with a new position each time. First, print each frame on a separate line.','ascii-caption'), 'code')
    add('train','列車を動かす関数','A function that moves the train',
        demo('train','compact')+c.code_html(train)+p(*TRAIN_HINT,'ascii-caption')
        +p('動いているプログラムを止めるには Ctrl+C。','Press Ctrl+C in the terminal to stop a running script.','ascii-caption')+note, 'example')
    add('parameters','短くする？ ゆっくりにする？','Shorter run or slower train?',
        demo('train','calls',variants=train_calls)+p(*PARAMETER_HINT,'ascii-caption')
        +p('train.py に保存して実行。最後の呼び出しだけを変えて、ターミナルでも比べよう。',
           'Save the previous example as train.py and run it. Edit only the call at the bottom and compare in the terminal.','ascii-caption')+note, 'timing')
    add('route','次はどの停留所？','What’s the next stop?',
        demo('route','compact')+c.code_html(route)+p(*ROUTE_HINT,'ascii-caption')+note, 'example')
    add('rain','屋根はそのまま、雨だけ動く','A still roof, moving rain',
        demo('rain','compact')+c.code_html(rain)+p(*RAIN_HINT,'ascii-caption')+note, 'example')
    add('skyline','高さのリストで街を描く','A skyline from a list of heights',
        c.code_html(skyline,skyline_output)+p(*SKYLINE_HINT,'ascii-caption'), 'code')
    add('signal','同じ絵、違う状態','One picture, changing states',
        demo('signal','compact')+c.code_html(signal)+p(*SIGNAL_HINT,'ascii-caption')+note, 'example')
    add('launch','ロケットの1コマは何行？','How does the rocket get into each frame?',
        demo('launch','wide')+c.code_html(launch_code)+p(*LAUNCH_HINT,'ascii-caption')+note
        +links([('challenge.html#launch','ロケットの全コード','Full rocket script')]), 'example')
    add('challenge','30分：ターミナル上映会','30 minutes: Terminal show-and-tell',
        p(*BRIEF,'lesson-lead')+p('20分で作る → 残り10分でペアに見せる。','Build for 20 minutes, then spend 10 minutes trying each other’s work.','ascii-caption')
        +c.list_html(REQUIREMENTS)+p(*PITCHES)+links([('challenge.html#make','チャレンジの手順・コード例','Challenge instructions and examples')]), 'challenge')
    add('feedback','10分：ペアで見せ合う','10 minutes: Try it with a partner',
        p(*FEEDBACK,'lesson-lead')+c.list_html(FEEDBACK_STEPS)
        +p('次の5分で一つ直して、もう一度動かそう。','Use the next five minutes to make one revision and run it again.','ascii-caption'), 'challenge')
    add('share','上映と提出','Showtime and submission',
        p('発表は30秒。ターミナルで実行し、関数に渡す値で何が変わるか一言。','For the 30-second share-out, run the script and say what changes when you pass a different value to the function.','lesson-lead')
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
    assert set(slides) == set(SLIDES)
    c.write(dest/'lecture.html',head+assets+f'</head><body class="lecture-page course-deck ascii-week" data-week="10" data-release="{RELEASE}">'
            +header+'<main><div id="slides-view" class="view">'+nav+'<div class="slide-stage">'+''.join(slides[key] for key in SLIDES)+'</div></div></main>'
            +'<script type="application/json" id="lesson-data">{}</script>'+data+'</body></html>\n')

    body = p(*BRIEF)+'<section id="first-file">'+heading('最初の .py','Your first .py')+p(*SAVE)+c.code_html(hello)+p(*RUN)+cmd
    body += '<pre class="ascii-hello-output">'+html.escape(hello_output.strip())+'</pre>'
    body += ('<details><summary>'+bi('うまく動かないとき','If it doesn’t run')+'</summary>'+p(*FIX)
             +p('<a href="https://code.visualstudio.com/docs/python/run">VS Code公式：Pythonを実行する</a>',
                '<a href="https://code.visualstudio.com/docs/python/run">VS Code documentation: Running Python code</a>')
             +'</details></section>')
    body += '<section id="examples">'+heading('ASCII作品のサンプル','ASCII examples')
    body += p('コードをコピーして、見出しの名前で保存。hello.py と同じように、コマンドのファイル名を変えて実行する。','Copy the code and save it using the name shown above each script. Run it like hello.py, replacing the file name in the command.')
    for name, code, hint in [('train',train,TRAIN_HINT),('route',route,ROUTE_HINT),
                             ('tiny',tiny,TINY_HINT),('spinner',spinner,SPIN_HINT),('dot',dot,DOT_HINT),('emoji',emoji,EMOJI_HINT),
                             ('rain',rain,RAIN_HINT),
                             ('skyline',skyline,SKYLINE_HINT),('signal',signal,SIGNAL_HINT),
                             ('launch',launch,LAUNCH_HINT)]:
        body += f'<h3 id="{name}">{name}.py</h3>'
        if name == 'skyline':
            body += '<div class="ascii-preview"><pre class="ascii-output">'+html.escape(skyline_output.rstrip('\n'))+'</pre></div>'
        else:
            body += demo(name,'page',variants=train_calls if name == 'train' else ())
        body += c.code_html(code)+p(*hint)+(note if name != 'skyline' else '')
        if name == 'train':
            body += p(*PARAMETER_HINT)
        if name == 'spinner':
            body += p(*TIME_HINT)
    body += links([('starter-files.zip','サンプル .py（ZIP）','Example scripts (ZIP)')])+'</section>'
    body += '<section id="make">'+heading('20分：作品を作る','20 minutes: Build your piece')+p(*PITCHES)+c.list_html(REQUIREMENTS)
    body += p('新しい ascii.py を作る。まず関数で1コマを描き、次に2つの引数で呼び出して違いを確認。最後にループでつなげて、ターミナルから実行する。',
              'Create a new ascii.py. Make one frame with a function, then call it with two different values and check what changes. Finally, connect the frames in a loop and run the script from the terminal.')
    body += p(*STRETCH)+'</section>'
    body += '<section id="feedback">'+heading('10分：ペアで見せ合う','10 minutes: Try it with a partner')+p(*FEEDBACK)+c.list_html(FEEDBACK_STEPS)
    body += p('次の5分で一つ直して、もう一度動かそう。','Use the next five minutes to make one revision and run it again.')+'</section>'
    body += '<section id="homework">'+heading('宿題・提出','Homework and submission')+p(*HOMEWORK)+p(f'締切：{DUE} 23:59 JST',f'Due: {DUE}, 23:59 JST')+'</section>'
    head = c.page_head('Week 10 challenge · ASCII Studio','course-pages.css','course-page.js',VERSION)
    c.write(dest/'challenge.html',head+assets+f'</head><body class="course-challenge ascii-week" data-release="{RELEASE}">'+header
            +'<main id="course-page" hidden><h1>'+bi(SPEC['title_ja'],SPEC['title'])+'</h1>'+body
            +links([('lecture.html','講義スライド','Lecture slides')])+'</main>'+data+'</body></html>\n')

    cells = [c.mdcell('# ASCII Studio\n\n授業の提出形式は .py です。スライドとチャレンジページの手順に沿ってターミナルで実行しましょう。\n\nThis notebook is a reference. Save and run your own .py in a terminal for the assignment.')]
    cells += [c.codecell(code,result,i) for i,(code,result) in enumerate(examples,1)]
    cells += [c.mdcell('## Terminal examples\n\n'+''.join(f'### {name}\n\n```python\n{code}\n```\n\n' for name,code in zip(SCRIPTS[1:],[tiny,spinner,dot,emoji,train,route,rain,skyline,signal,launch])))]
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
        ('Lecture Flow', ('0–15分：.pyを作って実行、15–40分：関数・引数・ループ、40–60分：制作、60–70分：ペアで感想、70–75分：修正、75–90分：上映、90–100分：最終作品のアイデア。',
                          '0–15 min: create and run a .py file. 15–40: functions, arguments, and loops. 40–60: build. 60–70: partner feedback. 70–75: revise. 75–90: show-and-tell. 90–100: final project idea.')),
        ('In-Class Notebook', ('hello.py から始めて、train.py の引数でコマ数と速さを変える。route.py ではリストと if で停留所を表示。',
                               'Start with hello.py, then change the train’s frame count and speed with arguments. Use a list and an if statement to make a shuttle display.')),
        ('In-Class Challenge', BRIEF),
        ('Take-Home Assignment', HOMEWORK),
        ('Aha!', ('関数の中身はそのまま。渡す値を変えるだけで動きが変わる。','Keep the function the same. Change what it does by passing in different values.')),
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
