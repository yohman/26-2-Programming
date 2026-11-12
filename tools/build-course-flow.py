"""Build Weeks 07–14 HTML lessons, aligned notebooks, challenge pages and panels.

Only trusted course examples are executed. Original archive notebooks/PDFs are kept.
Rebuild: admin/.venv/bin/python tools/build-course-flow.py
"""
from pathlib import Path
import contextlib, csv, html, io, json, re, shutil, zipfile, sys
import weather_hackathon
from urllib.parse import urljoin, urlencode

ROOT = Path(__file__).resolve().parents[1]
VERSION = '20261107-menu'
MENU = [
    ('Onigiri',150,3,'food'),('Sandwich',320,5,'food'),('Curry',550,12,'food'),
    ('Udon',450,10,'food'),('Bento',650,8,'food'),('Salad',280,4,'food'),
    ('Water',100,2,'drink'),('Tea',130,2,'drink'),('Coffee',180,5,'drink'),
    ('Juice',160,2,'drink'),('Soup',220,4,'food'),('Bread',190,3,'food'),
    ('Pasta',700,15,'food'),('Ramen',800,18,'food'),('Fruit',250,3,'food'),
    ('Yogurt',170,2,'food'),('Rice bowl',600,10,'food'),('Toast',300,7,'food'),
    ('Cookie',120,2,'snack'),('Ice cream',230,3,'snack'),('Chocolate',140,2,'snack'),
    ('Bookshop browse',0,20,'activity'),('Park walk',0,30,'activity'),('Arcade round',200,10,'activity')]
MENU_DICTS=[dict(name=n,price=p,minutes=m,category=c) for n,p,m,c in MENU]
SMALL=MENU_DICTS[:4]
LOAD='''import csv

with open("student-menu.csv", encoding="utf-8-sig", newline="") as file:
    menu = list(csv.DictReader(file))

for item in menu:
    item["price"] = int(item["price"])
    item["minutes"] = int(item["minutes"])

print(len(menu), "options")'''
SMALL_CODE='''menu = [
    {"name": "Onigiri", "price": 150, "minutes": 3},
    {"name": "Sandwich", "price": 320, "minutes": 5},
    {"name": "Curry", "price": 550, "minutes": 12},
    {"name": "Udon", "price": 450, "minutes": 10}
]'''
AFFORD='''def affordable(items, budget):
    chosen = []
    for item in items:
        if item["price"] <= budget:
            chosen.append(item["name"])
    return chosen'''
REMAIN='''def remaining(budget, price):
    balance = budget - price
    return balance'''
BOXES=[dict(x=40,y=30,w=80,h=90),dict(x=180,y=50,w=60,h=70),dict(x=320,y=25,w=100,h=110)]
def bi(ja,en): return f'<span class="ja">{ja}</span><span class="en">{en}</span>'
def p(ja,en,cls=''): return f'<p class="{cls}">{bi(ja,en)}</p>'
def list_html(items): return '<ul>'+''.join('<li>'+bi(*i)+'</li>' for i in items)+'</ul>'
def links(items,week=None,return_page='challenge.html'):
    rendered=[]
    for u,j,e in items:
        if week is not None and re.search(r'\.(ipynb|csv|json)$',u):
            file=urljoin(f'weeks/week-{week:02}/',u)
            preview='../../viewer.html?'+urlencode(dict(file=file,title=j+' / '+e,**{'return':f'weeks/week-{week:02}/'+return_page}))
            rendered.append('<div class="lesson-file"><span>'+bi(j,e)+'</span><a href="'+html.escape(preview,quote=True)+'">'+bi('プレビュー','Preview')+'</a><a href="'+html.escape(u,quote=True)+'" download>'+bi('ダウンロード','Download')+'</a></div>')
        else:
            rendered.append(f'<a href="{u}"'+(' download' if re.search(r'\.(ipynb|csv|py|zip)$',u) else '')+f'>{bi(j,e)} ↗</a>')
    return '<div class="lesson-links">'+''.join(rendered)+'</div>'

def slide(title,ja,en='',layout='plain',code=None,**kwargs):
    return dict(title=title,ja=ja,en=en or ja,layout=layout,code=code,**kwargs)
def C(title,ja,en,code,**kw): return slide(title,ja,en,'code',code,**kw)
def Q(title,ja,en,answer):return slide(title,ja,en,'question',answer=answer)
def H(title,ja,en,**kw):return slide(title,ja,en,'hero',**kw)
def CH(ja,en):return slide('30 MIN / CHALLENGE',ja,en,'challenge')
W={}

W[7]=weather_hackathon.SPEC

W[8]=dict(title='Make it work for a friend',title_ja='友だちの条件でも使える？',date='2026-11-19',due='2026-11-25',
 aim=('先週のプログラムを、違う条件でも使えるように直す。','Make last week’s program work for different settings.'),
 flow=('0–10：動作チェック、10–22：同じ処理を関数に、22–60：改善、60–78：ペアテスト、78–93：見せ合う、93–100：保存。','0–10 run check; 10–22 one small function; 22–60 improve; 60–78 peer test; 78–93 share; 93–100 save.'),
 brief=('予算ツールを、友だちが条件を変えて使えるようにする。先週の提出がなくても、今日のスターターから始められる。自転車盗データの集計は選択課題。','Make a budget tool a friend can use with different settings. Start with today’s notebook even without last week’s work. Bicycle-theft counting is an alternative challenge.'),
 requirements=[('二つの予算（事件課題は二つの集計列）で使い、違いを説明する。','Run two budgets, or two grouping columns for incident data, and explain the difference.'),('候補0件・対象0行でも、読み手に伝わる結果を出す。','Give an understandable result when no options or records match.'),('一つの処理を関数にし、相手に試してもらって一か所直す。','Put one operation in a function; improve one issue found by a partner.')],
 homework=('授業の同じ作品を改善し、変更前後・通常と候補0件の確認・相手の反応を短く記録。実行済みNotebookと必要なデータをUNIPAへ。','Improve the same work and record before/after, normal/no-match checks and a partner’s feedback. Submit the executed notebook and needed data to UNIPA.'),
 slides=[
 H('「これ、使っていい？」','説明なしで、友だちは動かせる？','Can a friend use it without your explanation?'),
 Q('誰の予算？','自分の500円をコードの3か所で変えている。友だちは700円。どこを直す？','You copied the ¥500 budget into three places. A friend has ¥700. What must change?',('一つのbudget変数へまとめる。次に繰り返す処理を関数へ。','Use one budget variable, then put repeated work into a function.')),
 C('同じ引き算を一つに','defは処理の定義。呼ぶまで動かない。budgetとpriceは受け取る値。returnは結果を呼び出し元へ返す。','def defines the operation; calling runs it. Parameters receive values; return sends the result back.',REMAIN+'\n\nprint(remaining(1000, 470))\nprint(remaining(700, 470))'),
 slide('中に入る値、戻る値','引数→計算→returnを一段ずつ追う。','Step through arguments, calculation and return.','interactive',demo='call'),
 C('候補0件を伝える','空のリストはFalseとして扱える。not chosenなら一件もなかった。','An empty list is falsey; not chosen means no item matched.', 'chosen = []\nfor item in menu:\n    if item["price"] <= 0:\n        chosen.append(item["name"])\nif not chosen:\n    print("No options. Try another budget.")'),
 slide('2つのテスト','通常：500円で候補がある。境界：150円でOnigiriが入る。0円の結果は、使ったデータに0円の活動があるかでも変わる。','Normal: ¥500 finds options. Boundary: ¥150 includes Onigiri. A ¥0 result depends on whether your data includes free activities.','comparison'),
 C('結果を、目で照合する','assertは条件が違えば止まる確認。まず手で計算してから書く。','assert stops when a check is false. Calculate the expected answer first.', 'assert remaining(1000, 470) == 530\nassert remaining(470, 470) == 0\nprint("Two checks passed")'),
 slide('選択課題：自転車をどこに停める？','千葉県警の事件データで、発生場所別の件数を数える。事件の件数から盗まれる確率は計算できない。','Count reported bicycle thefts by place. Incident counts cannot establish the risk per parked bicycle.','data',extra=links([('../week-08/bicycle-theft-guide.ipynb','CSV集計のスターター','Counting notebook')],8,'lecture.html')),
 C('集計も、同じfor','この3行は説明用の小さな例。完全な事件データは選択Notebookで読み込む。','These three rows are a teaching example. The alternative notebook loads the actual incident CSV.', 'places = ["Parking", "Road", "Parking"]\ncounts = {}\nfor place in places:\n    counts[place] = counts.get(place, 0) + 1\nprint(counts)'),
 CH('予算ツールを改善するか、事件データを集計する。どちらも「条件を変えた結果」を一つ示そう。','Improve the budget tool or count incident data. Show how one changed setting changes the result.'),
 slide('ペアテストは、実況しない','操作する人は読みながら使う。作った人は観察し、詰まった場所を一つメモする。','Let the tester read and use it. The author watches and notes one obstacle.','pair'),
 slide('直した一か所を見せる','変更前→変更後→確認した結果。次回は、この処理をもっと分かりやすく関数へまとめる。','Before → after → checked result. Next week we make the function-and-loop relationship explicit.','exit')])

W[9]=dict(title='One function, many calls',title_ja='関数を一つ、何度でも',date='2026-11-26',due='2026-12-02',
 aim=('引数と戻り値を追い、ループ内から関数を呼び、関数の中のループも説明する。','Trace arguments and returns; distinguish a loop calling a function from a loop inside a function.'),
 flow=('0–8：予想、8–23：定義・呼び出し・return、23–40：関数とループの追跡、40–55：Notebookで修正、55–85：チャレンジ、85–100：確認・説明。','0–8 predict; 8–23 definition/call/return; 23–40 trace functions and loops; 40–55 notebook changes; 55–85 challenge; 85–100 verify and explain.'),
 brief=('先週のメニューを使い、予算を受け取って候補のリストを返す関数を作る。500円、700円、1,000円を外側のforで順に渡す。','Use the familiar menu to write a function receiving a budget and returning a list. Call it for ¥500, ¥700 and ¥1,000 in an outer for loop.'),
 requirements=[('引数とreturnを持つ関数を一つ作る。','Write one function with a parameter and a return value.'),('外側のforから3回呼び、呼ぶたびに値が変わる様子を示す。','Call it three times from an outer loop and show the changing results.'),('通常・境界・候補0件を確認し、returnの位置を説明する。','Check normal, boundary and no-match cases; explain the position of return.')],
 homework=('同じ関数に時間の条件を追加するか、自分のテーマの関数へ変える。3回の呼び出し、3件の確認、引数→処理→戻り値の説明を保存してUNIPAへ。','Add a time condition or adapt the function to your own topic. Save three calls, three checks and an explanation of input → process → return; submit to UNIPA.'),
 slides=[
 H('3人、3つの予算','Takumaは500円、Yukiは700円、Masakiは1,000円。練習用の架空設定。同じコードを3回コピーする？','Fictional practice budgets: Takuma ¥500, Yuki ¥700, Masaki ¥1,000. Copy the same code three times?',stamp='500 / 700 / 1000'),
 C('まず、知っている処理','価格を調べ、候補を集める。この処理を名前で呼べるようにしたい。','Inspect prices and collect matching names. Give this process a name.', 'chosen = []\nfor item in menu:\n    if item["price"] <= 500:\n        chosen.append(item["name"])\nprint(chosen)'),
 C('defは、まだ実行しない','字下げ部分を関数として保存する。名前の後の()で初めて呼び出す。','The indented body is defined here. Parentheses on a call run it.',REMAIN+'\n\nprint("Function defined; body not called yet")'),
 C('引数を渡す','1000→budget、470→price。引数は呼び出す側の値、仮引数は関数内の受け口。','1000 becomes budget; 470 becomes price. Arguments are supplied values; parameters are the names receiving them.', 'balance = remaining(1000, 470)\nprint(balance)'),
 slide('呼び出しを、スロー再生','関数へ入り、計算し、returnで元の場所へ戻る。','Enter, calculate, then return to the caller.','interactive',demo='call'),
 C('printとreturnは役割が違う','printは画面へ表示。returnは次の計算で使う値を返す。returnがなければNoneが返る。','print displays; return supplies a reusable result. With no explicit return, the result is None.', 'def show_balance(budget, price):\n    print(budget - price)\n\nresult = show_balance(1000, 470)\nprint("result:", result)'),
 Q('このresultは？','returnのあるremaining(1000, 470)なら、resultには何が入る？','What would result contain with remaining(1000, 470), which uses return?',('530。画面に出るだけでなく、result + 100のように使える。','530. It can be reused in an expression such as result + 100.')),
 C('関数の中にfor','関数全体で一つの予算を処理。chosen=[]は毎回の呼び出しで作り直す。','One call processes one budget. chosen=[] creates a fresh list each time.', AFFORD+'\n\nprint(affordable(menu, 500))'),
 slide('1回の呼び出しを数える','4品を調べて、一つのリストを返す。returnはforと同じ字下げの外側。','Inspect four items and return one list. return is outside the for body.','path',extra='<div class="process-line"><span>budget = 500</span><b>→</b><span>4 items</span><b>→</b><span>[Onigiri, Sandwich, Udon]</span></div>'),
 C('外側のforから関数を呼ぶ','forが予算を一つずつ取り出す。関数がその予算の候補を返す。','The outer for supplies one budget; the function returns that budget’s choices.', 'for budget in [500, 700, 1000]:\n    names = affordable(menu, budget)\n    print(budget, names)'),
 slide('ループ × 関数を追跡','呼び出し元のbudgetと、関数の中のitem・chosenを分けて見る。','Watch caller budget separately from local item and chosen.','trace',trace='loopcalls'),
 Q('何回、価格を見る？','メニュー4品×予算3つ。関数呼び出しは何回？価格の比較は何回？','Four menu items, three budgets. How many calls and price comparisons?',('呼び出し3回、比較12回。関数の定義は1回。','Three calls, twelve comparisons, one definition.')),
 C('returnが早すぎる','この例では最初の品だけでreturnする。修正前の結果を予想する。','This version returns after the first item. Predict the bug before fixing it.', 'def too_early(items, budget):\n    chosen = []\n    for item in items:\n        if item["price"] <= budget:\n            chosen.append(item["name"])\n        return chosen\n\nprint(too_early(menu, 500))'),
 C('空の入力も、結果を返す','returnをループの外へ置くと、空のリストでも[]を返す。','With return after the loop, an empty input still returns [].', 'assert affordable([], 500) == []\nassert affordable(menu, 149) == []\nassert affordable(menu, 150) == ["Onigiri"]\nprint("Three checks passed")'),
 slide('値は、呼び出すたびに変わる','処理の定義は共通。引数が変わる。ローカルのchosenは毎回新しい。結果は外側のnamesへ戻る。','The definition stays the same. Arguments change. Each call gets a new chosen list; its result returns to names.','comparison'),
 CH('affordable(items, budget)を作り、外側のforで3つの予算を渡す。発展：max_minutesも引数へ。','Build affordable(items, budget), then pass three budgets from an outer loop. Extension: add max_minutes.'),
 slide('相手に説明する3行','「どこから呼ぶ？」「何を渡す？」「何が戻る？」をコード上で指さす。日本語で説明してOK。','Point to the caller, argument and returned value. Explain in Japanese if you prefer.','pair'),
 slide('次回は、Cellの外へ','今日の関数を.pyへ保存して実行する。同じPythonがNotebookの外でも動く。','Next week, save the function in a .py file and run the same Python outside a notebook.','exit')])

W[10]=dict(title='Python outside the notebook',title_ja='Notebookの外でPythonを動かす',date='2026-12-03',due='2026-12-09',
 aim=('関数を.pyへ保存し、Terminalから実行し、他のファイルからimportする。','Save a .py script, run it in a terminal, and import a function from another file.'),
 flow=('0–10：関数の復習、10–25：.pyを保存・実行、25–40：入力とimport、40–70：チャレンジ、70–90：相手のPC想定で確認、90–100：最終作品の問いを一つ。','0–10 function review; 10–25 save/run .py; 25–40 input/import; 40–70 challenge; 70–90 portability checks; 90–100 choose one final-project question.'),
 brief=('予算ツールを.pyにし、Terminalから実行する。Notebookも一緒に使い、何を入力し何が返ったかを記録する。','Turn the budget tool into a script and run it in a terminal. Keep a notebook recording inputs and results.'),
 requirements=[('hello.pyを自分で保存し、Terminalで実行する。','Save hello.py yourself and run it in the terminal.'),('budget_tool.pyを二つの予算で実行し、関数をNotebookからimportする。','Run budget_tool.py with two budgets; import its function into a notebook.'),('必要なファイル・実行コマンド・確認結果を記録する。','Record required files, launch commands and checked results.')],
 homework=('.py・必要なCSV・実行記録Notebookを提出。通常の入力と不正な入力を確認し、最終作品の「読み手と問い」を一つ添える。GUIは不要。UNIPAへ。','Submit the .py, needed CSV and execution-record notebook. Check normal/invalid input and add one final-project audience and question. A GUI is not required. Submit to UNIPA.'),
 slides=[
 H('▶のない場所で、動かす','保存したファイルが、一つのプログラムになる。','A saved file becomes a runnable program.'),
 slide('.ipynb と .py','Notebookは説明・Code Cell・出力を一緒に保存。.pyはPythonコードを保存するテキストファイル。上から順に実行される。','A notebook stores explanations, cells and outputs. A .py file stores Python code, executed from the top.','comparison',extra='<div class="process-line"><span>report.ipynb<br>Markdown + Python + outputs</span><b>↔</b><span>hello.py<br>Python code</span></div>'),
 C('hello.pyを作る','VS Codeで新規ファイル→hello.pyという名前で保存。Code Cellの```やMarkdown説明は入れない。.py.txtになっていないか確認。','Create a new VS Code file and save as hello.py. Include Python only, without Markdown fences; check it is not hello.py.txt.', 'print("Hello, Reitaku!")\nprint(1000 - 470)'),
 slide('Terminalで実行','VS CodeのTerminal→New Terminal。ファイルのフォルダを開き、次のコマンドを入力する。>>>はPython対話画面で、Terminalのプロンプトとは違う。','Open Terminal → New Terminal in the file’s folder. A >>> prompt is the Python interpreter, not the shell.','terminal',extra='<pre data-language="shell"><code># macOS\npython3 hello.py\n\n# Windows Python launcher\npy hello.py</code></pre>'+p('Windowsでpyがなければ、選択したPythonに対応するpython hello.pyを使う。VS CodeのRun Python Fileでも実行できる。','If py is unavailable, use python hello.py with your selected installation, or VS Code’s Run Python File.')),
 Q('何も表示されない？','関数を定義しただけのファイルを実行した。画面には何が出る？','You ran a file containing only a function definition. What appears?',('呼び出しがなければ、何も表示しない。printの有無も確かめる。','Nothing appears without a call. Check whether anything prints.')),
 C('自分の関数を呼ぶ','定義が先、呼び出しが後。Notebookの実行順に頼らず、ファイルを最初から実行する。','Define before calling; the script starts fresh rather than relying on notebook state.', REMAIN+'\n\nprint(remaining(1000, 470))'),
 slide('入力は文字列','input()は文字列を返す。int()で整数へ。数字以外が来たら、短い案内を出す。','input() returns text; int() converts it. Explain invalid input instead of a confusing crash.','terminal',extra='<pre data-language="python"><code>try:\n    budget = int(input("Budget in yen: "))\n    print(remaining(budget, 470))\nexcept ValueError:\n    print("Enter a whole number, such as 1000.")</code></pre>'),
 C('importして使う','randomと同じように、自分の.pyもモジュールになる。ここはbudget_tool.pyを同じフォルダへ置いたNotebookの例。','Your own .py can be a module like random. This notebook example assumes budget_tool.py is beside it.', 'from budget_tool import affordable\nprint(affordable(menu, 500))',run=False,output="['Onigiri', 'Sandwich', 'Udon']"),
 slide('__name__の小さな役割','if __name__ == "__main__": の内側は、直接実行したときだけ動く。importしただけでinputが始まるのを防ぐ。','The __main__ guard runs interactive code only on direct execution, so import does not unexpectedly ask for input.','code',code='if __name__ == "__main__":\n    main()',run=False),
 slide('データはどこ？','budget_tool.pyとstudent-menu.csvを同じフォルダへ。配布コードはPath(__file__).with_name(...)でスクリプトの隣を探す。','Keep budget_tool.py and student-menu.csv together. The supplied code uses Path(__file__).with_name(...) to find data beside the script.','path'),
 CH('hello.py→budget_tool.py→Notebookからimport。相手に実行方法を渡し、同じ結果になるか確かめる。','Save hello.py, run budget_tool.py, then import it. Give a partner launch instructions and compare results.'),
 slide('最終作品の、小さな種','誰の、何を助ける？ 入力→処理→結果を一文ずつ。データ調査か、小さな道具か、ゲームでもよい。','Whom will it help, and how? State input → process → result. A data investigation, tool or game is welcome.','exit')])

W[11]=dict(title='What did the detector miss?',title_ja='検出器は、何を見落とした？',date='2026-12-10',due='2026-12-16',
 aim=('画像検出を、入力→関数→座標のリスト→forの処理として理解する。','Understand image detection as input → function → list of boxes → a for loop.'),
 flow=('0–10：画像を観察、10–25：モジュールと座標、25–40：検出結果をforで処理、40–70：画像チャレンジ、70–90：誤検出と見落としを確認、90–100：最終作品の計画。','0–10 inspect an image; 10–25 modules/coordinates; 25–40 loop through detections; 40–70 image challenge; 70–90 inspect misses/false positives; 90–100 project plan.'),
 brief=('検出された顔の枠を描き、見落とし・誤検出を人の目で確認する。OpenCVが動かなくても、配布した実際の検出座標CSVを使って同じループを実行できる。','Draw face-detection boxes and inspect misses and false positives. If OpenCV is unavailable, process the supplied real detection-coordinate CSV with the same loop.'),
 requirements=[('入力画像・座標・検出件数の関係を説明する。','Explain how the input image, boxes and detection count relate.'),('枠の色・太さ・大きさ条件など、一つを変えて結果を確認する。','Change one property such as box color, width or size filter and check the result.'),('見落としか誤検出を一つ記録し、何が言えないかを書く。','Record one miss or false positive, and one conclusion the output cannot support.')],
 homework=('画像活動の実行記録と、最終作品の1ページ計画（読み手・入力・結果・必要ファイル・3つの確認）を提出。OpenCVなしの座標ルートでも同じ評価。UNIPAへ。','Submit the image activity record and a one-page final plan: audience, input, output, required files and three checks. The no-OpenCV coordinate route has equal standing. Submit to UNIPA.'),
 slides=[
 slide('何人、見つけられる？','画像を見て予想。次に検出結果と比べる。枠の数は、写っている人数そのものではない。','Predict, then compare with the detector. A box count is not the number of people in the image.','image',image='reitaku.jpg'),
 slide('検出 ≠ 本人の認識','顔検出は「顔らしい場所」を探す。この活動は名前・表情・出席を判断しない。','Detection locates face-like regions. This activity does not identify names, expressions or attendance.','statement'),
 slide('モジュールを使う','import cv2はOpenCVを読み込む。画像を読む→グレーへ変換→検出→座標を返す。内部のモデルを一から作る授業ではない。','import cv2 loads OpenCV. Read → grayscale → detect → return boxes. We use the detector, rather than train one.','path',extra='<div class="process-line"><span>image</span><b>→</b><span>detectMultiScale()</span><b>→</b><span>[(x, y, w, h), ...]</span></div>'),
 C('座標は、もう知っているデータ','1つの枠を辞書にすると、メニューと同じリストとして処理できる。ここは説明用の架空座標。','Dictionary boxes can be processed like menu items. These are fictional teaching coordinates.', 'boxes = [{"x": 40, "y": 30, "w": 80, "h": 90},\n         {"x": 180, "y": 50, "w": 60, "h": 70}]\nfor box in boxes:\n    print(box["x"], box["y"], box["w"] * box["h"])'),
 slide('x・y・幅・高さ','xとyは左上、右端はx+w、下端はy+h。座標を変えて、枠がどちらへ動くか予想する。','x/y mark the top-left; right is x+w and bottom is y+h. Predict how changing a coordinate moves the box.','interactive',demo='boxes'),
 slide('同じforで、枠を描く','検出モデルの戻り値を受け取り、一つずつ長方形へ。検出のたびに画像全体をコピーし直さない。','Take the detector output and draw one rectangle per box. Keep one image copy for all boxes.','code',code='for x, y, w, h in faces:\n    cv2.rectangle(image, (x, y),\n                  (x + w, y + h), (0, 255, 0), 2)',run=False),
 slide('インストールは、ここだけ','追加パッケージはOpenCV 4。Notebookで %pip install "opencv-python<5"。配布スクリプトには同梱のHaarモデルを使い、別の重いモデルは不要。','Use OpenCV 4: %pip install "opencv-python<5" in a notebook. The script uses its bundled Haar model, with no separate model download.','plain',extra=p('動かない人：検出済み座標CSVを読み、面積で絞り込み、結果を表示する。検出モデル自体を動かしたとは書かない。','Fallback: read cached boxes, filter by area and print results. Label these as cached detections.')),
 slide('実際の検出結果','この画像は同じ入力画像を配布スクリプトで処理したもの。件数と見た目を照合しよう。','This image was produced by the supplied detector script. Compare its count with what you see.','image',image='detected-faces.jpg'),
 C('大きな枠だけ、残す','同じ条件付きループ。min_areaという引数で、選択の基準を外から変える。','The same conditional loop, with min_area as a parameter.', 'def large_boxes(boxes, min_area):\n    kept = []\n    for box in boxes:\n        if box["w"] * box["h"] >= min_area:\n            kept.append(box)\n    return kept\n\nprint(len(large_boxes(boxes, 5000)))'),
 Q('検出0件なら？','「人がいない」と言える？','Does zero detections prove nobody is there?',('言えない。顔の向き・大きさ・画像条件などで見落とす。入力画像も確認する。','No. Pose, size and image conditions can cause misses; inspect the input too.')),
 CH('一つの変更を選び、元画像と結果を並べる。OpenCVなしでも、実際の座標CSVを条件で絞れる。','Choose one change and compare input/output. Without OpenCV, filter the actual cached coordinate CSV.'),
 slide('最終作品の計画を1ページに','画像、データ、道具、ゲーム。読み手と結果を一つに絞る。入力・必要ファイル・通常／境界／手計算の確認を記す。','Choose a focused image, data, tool or game project. State audience, input, files, and normal/boundary/manual checks.','exit')])

W[12]=dict(title='One click, one function',title_ja='クリック一回、関数一回',date='2026-12-17',due='2027-01-06',
 aim=('ゲームの入力・状態・更新を追い、イベントが関数を呼ぶことを理解する。','Trace game input, state and updates; understand that events call functions.'),
 flow=('0–10：ゲーム体験、10–25：状態と関数、25–40：イベントと繰り返し、40–70：ゲーム改造チャレンジ、70–90：自分の試作品、90–100：冬休みの作業を決める。','0–10 play; 10–25 state/functions; 25–40 events/repetition; 40–70 game modification challenge; 70–90 own prototype; 90–100 plan the break.'),
 brief=('小さなクリックゲームを一つのルールだけ変え、変更前後を確認する。その経験を使い、最終作品の中心となる機能を一つ動かす。','Change one rule in a small click game and test before/after. Then make one core feature of your own final project work.'),
 requirements=[('入力→関数→状態→表示を、ゲームの一手で説明する。','Explain input → function → state → display for one game action.'),('一つのルールを変え、通常と境界の結果を確認する。','Change one rule and check normal/boundary behavior.'),('自分の最終作品の動く機能一つと、次に直すことを保存する。','Save one working feature of your project and the next repair needed.')],
 homework=('最終作品の動く試作品一つ、通常／境界の確認、次に直すことを実行記録Notebookと必要ファイルで提出。最後の週課題（3点）。完成版は1月13日。','Submit a working project prototype, normal/boundary checks and next repair in a record notebook with needed files. This is the last 3-point weekly task; final project due January 13.'),
 slides=[
 H('あと1回だけ。','そのクリックで、何が変わる？','What changes when you click?',stamp='SCORE 0'),
 slide('まず、遊ぶ','的を押すと得点、時間が0なら終了。ブラウザ版はPythonのルールをJavaScriptで再現。','Click the target to score; stop at zero time. JavaScript simulates the Python rules in this browser.','interactive',demo='game'),
 C('ゲームにも、同じ変数','得点、残り時間、動作中か。文字や画像の前に、数値の変化を確かめる。','Score, time left and running state. Check the numbers before adding visuals.', 'score = 0\nseconds_left = 3\nwhile seconds_left > 0:\n    seconds_left -= 1\n    print(seconds_left)\nprint("Finished")'),
 C('クリック一回で、関数一回','hitは状態を受け取り、次の得点を返す。0秒なら増えない。','hit receives state and returns the next score; no points at zero seconds.', 'def hit(score, seconds_left):\n    if seconds_left > 0:\n        return score + 1\n    return score\n\nprint(hit(0, 3))\nprint(hit(1, 0))'),
 slide('command=hit と hit()','command=hitは「押されたら呼ぶ関数」を渡す。command=hit()は今呼んでしまう。配布GUIは引数なしのon_hitを使う。global scoreは外側の得点を書き換える宣言。中心のhitは値を返すだけ。','command=hit supplies a callback; command=hit() calls it immediately. The GUI uses the no-argument on_hit wrapper. global score lets that wrapper update module-level state; the core hit function only returns a value.','comparison'),
 slide('while Trueで画面を止めない','GUIには入力を待つイベントループがある。root.after(1000, tick)で、1秒後にtickを呼ぶよう予約する。','A GUI already has an event loop. root.after(1000, tick) schedules tick for one second later.','code',code='def tick():\n    global seconds_left\n    seconds_left -= 1\n    if seconds_left > 0:\n        root.after(1000, tick)',run=False),
 C('ループは、モデルの確認にも使える','画面を開かず、時間が0で得点が止まるか確かめる。','Verify the score stops at zero without opening a window.', 'score = 0\nfor seconds in [2, 1, 0]:\n    score = hit(score, seconds)\n    print(seconds, score)\nassert hit(5, 0) == 5'),
 slide('.pyでゲームを起動','click_game.pyを保存してTerminalから実行。macOSはpython3 click_game.py、Windowsはpy click_game.py。Notebookに入力・結果・変更点を残す。','Run click_game.py in a terminal: python3 on macOS, py on Windows. Keep inputs, results and changes in your notebook.','terminal',extra=p('Tkinterがない環境ではブラウザ版＋配布の画面なしPythonモデルで、同じルールを確認できる。','Without Tkinter, use the browser simulation and supplied headless Python model to test the same rules.')),
 Q('連打で、タイマーも速くなる？','クリック関数から毎回tickを呼んだら、どうなる？','What happens if every click starts another timer?',('複数のタイマーが重なり得る。タイマーはStartから一つだけ始め、再開時は前の予約を取り消す。','Multiple timers can overlap. Start one timer and cancel the old scheduled callback on restart.')),
 CH('得点・時間・的の大きさから一つだけ変える。変える前に予想し、結果を試す。','Change only scoring, duration or target size. Predict, then test.'),
 slide('作品の中心を、一つ動かす','ゲーム以外でもOK。データを読む、候補を返す、画像へ枠を描く。その一つが動く証拠を保存する。','Any project route is welcome: load data, return options or draw boxes. Save evidence of one working feature.','pair'),
 slide('冬休みの前に','今動くこと・直すこと・必要なファイルを残す。1月7日は相手に試してもらう。','Record what works, what needs repair and required files. A peer will test it on January 7.','exit')])

W[13]=dict(title='Let someone else run it',title_ja='自分が操作しなくても、動く？',date='2027-01-07',due='2027-01-13',
 aim=('最終作品を他の人に試してもらい、実行・説明・確認の穴を一つずつ直す。','Have a peer run the final project and repair gaps in running, explanation and verification.'),
 flow=('0–10：再起動して実行、10–25：最終作品の提出確認、25–40：ゲーム／UIの任意ミニ講義、40–70：ペアテスト・修正、70–90：仕上げ、90–100：提出物を確認。','0–10 fresh run; 10–25 submission check; 25–40 optional game/UI mini-lecture; 40–70 peer test/repair; 70–90 finish; 90–100 package check.'),
 brief=('最終作品を完成させる。相手に実行方法だけを渡し、動かせたか・結果を理解できたかを記録して一か所改善する。','Finish the project. Give a peer only the run instructions, record whether it runs and makes sense, and improve one issue.'),
 requirements=[('カーネルを再起動→全セル実行、または.pyを新しく起動する。','Restart/run all cells, or launch the script in a fresh process.'),('相手のテストを観察し、一つ直すか残る理由を書く。','Observe a peer test and repair one issue or explain why it remains.'),('必要ファイル、出典、三つの確認、修正記録、振り返りをそろえる。','Include needed files, sources, three checks, revision evidence and reflection.')],
 homework=('最終プロジェクト（独立した20%）を1月13日23:59 JSTまでにUNIPAへファイル提出。実行済み.ipynbまたは動く.py、必要データ、README、三つの確認、修正・ピアテスト記録、振り返り。GitHubリンクだけで代用しない。','Submit the separate 20% final project as files to UNIPA by January 13, 23:59 JST: executed .ipynb or runnable .py, needed data, README, three checks, revision/peer-test record and reflection. A GitHub link alone is insufficient.'),
 slides=[
 H('そのファイル、足りてる？','あなたの画面では動く。相手の手元では？','It runs on your screen. What about someone else’s?'),
 slide('まず、まっさらな状態で','NotebookはRestart Kernel→Run All。.pyはTerminalから新しく実行する。順番が違うと動かないCellを直す。','Restart Kernel → Run All, or launch a new script process. Repair cells relying on hidden execution order.','terminal'),
 slide('提出物は、小さくそろえる','動くコード、必要データ、短いREADME、三つの確認、修正と振り返り。GUIや大量のグラフは必須ではない。','Runnable code, data, short README, three checks, revision and reflection. A GUI or many charts are not required.','plain',extra=links([('../../final-project.html','最終プロジェクト要項','Final project requirements')])),
 slide('同じ関数が、別の入口で動く','Notebook、Terminal、ボタン。入力の入口が変わっても、中心の関数は共通にできる。','Notebook, terminal or button: different entry points can share the same core function.','path',extra='<div class="process-line"><span>Notebook / input() / button</span><b>→</b><span>function</span><b>→</b><span>result</span></div>'),
 C('ゲームの当たり判定','弾の点が的の長方形の内側ならTrue。境界も含めるか、仕様を決めて確認する。','A point inside a target rectangle is a hit. Decide and check whether edges count.', 'def inside(x, y, left, top, width, height):\n    return left <= x <= left + width and top <= y <= top + height\n\nprint(inside(20, 20, 10, 10, 30, 30))\nprint(inside(9, 20, 10, 10, 30, 30))\nassert inside(10, 10, 10, 10, 30, 30)'),
 slide('発展：シューティング','既存のシューティングを整理した版を配布。クリックゲームが動いた人向け。角度・弾・当たり判定は追加機能。新しい完成条件にしない。','An updated version of the existing shooter is optional after the click game. Angles, projectiles and collision are extensions, not new completion requirements.','game',extra=links([('../week-12/click_game.py','基本のクリックゲーム','Basic click game'),('stretch-shooter.py','発展シューティング','Optional shooter')])),
 slide('相手は、READMEだけで始める','作った人はキーボードを触らない。止まった所、分からない言葉、想定外の入力をメモする。','The author does not take the keyboard. Note where the tester stops, unclear wording and unexpected input.','pair'),
 Q('コードを増やす前に','結果は正しいが、どの単位か分からない。関数を増やすべき？','The result is correct but its units are unclear. Does it need another function?',('まずラベルと説明を直し、読み手に確認する。','Fix the label and explanation, then check with the reader.')),
 C('説明できる、小さな証拠','手計算できる例を残す。assertの成功だけでなく、期待値の理由を説明する。','Keep a hand-checkable case; explain the expected value, not only the passing assertion.', 'assert remaining(1000, 470) == 530\nassert remaining(470, 470) == 0\nassert remaining(100, 470) == -370\nprint("Normal, boundary and over-budget checks passed")'),
 CH('30分で、相手が見つけた問題を一つ改善する。変更前・変更後・確認結果を残す。','Use 30 minutes to improve one peer-found issue. Keep before, after and verification.'),
 slide('最終提出：1月13日（水）23:59','UNIPAへファイル提出。作品をクラスギャラリーで読めるよう、出力と説明を保存する。','Submit files to UNIPA. Save outputs and explanations for the class gallery.','deadline'),
 slide('次回は、一人で確かめる','最終作品とは別の20%チャレンジ。練習済みの形式で、読む・直す・確かめる・説明する。','Next week is a separate 20% individual challenge: read, modify, verify and explain in the practiced format.','exit')])

W[14]=dict(title='Read, change, check, explain',title_ja='読んで、変えて、確かめて、説明する',date='2027-01-14',due=None,
 aim=('練習した形式で、Pythonの理解を個人で示す。','Demonstrate individual Python understanding in a familiar format.'),
 flow=('0–10：説明と動作確認、10–25：予想・読解、25–70：修正と変更、70–90：確認と説明、90–100：保存してUNIPAへ。','0–10 instructions/run check; 10–25 predict/read; 25–70 repair/modify; 70–90 verify/explain; 90–100 save and submit to UNIPA.'),
 brief=('このページとNotebookは形式練習用で、本番問題ではありません。本番はUNIPAで配布。新しい小さなデータを使い、既習のコードを読む・直す・確認する。','This page and notebook are format practice, not the actual exam. The exam comes through UNIPA, using a new small dataset and familiar reading, repair and checking tasks.'),
 requirements=[('コードを実行する前に、結果と理由を書く。','Write the output prediction and reason before running.'),('条件や関数の小さな変更を行い、動作を確認する。','Make and check a small change to a condition or function.'),('通常・境界の結果を確かめ、変更の理由を説明する。','Check normal/boundary results and explain the change.')],
 homework=('持ち帰り課題なし。本番の完成Notebookを授業中にUNIPAへ提出。独立した20%。1月13日提出の最終作品を再提出する必要はない。','No homework. Submit the completed actual challenge notebook to UNIPA during class. Worth a separate 20%; do not resubmit the project due January 13.'),
 slides=[
 H('自分で、確かめる','見慣れた形式で、理解を示そう。','Show your understanding in a familiar format.'),
 slide('今日は、最終作品とは別','プロジェクト20%と、今日の個人チャレンジ20%は別。配布された本番Notebookを使う。','The project and today’s individual challenge are separate 20% components. Use the actual notebook distributed in class.','statement'),
 slide('まず、実行環境を確認','PythonのCellを一つ動かす。問題があればすぐ伝える。データは配布済みで、APIや追加パッケージは不要。','Run one Python cell and report a problem immediately. Data is supplied; no APIs or extra packages are needed.','plain'),
 slide('使えるもの','自分の授業ノート・授業教材・Python公式ドキュメント・通常の構文補完は可。生成AIと他者との相談は本番の個人チャレンジでは使わない。事前練習も同じ条件。','Course notes/materials, official Python docs and ordinary syntax completion are allowed. No generative AI or collaboration in the individual challenge; practice under the same rules.','plain'),
 Q('形式練習：出力を予想','prices = [150, 320, 550] を <= 320 で選ぶと？','Which values from [150, 320, 550] satisfy <= 320?',('150と320。境界を含む。','150 and 320; the boundary is included.')),
 C('形式練習：修正を確かめる','本番の解答ではない。予算と同じ値を含める、いつもの境界確認。','This is practice, not an exam answer. Check an exactly affordable value.', 'def keep_prices(prices, budget):\n    kept = []\n    for price in prices:\n        if price <= budget:\n            kept.append(price)\n    return kept\n\nprint(keep_prices([150, 320, 550], 320))'),
 slide('4つの観点、各5点','読解・予想／修正・拡張／検証／説明。正しい出力と、その理由の両方を残す。','Reading/prediction, repair/extension, verification and explanation: five points each. Keep output and reasoning.','comparison'),
 slide('時間の使い方','予想15分→修正・変更45分→確認・説明20分→保存10分。全部が終わらなくても、途中の考えと実行結果を保存。','Predict 15 min → repair/change 45 → check/explain 20 → save 10. Save reasoning and outputs even if unfinished.','path'),
 slide('授業内の本番を始める','ここから先は、UNIPA配布の問題で個人作業。疑問は教員に聞く。','Continue individually in the UNIPA-distributed notebook. Direct questions to the instructor.','challenge'),
 slide('保存して提出','ファイル名と氏名を確認。出力・説明を保存し、NotebookをUNIPAへ提出。','Check filename/name, save outputs and explanations, and submit the notebook to UNIPA.','exit')])

BUDGET_SCRIPT='''"""Run: python3 budget_tool.py (macOS) or py budget_tool.py (Windows)."""
import csv
from pathlib import Path


def affordable(items, budget):
    chosen = []
    for item in items:
        if item["price"] <= budget:
            chosen.append(item["name"])
    return chosen


def load_menu():
    path = Path(__file__).with_name("student-menu.csv")
    with path.open(encoding="utf-8-sig", newline="") as file:
        items = list(csv.DictReader(file))
    for item in items:
        item["price"] = int(item["price"])
    return items


def main():
    try:
        budget = int(input("Budget in yen: "))
    except ValueError:
        print("Enter a whole number, such as 1000.")
        return
    if budget < 0:
        print("Budget must be zero or more.")
        return
    try:
        names = affordable(load_menu(), budget)
    except FileNotFoundError:
        print("Put student-menu.csv beside budget_tool.py.")
        return
    print(names if names else "No options. Try another budget.")


if __name__ == "__main__":
    main()
'''
CLICK_MODEL='''"""Game rules without a window; usable on any Python installation."""
def hit(score, seconds_left):
    if seconds_left > 0:
        return score + 1
    return score


def tick_state(seconds_left):
    return max(0, seconds_left - 1)
'''
CLICK_GAME='''"""Click the target. Run with python3 click_game.py or py click_game.py."""
import random
import tkinter as tk
from click_model import hit, tick_state

DURATION = 20
score = 0
seconds_left = 0
timer = None


def refresh():
    status.config(text=f"Score: {score}   Time: {seconds_left}")


def move_target():
    target.place(x=random.randint(30, 380), y=random.randint(90, 260))


def on_hit():
    global score
    if seconds_left <= 0:
        return
    score = hit(score, seconds_left)
    refresh()
    move_target()


def tick():
    global seconds_left, timer
    seconds_left = tick_state(seconds_left)
    refresh()
    if seconds_left > 0:
        timer = root.after(1000, tick)
    else:
        timer = None
        target.place_forget()


def start():
    global score, seconds_left, timer
    if timer is not None:
        root.after_cancel(timer)
    score = 0
    seconds_left = DURATION
    refresh()
    move_target()
    timer = root.after(1000, tick)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("One click, one function")
    root.geometry("500x360")
    status = tk.Label(root, text="Press Start", font=("Arial", 18))
    status.pack(pady=12)
    target = tk.Button(root, text="●", font=("Arial", 20), command=on_hit)
    tk.Button(root, text="Start / Restart", command=start).pack(side="bottom", pady=15)
    root.mainloop()
'''
DETECT_SCRIPT='''"""Still-image detection; no identity or attendance inference.
Install OpenCV 4 first: python3 -m pip install "opencv-python<5"
Run: python3 detect_faces.py [path/to/image.jpg]
"""
import csv
import sys
from pathlib import Path
import cv2


def detect(image_path):
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(image_path)
    height, width = image.shape[:2]
    image = cv2.resize(image, (1200, round(height * 1200 / width)))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = classifier.detectMultiScale(gray, scaleFactor=1.1,
                                       minNeighbors=5, minSize=(20, 20))
    return image, faces


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("reitaku.jpg")
    image, faces = detect(source)
    cv2.imwrite("vision-input.jpg", image)
    with open("detected-boxes.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator=chr(10))
        writer.writerow(["x", "y", "w", "h"])
        for x, y, w, h in faces:
            writer.writerow([int(x), int(y), int(w), int(h)])
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imwrite("detected-faces.jpg", image)
    print(len(faces), "candidate face boxes; inspect misses and false positives.")


if __name__ == "__main__":
    main()
'''

EN_TITLES={

8:['“Can I use this?”','Whose budget?','Give the subtraction a name','Values in, result out','Explain an empty result','Two useful checks','Check it by hand','Alternative: bicycle theft','Counting uses the same for','30 MIN / CHALLENGE','Watch the tester','Show one repair'],
9:['Three people, three budgets','The process you already know','def does not call the function','Pass the arguments','Slow down one call','print and return','What is stored in result?','A for inside a function','Count the work in one call','A for that calls a function','Trace the loop and function','How many comparisons?','Returning too early','An empty input still returns','A new local list each call','30 MIN / CHALLENGE','Explain three lines','Next: outside the cell'],
10:['Run without a cell button','.ipynb and .py','Create hello.py','Run it in a terminal','Why is nothing printed?','Call your function','input returns text','Import your own function','The __main__ guard','Where is the data file?','30 MIN / CHALLENGE','A small final-project idea'],
11:['How many faces will it find?','Detection is not identification','Use a module','Boxes are familiar data','x, y, width, height','Draw one rectangle per box','One optional installation','The actual detector output','Keep only larger boxes','What does zero prove?','30 MIN / CHALLENGE','One page for your project'],
12:['One more click','Play first','Games have ordinary variables','One click calls one function','command=hit versus hit()','Do not freeze the event loop','Check rules without a window','Launch the game as a script','What if clicks start timers?','30 MIN / CHALLENGE','One working project feature','Before the winter break'],
13:['Are all the files there?','Start with a fresh run','A small complete submission','One function, several entry points','Check a hit','Optional: the shooter','The tester uses only the README','What needs changing?','A small check you can explain','30 MIN / CHALLENGE','Final submission: January 13','Next week: individual understanding'],
14:['Check it yourself','Separate from the final project','Check your environment','Permitted resources','Practice: predict the output','Practice: verify a repair','Four criteria, five points each','Use the time well','Begin the actual challenge','Save and submit']}

def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8')
def mdcell(text):return dict(cell_type='markdown',source=text,metadata={})
def codecell(code,output=None,count=None):
    return dict(cell_type='code',source=code,metadata={},execution_count=count,
                outputs=[] if output is None else [dict(output_type='stream',name='stdout',text=output)])
def notebook(path,cells):
    write(path,json.dumps(dict(nbformat=4,nbformat_minor=4,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},cells=cells),ensure_ascii=False,indent=1)+'\n')

def code_html(source,output=None,language='python'):
    button='<button type="button" data-run aria-expanded="false">▶ '+bi('実行結果','Run / output')+'</button>' if output else ''
    return '<div class="lesson-code"><div class="code-toolbar"><span>'+language.title()+'</span>'+button+'</div><pre data-language="'+language+'"><code>'+html.escape(source)+'</code></pre></div>'+('' if not output else '<pre class="lesson-output" hidden aria-live="polite">'+html.escape(output)+'</pre>')

def page_head(title,css,js,version=VERSION):
    return f'''<!doctype html><html lang="ja" data-language="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&amp;family=Manrope:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet"><link rel="icon" href="../../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../week-02/lecture.css?v={version}"><link rel="stylesheet" href="../../assets/{css}?v={version}"><link rel="stylesheet" href="../../assets/copy-blocks.css"><script src="../../assets/course-models.js?v={version}" defer></script><script src="../../assets/{js}?v={version}" defer></script><script src="../../assets/copy-blocks.js" defer></script>'''

def demo_html(kind):
    if kind=='menu-budget':return '<div data-demo="budget"><label>'+bi('予算 / 円','Budget / yen')+' <input data-budget type="number" min="0" max="10000" value="500"></label><button data-demo-run type="button">▶ '+bi('実行','Run')+'</button><pre data-demo-code data-language="python"><code></code></pre><pre data-demo-output aria-live="polite"></pre></div>'
    if kind=='budget':return '<div data-demo="budget"><label>'+bi('予算 / 円','Budget / yen')+' <input data-budget type="number" min="0" max="10000" value="500"></label><label>'+bi('時間 / 分','Time / minutes')+' <input data-minutes type="number" min="0" max="120" value="10"></label><button data-demo-run type="button">▶ '+bi('実行','Run')+'</button><pre data-demo-code data-language="python"><code></code></pre><pre data-demo-output aria-live="polite"></pre></div>'
    if kind=='vending':return '<div data-demo="vending"><div class="coin-slot"><output data-paid>¥0 / ¥150</output>'+''.join(f'<button type="button" data-coin="{c}">¥{c}</button>' for c in [10,50,100])+'<button type="button" data-reset aria-label="Reset">↶</button></div><pre data-demo-code data-language="python"><code></code></pre><pre data-demo-output aria-live="polite"></pre></div>'
    if kind=='call':return '<div data-demo="call"><div class="argument-inputs"><label>budget <input data-call-budget type="number" value="1000"></label><label>price <input data-call-price type="number" value="470"></label></div><div class="call-path"><span data-frame="argument">arguments</span><b>→</b><span data-frame="local">local variables</span><b>→</b><span data-frame="return">return</span><b>→</b><span data-frame="caller">caller</span></div><pre data-demo-code data-language="python"><code></code></pre><button type="button" data-step>'+bi('一段ずつ追う','Step through')+' →</button><button type="button" data-reset aria-label="Reset">↶</button><pre data-demo-output aria-live="polite"></pre></div>'
    if kind=='boxes':return '<div data-demo="boxes"><label>x <input data-box-x type="range" min="0" max="400" value="40"></label><label>'+bi('最小面積','Minimum area')+' <input data-box-area type="number" min="0" max="20000" value="0"></label><svg viewBox="0 0 500 180" role="img" aria-label="Fictional coordinate boxes"><rect width="500" height="180" fill="#e9eeea"/><g data-box-layer></g></svg><pre data-demo-code data-language="python"><code></code></pre><pre data-demo-output aria-live="polite"></pre></div>'
    if kind=='game':return '<div data-demo="game"><div class="game-readout"><output data-game-status>Score: 0 · Time: 20</output><button type="button" data-game-start>Start / Restart</button></div><div class="game-field"><button type="button" data-game-target aria-label="Hit target" hidden>●</button></div><pre data-demo-output aria-live="polite">Startを押す / Press Start</pre></div>'
    return ''

def build_week(week,spec):
    if week==7:
        return weather_hackathon.build(ROOT,sys.modules[__name__])
    dest=ROOT/f'weeks/week-{week:02}'
    date=spec['date']; release=date+'T12:00:00+09:00'
    if week in [8,9,10]:
        with (dest/'student-menu.csv').open('w',encoding='utf-8',newline='') as file:
            writer=csv.DictWriter(file,lineterminator=chr(10),fieldnames=['name','price','minutes','category']);writer.writeheader();writer.writerows(MENU_DICTS)
    small_menu=spec.get('small_menu',SMALL)
    small_code=spec.get('small_code',SMALL_CODE)
    ns={'menu':[dict(x) for x in small_menu]}; exec(REMAIN+'\n'+AFFORD,ns)
    # Each deck starts from the same explicitly supplied four-item menu.
    cells=[mdcell(f'# Week {week:02} · {spec["title_ja"]}\n\n氏名：\n\nコードを上から順に実行する。予想・変更したコード・結果をMarkdownで短く説明しよう。\nRun from top to bottom. Use Markdown to explain your prediction, code change and result.')]
    cells.append(codecell(small_code))
    if week==13:cells.append(codecell(REMAIN))
    content=[]
    for i,s in enumerate(spec['slides'],1):
        title=s['title']; layout=s['layout']; output=s.get('output')
        if s.get('code') is not None and s.get('run',True):
            stream=io.StringIO()
            with contextlib.redirect_stdout(stream),contextlib.chdir(dest):exec(s['code'],ns)
            output=stream.getvalue()
            cells += [mdcell('## '+title+'\n'+s['ja']+'\n\n'+s['en']),codecell(s['code'],output or None,len([c for c in cells if c['cell_type']=='code'])+1)]
        elif s.get('code'):
            cells.append(mdcell('## '+title+'\n'+s['ja']+'\n\n```python\n'+s['code']+'\n```'))
        body=p(s['ja'],s['en'],'lesson-lead')
        if s.get('code'):body+=code_html(s['code'],output)
        if s.get('answer'):body+='<details class="answer"><summary>'+bi('予想してから開く','Predict, then reveal')+'</summary>'+p(*s['answer'])+'</details>'
        if s.get('demo'):body+=demo_html(s['demo'])+p('Pythonの動きをJavaScriptで再現。自分のNotebookでも同じコードを実行する。','JavaScript simulates the Python logic. Also run the code in your own notebook.','simulation-note')
        if s.get('trace'):body+='<div data-trace="loopcalls"><pre data-trace-code data-language="python"><code>'+html.escape(AFFORD+'\n\nfor budget in [500, 700, 1000]:\n    names = affordable(menu, budget)\n    print(budget, names)')+'</code></pre><button type="button" data-trace-next>'+bi('次の一段','Next step')+' →</button><button type="button" data-trace-reset aria-label="Reset">↶</button><div class="trace-frame"><p data-trace-phase></p><pre data-trace-state></pre></div><pre data-trace-output aria-live="polite"></pre></div>'
        if s.get('image'):body+='<img class="lesson-image" src="'+s['image']+'" alt="'+html.escape(title)+'">'
        if layout=='challenge' and week!=14:body+=links([('challenge.html','チャレンジを開く','Open challenge'),('practice.ipynb','授業のNotebook','Lesson notebook')],week,'lecture.html')
        if layout=='exit':body+=links([('challenge.html','課題・提出方法','Assignment / submission')])
        body+=s.get('extra','')
        assert len(EN_TITLES[week])==len(spec['slides'])
        content.append(f'<section class="slide lesson-slide layout-{layout}" data-slide data-slide-number="{i}" data-ink-id="w{week}-{i}" hidden><p class="slide-kicker">WEEK {week:02} · {html.escape(spec["title"])}</p><h{1 if layout=="hero" else 2}>'+bi(html.escape(title),html.escape(EN_TITLES[week][i-1]))+f'</h{1 if layout=="hero" else 2}>'+('<div class="large-stamp">'+s['stamp']+'</div>' if s.get('stamp') else '')+body+'</section>')
    head=page_head(f'Week {week:02} · {spec["title"]}','course-decks.css','course-decks.js',spec.get('version',VERSION))
    head+=f'<link rel="stylesheet" href="../../assets/slide-annotations.css"><script src="../../assets/slide-annotations.js" defer></script><script src="../../assets/slide-swipe.js" defer></script></head><body class="lecture-page course-deck" data-week="{week}" data-release="{release}"><header class="lecture-header"><a id="lecture-return" class="return-link" href="../../agenda.html?open={week:02}#week-{week:02}">← '+bi('授業予定','Agenda')+'</a><span class="lecture-mark">PRG / 26–2</span><button id="language-toggle" class="language-toggle" type="button" aria-label="Switch language">EN</button></header>'
    trace=[dict(phase='Ready / 予想',line=-1,state='menu: 4 items\nbudgets: [500, 700, 1000]',output='')]
    lines=[]
    for budget in [500,700,1000]:
        chosen=[]
        trace.append(dict(phase=f'Call affordable(menu, {budget})',line=9,state=f'caller budget = {budget}\nlocal chosen = []',output='\n'.join(lines)))
        for item in SMALL:
            match=item['price']<=budget
            if match:chosen.append(item['name'])
            trace.append(dict(phase='Compare / 価格を確認',line=3,state=f'local budget = {budget}\nitem = {item["name"]}: {item["price"]}\ncondition = {match}\nchosen = {chosen!r}',output='\n'.join(lines)))
        trace.append(dict(phase='Return / 呼び出し元へ',line=5,state=f'return {chosen!r}\ncaller names = {chosen!r}',output='\n'.join(lines)))
        lines.append(f'{budget} {chosen!r}')
        trace.append(dict(phase='Caller prints / 外側で表示',line=10,state=f'function has finished; next outer iteration\nbudget = {budget}',output='\n'.join(lines)))
    payload=json.dumps(dict(menu=small_menu,trace=trace),ensure_ascii=False).replace('</','<\\/')
    write(dest/'lecture.html',head+'<main><div id="slides-view" class="view"><nav class="slide-controls" aria-label="Slide navigation"><div class="slide-nav-group"><button id="previous-slide" type="button">← '+bi('前へ','Previous')+'</button><span id="slide-count" aria-live="polite"></span><button id="next-slide" type="button">'+bi('次へ','Next')+' →</button></div><button id="slide-fullscreen" type="button" class="slide-fullscreen" aria-pressed="false">⛶</button></nav><div class="slide-stage">'+''.join(content)+'</div></div></main><script type="application/json" id="lesson-data">'+payload+'</script></body></html>')
    cells += [mdcell('## Your challenge / 自分で試す\n'+spec['brief'][0]+'\n\n'+'\n'.join('- '+r[0] for r in spec['requirements'])+'\n\nUse a Markdown cell to document your prediction, change, result and checks.'),codecell('# Write your own change here. / 自分の変更を書こう。\n'),mdcell('## Check / 確認\n通常：\n境界・失敗：\n手計算・元データとの照合：\n\n## Reflection / 気づき\n自分で説明できるコード：\n改善したこと：\n残る限界：')]
    notebook(dest/'practice.ipynb',cells)
    challenge=[mdcell(f'# Week {week:02} challenge · {spec["title_ja"]}\n\n作品タイトル：\n氏名：\n\n'+spec['brief'][0]+'\n\n'+'\n'.join('- '+r[0] for r in spec['requirements']))]
    if week in [8,9,10]:challenge += [mdcell('## Load / 読み込み\n同じフォルダへstudent-menu.csvを保存。追加パッケージ不要。'),codecell(LOAD)]
    if week==11:challenge += [mdcell('## OpenCVなしの入口 / Cached detections\n同じフォルダにdetected-boxes.csvを置く。これは配布画像に対する実際の検出結果。検出自体は再実行していません。'),codecell('import csv\nwith open("detected-boxes.csv", encoding="utf-8", newline="") as file:\n    boxes = list(csv.DictReader(file))\nfor box in boxes:\n    for key in ["x", "y", "w", "h"]:\n        box[key] = int(box[key])\nprint(len(boxes), "cached boxes")')]
    if week==12:challenge += [mdcell('## 画面なしのモデル / Headless model\nclick_model.pyを同じフォルダへ。GUIがなくても実際のPythonで確認できます。'),codecell('from click_model import hit, tick_state\nprint(hit(0, 3))\nprint(hit(1, 0))\nprint(tick_state(1))')]
    challenge += [mdcell('## Predict / 予想\n変更前に何が起きると思う？'),codecell('# Your program / 自分のプログラム\n'),mdcell('## Checks / 確認\n入力 → 期待値 → 実際の結果\n\n通常：\n境界・失敗：\n手計算・元データとの照合：\n\n## Explain / 説明\n何を変えた？ なぜ？ 何がまだできない？')]
    notebook(dest/'challenge-starter.ipynb',challenge)
    extras=[('starter-files.zip','必要ファイルをまとめてダウンロード','Download the starter pack'),('practice.ipynb','ミニ講義の実行例Notebook','Worked-example notebook'),('challenge-starter.ipynb','空欄つきチャレンジNotebook','Challenge notebook')]
    if week in [8,9,10]:extras.append(('student-menu.csv','メニュー CSV','Menu CSV'))
    if week==8:extras.append(('bicycle-theft-guide.ipynb','選択：実際の事件CSVを集計','Alternative: actual incident CSV'))
    if week==10:extras += [('budget_tool.py','予算ツール.py','Budget tool script')]
    if week==11:extras += [('detect_faces.py','OpenCV検出.py','OpenCV detection script'),('reitaku.jpg','入力画像','Input image'),('detected-boxes.csv','検出済み座標CSV','Cached detection CSV'),('vision-input.jpg','座標に対応する縮小入力画像','Resized input matching cached coordinates'),('detected-faces.jpg','実際の出力画像','Actual output image')]
    if week==12:extras += [('click_game.py','クリックゲーム.py','Click game script'),('click_model.py','画面なしのルール.py','Headless game rules')]
    if week==13:extras += [('stretch-shooter.py','任意：発展シューティング','Optional shooter'),('workshop-tkinter.ipynb','任意：ボタンから関数を呼ぶ','Optional function behind a button')]
    body=p(*spec['brief'])+'<h2>'+bi('まず、ここから','Start here')+'</h2>'+p('新しい空のNotebookを作り、タイトル・氏名・問いをMarkdownで書く。必要なデータを同じフォルダへ保存。コードを実行し、結果と自分の説明を交互に置く。前の週の提出がなくてもスターターから始められる。','Create a blank notebook; write title, name and question in Markdown. Save needed data beside it. Alternate code/results with your explanation. The starter works without a previous submission.')+'<h2>'+bi('30分のチャレンジ','30-minute challenge')+'</h2>'+list_html(spec['requirements'])+links(extras,week)+'<h2>'+bi('保存するもの','Save your evidence')+'</h2>'+p('予想→変更→結果→確認。各セルの役割をMarkdownで説明し、全セルを実行して出力を保存する。派手さより、自分で説明できる変更を大切に。','Prediction → change → result → check. Explain steps in Markdown, run all cells and save outputs. Choose a change you can explain.')+'<h2>'+bi('宿題・提出','Homework / submission')+'</h2>'+p(*spec['homework'])+(p(f'締切：{spec["due"]} 23:59 JST',f'Due: {spec["due"]}, 23:59 JST') if spec['due'] else '')+p('提出作品はクラスギャラリーへ。AIを使った場合は、一つの提案と、それを確かめて採用・修正・却下した理由を記す。','Submitted projects go to the class gallery. If using AI, record one suggestion and why you accepted, changed or rejected it after checking.')
    if week==14:body=p(*spec['brief'])+'<h2>'+bi('形式練習','Format practice')+'</h2>'+list_html(spec['requirements'])+links(extras,week)+p(*spec['homework'])+p('本番：授業ノート・教材・Python公式文書・通常の構文補完は可。生成AI・他者との相談は不可。予想を実行前に書き、読解・変更・検証・説明を各5点で評価。','Actual challenge: notes/materials, official Python docs and ordinary completion allowed; no generative AI or collaboration. Predict before running. Reading, change, verification and explanation are five points each.')
    refs={10:('https://docs.python.org/3/tutorial/modules.html','Python公式：スクリプトとモジュール','Python documentation: scripts and modules'),11:('https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html','OpenCV公式：Cascade Classifier','OpenCV documentation: Cascade Classifier'),12:('https://docs.python.org/3/library/tkinter.html','Python公式：Tkinterとイベントループ','Python documentation: Tkinter and its event loop')}
    if week in refs:
        url,ja,en=refs[week];body+='<footer class="reference">'+p('参考：<a href="'+url+'">'+ja+'</a>','Reference: <a href="'+url+'">'+en+'</a>')+'</footer>'
    body=body.replace('href="starter-files.zip" download',f'href="starter-files.zip" download="week-{week:02}-starter.zip"')
    write(dest/'challenge.html',page_head(f'Week {week:02} challenge · {spec["title"]}','course-pages.css','course-page.js',spec.get('version',VERSION))+f'</head><body class="course-challenge" data-release="{release}"><header class="lecture-header"><a href="../../agenda.html?open={week:02}#week-{week:02}">← '+bi('授業予定','Agenda')+'</a><span class="lecture-mark">WEEK '+f'{week:02}'+'</span><button id="language-toggle" class="language-toggle" type="button">EN</button></header><main id="course-page" hidden><p class="slide-kicker">'+bi('授業内チャレンジ＋宿題','In-class challenge + homework')+'</p><h1>'+bi(spec['title_ja'],spec['title'])+'</h1>'+body+links([('lecture.html','講義スライド','Lecture slides')])+'</main></body></html>')
    # Update the agenda source while retaining the date and release gate.
    source=next((ROOT/'content/weeks').glob(f'{week:02}-*.md'))
    old=source.read_text(); front=old.split('---',2)[1]
    if week==14:
        front=re.sub(r'^practice_mix:.*$','practice_mix: Human 100% · AI 0%',front,flags=re.M)
        front=re.sub(r'^practice_mix_ja:.*$','practice_mix_ja: 人 100% · AI 0%',front,flags=re.M)
    for key,value in [('title',spec['title']),('title_ja',spec['title_ja']),('overview',spec['aim'][1]),('overview_ja',spec['aim'][0])]:
        front=re.sub(r'^'+key+r':.*$',key+': '+value,front,flags=re.M)
    homework_titles={7:('天気の道具を改善する','Improve your weather tool'),8:('友だちが使える道具','A tool a friend can use'),9:('関数とループで繰り返す','Repeat with a function and loop'),10:('.pyで動く予算ツール','A runnable budget script'),11:('画像の確認と作品計画','Image checks and a project plan'),12:('動く試作品','A working prototype'),13:('最終プロジェクト提出','Final project submission'),14:('授業内に提出','Submit during class')}
    for key,value in [('homework_title',homework_titles[week][1]),('homework_title_ja',homework_titles[week][0])]:
        if re.search(r'^'+key+':',front,re.M):front=re.sub(r'^'+key+':.*$',key+': '+value,front,flags=re.M)
        else:front+='\n'+key+': '+value
    front=front.rstrip()+'\n'
    resources=[f'- [Week {week:02} Lecture — {spec["title"]}](weeks/week-{week:02}/lecture.html) {{lecture}}',f'- [ミニ講義の実行例 / Worked Examples](weeks/week-{week:02}/practice.ipynb) {{fundamentals}}',f'- [チャレンジ・スターター / Challenge Starter](weeks/week-{week:02}/challenge-starter.ipynb) {{notebook}}',f'- [チャレンジの手順 / Challenge Instructions](weeks/week-{week:02}/challenge.html) {{challenge}}',f'- [宿題・提出方法 / Homework and Submission](weeks/week-{week:02}/challenge.html) {{homework}}']
    if week in [8,9,10]:resources.append(f'- [メニュー / Menu](weeks/week-{week:02}/student-menu.csv) {{data}}')
    if week==8:resources.append('- [選択：千葉の自転車盗 / Optional Bicycle-Theft Investigation](weeks/week-08/bicycle-theft-guide.ipynb) {support}')
    if week in [10,11,12,13]:resources.append('- [Final Project Requirements](content/final-project.md) {support}')
    sections=[('Lecture Flow',spec['flow']),('In-Class Notebook',('スライドの短いコードを予想→実行→一つ修正。説明と結果が入った実行例Notebookを使う。','Predict, run and modify short slide examples using the worked-example notebook.')),('In-Class Challenge',(spec['brief'][0]+f' [手順とファイルを開く](weeks/week-{week:02}/challenge.html)。',spec['brief'][1]+f' [Open instructions and files](weeks/week-{week:02}/challenge.html).')),('Take-Home Assignment',spec['homework']),('Aha!',spec['aim']),('Takeaway',('自分で変え、結果を確かめ、理由を説明する。','Change it yourself, check the result and explain why.'))]
    text='---'+front+'---\n'
    for name,(ja,en) in sections:text+=f'## {name}\nEN: {en}\nJP: {ja}\n'
    text+='## Resources\n'+'\n'.join(resources)+'\n'
    write(source,text)

def main():
    for week,spec in W.items():build_week(week,spec)
    write(ROOT/'weeks/week-10/budget_tool.py',BUDGET_SCRIPT)
    write(ROOT/'weeks/week-11/detect_faces.py',DETECT_SCRIPT)
    write(ROOT/'weeks/week-12/click_model.py',CLICK_MODEL)
    write(ROOT/'weeks/week-12/click_game.py',CLICK_GAME)
    bike=[mdcell('# 選択：千葉の自転車盗を集計\n\n作品タイトル：\n氏名：\n\n同じフォルダにbicycle-theft.csvを保存。授業配布の実際の事件データを集計します。件数は、駐輪された全自転車の被害確率ではありません。出典：https://www.police.pref.chiba.jp/seisoka/safe-life_publicspace-statistics_00002.html'),codecell('import csv\nwith open("bicycle-theft.csv", encoding="utf-8-sig", newline="") as file:\n    incidents = list(csv.DictReader(file))\nprint(len(incidents), "reported incidents")'),codecell('def count_places(rows, column):\n    counts = {}\n    for row in rows:\n        place = row[column]\n        counts[place] = counts.get(place, 0) + 1\n    return counts\n\ncounts = count_places(incidents, "発生場所")\nprint(counts)'),mdcell('## 自分の変更\n発生場所・時間・施錠関係など、別の列で数えてみる。列名はlist(incidents[0])で確認。元データ数行と照合し、何が言えて何が言えないかを書く。'),codecell('# Your change\n')]
    notebook(ROOT/'weeks/week-08/bicycle-theft-guide.ipynb',bike)
    # Keep incoming links to the established in-class notebooks useful.
    aliases={8:'week-08-in-class-bicycle-theft.ipynb',9:'week-09-in-class-functions.ipynb',10:'week-10-in-class-systems.ipynb',11:'week-11-in-class-modules.ipynb',12:'week-12-in-class-review-prototype.ipynb',13:'week-13-in-class-project-testing.ipynb',14:'week-14-in-class-final.ipynb'}
    for week,name in aliases.items():shutil.copyfile(ROOT/f'weeks/week-{week:02}/practice.ipynb',ROOT/f'weeks/week-{week:02}'/name)
    shutil.copyfile(ROOT/'weeks/week-09/practice.ipynb',ROOT/'weeks/week-09/fundamentals-functions.ipynb')
    vision=json.loads((ROOT/'weeks/week-11/challenge-starter.ipynb').read_text())['cells']
    vision.insert(1,mdcell('## 実際の入力と検出結果 / Actual input and detector output\n\n![Input resized to match cached coordinates](vision-input.jpg)\n\n![Actual detected boxes](detected-faces.jpg)\n\nOpenCVが使える人はdetect_faces.pyを実行して再検出できます。Notebookで `%pip install "opencv-python<5"` を実行後、Terminalで `python3 detect_faces.py`（Windowsは `py detect_faces.py`）。モデルはOpenCV 4同梱。下の座標ルートは検出を再実行せず、配布した結果を処理します。'))
    notebook(ROOT/'weeks/week-11/challenge-face-detection.ipynb',vision)
    tk_code='''import tkinter as tk

def remaining(budget, price):
    return budget - price

def show_balance():
    try:
        amount = int(entry.get())
        result.config(text=f"Remaining: {remaining(amount, 470)} yen")
    except ValueError:
        result.config(text="Enter a whole number, such as 1000.")

root = tk.Tk()
root.title("A function behind a button")
tk.Label(root, text="Budget in yen (plan price: 470)").pack(padx=20, pady=10)
entry = tk.Entry(root)
entry.insert(0, "1000")
entry.pack()
tk.Button(root, text="Calculate", command=show_balance).pack(pady=10)
result = tk.Label(root, text="")
result.pack(pady=10)
root.mainloop()'''
    notebook(ROOT/'weeks/week-13/workshop-tkinter.ipynb',[mdcell('# 任意：関数をボタンから呼ぶ\n\nTkinterの画面が使える環境向けの発展。新しい完成条件ではありません。下のコードをbudget_window.pyへ保存してTerminalで実行できます。Notebookで動かした場合は、画面を閉じるまでCellは実行中です。\n\ncommand=show_balance は関数を渡します。show_balance()と書くと今呼んでしまいます。中心のremaining関数はNotebookやTerminalと同じです。'),codecell(tk_code),mdcell('## 自分で試す\n470円、1,000円、文字列で確認。結果の単位、エラーの案内、関数へ渡る値を説明しよう。')])
    for week in W:
        if week==7:continue  # Week 7 has a single starter notebook, no duplicate pack.
        folder=ROOT/f'weeks/week-{week:02}'
        files=['practice.ipynb','challenge-starter.ipynb']
        if week in [8,9,10]:files+=['student-menu.csv']
        if week==8:files+=['bicycle-theft-guide.ipynb','bicycle-theft.csv']
        if week==10:files+=['budget_tool.py']
        if week==11:files+=['detect_faces.py','reitaku.jpg','vision-input.jpg','detected-faces.jpg','detected-boxes.csv','challenge-face-detection.ipynb']
        if week==12:files+=['click_model.py','click_game.py']
        if week==13:files+=['stretch-shooter.py','workshop-tkinter.ipynb']
        with zipfile.ZipFile(folder/'starter-files.zip','w') as archive:
            for name in files:
                file=folder/name
                if not file.exists():raise FileNotFoundError(file)
                item=zipfile.ZipInfo(f'week-{week:02}/'+name,date_time=(2026,11,11,0,0,0) if week==7 else (2026,11,6,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(item,file.read_bytes())
    report=[dict(week=w,title=s['title'],slides=len(s['slides']),date=s['date']) for w,s in W.items()]
    write(ROOT/'tools/course-flow-manifest.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Built:',', '.join(f'W{x["week"]}: {x["slides"]} slides' for x in report))

if __name__=='__main__':main()
