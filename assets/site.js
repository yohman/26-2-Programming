const weeks = [
  {
    n:'01', phase:'WRITE', title:'Make a first instruction visible.', jp:'最初の一行を、実行してみる。',
    learn:'Set up Python, VS Code, and a Jupyter kernel; use print() to make output appear.',
    try:'Run tiny examples, then write two explained code cells of your own.',
    experiment:'Change the calculator and odd/even examples; predict the output before you run them.',
    make:'Create a Week 01 notebook with a title, two short programs, visible output, and an explanation for each.',
    aha:'A computer does not “know what you mean.” It only does the precise instruction that reaches it.',
    takeaway:'Writing code is making an intention executable.',
    resources:[['Lecture PDF','weeks/week-01/lecture.pdf','lecture'],['First experiments','weeks/week-01/fundamentals-first-code.ipynb','fundamentals']]
  },
  {
    n:'02', phase:'WRITE', title:'Give changing things a name.', jp:'値に名前をつけて、変化を追えるようにする。',
    learn:'Variables, strings, numbers, input, conversion, and f-strings.',
    try:'Build multiplication tables, circle calculations, and small input/output conversations.',
    experiment:'Open the earthquake preview and trace how a table can become a chart or map.',
    make:'Use the Fundamentals notebook to make one small program that accepts an input, changes a value, and explains its result.',
    aha:'In Python, = stores a value; == asks whether two values are the same.',
    takeaway:'A variable lets one change travel through a whole program.',
    resources:[['Lecture PDF','weeks/week-02/lecture.pdf','lecture'],['Fundamentals · variables & types','weeks/week-02/fundamentals-variables-data-types.ipynb','fundamentals'],['Earthquake preview','weeks/week-02/experiment-earthquake-preview.ipynb','experiment'],['Earthquake data','weeks/week-02/all-month-earthquakes.csv','data']]
  },
  {
    n:'03', phase:'WRITE', title:'Put many values in one place.', jp:'たくさんの値を、ひとまとまりとして扱う。',
    learn:'Lists, tuples, dictionaries, sets, indexing, and the difference between a value and a collection.',
    try:'Use a collection to hold scores, names, or key–value information instead of making a variable for every item.',
    experiment:'Create a GitHub repository, make a README, and see how a commit records a change.',
    make:'Publish a “me” repository: photo, readable self-introduction, and a useful list of links. Submit the repository URL.',
    aha:'One variable can point to a whole collection—and an index gives each item an address.',
    takeaway:'Collections let a program keep related things together.',
    resources:[['Lecture PDF','weeks/week-03/lecture.pdf','lecture'],['Fundamentals · collections','weeks/week-03/fundamentals-collections.ipynb','fundamentals'],['Git & GitHub tutorial','https://github.com/yohman/tutorials/blob/main/git_github_setup_jp.md','support']]
  },
  {
    n:'04', phase:'WRITE', title:'Let the program choose.', jp:'条件によって、次に進む道を変える。',
    learn:'if / elif / else, comparison, logical operators, and indentation as structure.',
    try:'Write small classifiers: scores, ages, temperatures, passwords, and rock-paper-scissors.',
    experiment:'Reverse engineer the chatbot, then change its moods, replies, memory, questions, or images.',
    make:'Adapt the chatbot into your own voice. Also improve and commit your GitHub “me” profile if it still needs work.',
    aha:'Indentation is not decoration in Python. Moving a line changes when—and whether—it runs.',
    takeaway:'A conditional gives code a choice, not a guess.',
    resources:[['Lecture PDF','weeks/week-04/lecture.pdf','lecture'],['Fundamentals · conditionals','weeks/week-04/fundamentals-conditionals.ipynb','fundamentals'],['Challenge · chatbot','weeks/week-04/challenge-chatbot.ipynb','challenge'],['Chatbot image','weeks/week-04/chatbot.jpg','support']]
  },
  {
    n:'05', phase:'REPEAT', title:'Do the useful part again.', jp:'同じ処理を、違うデータに何度も使う。',
    learn:'for loops, range(), accumulators, and building a new list one item at a time.',
    try:'Count sheep, total numbers, select items, and notice why range(10) ends at 9.',
    experiment:'Read Japan demographic data and use loops plus conditions to classify, rank, and compare prefectures.',
    make:'Turn the Japan demographics notebook into a small data report: make at least one finding and explain it in Markdown.',
    aha:'A loop is not copied code. It is one instruction applied to a changing value.',
    takeaway:'When the task repeats, write the process once.',
    resources:[['Lecture PDF','weeks/week-05/lecture.pdf','lecture'],['Fundamentals · for loops','weeks/week-05/fundamentals-for-loops.ipynb','fundamentals'],['Challenge · Japan demographics','weeks/week-05/challenge-japan-demographics.ipynb','challenge'],['Japan data','weeks/week-05/japan.csv','data']]
  },
  {
    n:'06', phase:'REPEAT', title:'Keep going until something changes.', jp:'「回数」ではなく、「続ける条件」を書く。',
    learn:'while loops, state, counters, stopping conditions, break, and the cause of an infinite loop.',
    try:'Build a timer, password check, and number-guessing game.',
    experiment:'Fetch live USGS earthquake data, filter it, inspect time and depth, then make a chart or map.',
    make:'Make an Impact visualization from the live earthquake feed. Commit a notebook, a chart or map, and a 200–400 character Japanese summary.',
    aha:'An infinite loop is not a stubborn computer—the condition never became false.',
    takeaway:'A loop needs both a reason to continue and a way to stop.',
    resources:[['Lecture PDF','weeks/week-06/lecture.pdf','lecture'],['Fundamentals · while loops','weeks/week-06/fundamentals-while-loops.ipynb','fundamentals'],['Challenge · live earthquakes','weeks/week-06/challenge-earthquakes.ipynb','challenge'],['Earthquake snapshot','weeks/week-06/earthquakes-snapshot.csv','data'],['USGS live feed ↗','https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv','support']]
  },
  {
    n:'07', phase:'REPEAT', title:'Build logic from three moves.', jp:'順次・分岐・繰り返しを組み合わせる。',
    learn:'Combining conditions and loops; break and continue; reading an algorithm as a sequence of decisions.',
    try:'Select evens, classify values, search a list, and stop when the job is done.',
    experiment:'Compare approaches with your group, choose a solution, and improve it together.',
    make:'Refine the Week 06 earthquake work with your group. Explain one change that made the analysis or visualization more useful.',
    aha:'Sequence, selection, and repetition are enough to describe an enormous range of algorithms.',
    takeaway:'Complex behavior is assembled from a few precise control moves.',
    resources:[['Lecture PDF','weeks/week-07/lecture.pdf','lecture'],['Fundamentals · logic + loops','weeks/week-07/fundamentals-logic-loops.ipynb','fundamentals'],['Week 06 challenge to refine','weeks/week-06/challenge-earthquakes.ipynb','challenge']]
  },
  {
    n:'08', phase:'REPEAT', title:'Find a pattern worth acting on.', jp:'データから、行動につながる発見をつくる。',
    learn:'Review the basics through an open-book quiz, then use counts, rankings, charts, and maps in a real investigation.',
    try:'Inspect the bicycle-theft table: locks, location, month, time, and victim characteristics.',
    experiment:'Ask what the raw table cannot answer directly; try a map and notice why an address needs coordinates.',
    make:'Produce a bicycle-theft report in a notebook with summary, analysis, at least one chart, Markdown explanation, and a prevention proposal.',
    aha:'A table can tell you where something happened; a map needs a transformation from address to coordinates.',
    takeaway:'Data becomes useful when it changes the question you can ask next.',
    resources:[['Lecture PDF','weeks/week-08/lecture.pdf','lecture'],['Challenge · bicycle theft','weeks/week-08/challenge-bicycle-theft.ipynb','challenge'],['Assignment brief','weeks/week-08/bicycle-theft-brief.md','support'],['Bicycle-theft data','weeks/week-08/bicycle-theft.csv','data']]
  },
  {
    n:'09', phase:'COMPOSE', title:'Give a useful process a name.', jp:'何度も使う処理を、関数としてまとめる。',
    learn:'Functions, parameters, local variables, return values, and why print() is not return.',
    try:'Make converters, calculations, maps, and summaries that accept different inputs.',
    experiment:'Use the EM-DAT disaster table to tell a data story from a question you care about.',
    make:'Create a disaster-story notebook: choose a focus, make at least two visualizations and three insights, then explain the conclusion in Markdown.',
    aha:'Defining a function does not run it. Calling it is the moment the stored process becomes behavior.',
    takeaway:'A function turns a repeated idea into a reusable tool.',
    resources:[['Lecture PDF','weeks/week-09/lecture.pdf','lecture'],['Fundamentals · functions','weeks/week-09/fundamentals-functions.ipynb','fundamentals'],['Challenge · disaster story','weeks/week-09/challenge-disaster-story.ipynb','challenge'],['EM-DAT data','weeks/week-09/emdat.csv','data']]
  },
  {
    n:'10', phase:'COMPOSE', title:'Make one tool do many jobs.', jp:'関数とループで、ひとつの分析をシステムにする。',
    learn:'Functions plus loops: parameterize a chart, then run it across disaster types or countries.',
    try:'Read the lab examples that generate multiple line charts, bar charts, and maps from the same data.',
    experiment:'Change an input condition, a country, a disaster type, or a time range—and see the same tool produce a new view.',
    make:'Extend the disaster story with your own function, sample output, and a loop that produces multiple results or graphs.',
    aha:'A loop calling a function is a small production line: same tool, changing input, many outputs.',
    takeaway:'Good abstraction lets one clear idea scale without copying code.',
    resources:[['Lecture PDF','weeks/week-10/lecture.pdf','lecture'],['Lab · functions + loops','weeks/week-10/lab-functions-loops.ipynb','fundamentals'],['Challenge · disaster systems','weeks/week-10/challenge-disaster-systems.ipynb','challenge'],['EM-DAT data','weeks/week-10/emdat.csv','data']]
  },
  {
    n:'11', phase:'COMPOSE', title:'Use the abilities already inside things.', jp:'オブジェクトとライブラリで、できることを広げる。',
    learn:'Objects, methods, modules, import, and the difference between a value and the operations it carries.',
    try:'Use string methods, math tools, and data-analysis modules; inspect what a module makes available.',
    experiment:'Use a face-detection notebook to detect, blur, replace, or collage faces in an image.',
    make:'Create a face-detection notebook around your own use case. Include an image, visible results, a short analysis, and a reflection on strengths and limits.',
    aha:'The dot in text.lower() or list.append() means “ask this particular thing what it knows how to do.”',
    takeaway:'Libraries are other people’s carefully packaged capabilities—use them with judgment.',
    resources:[['Lecture PDF','weeks/week-11/lecture.pdf','lecture'],['Fundamentals · objects & modules','weeks/week-11/fundamentals-objects-modules.ipynb','fundamentals'],['Challenge · face detection','weeks/week-11/challenge-face-detection.ipynb','challenge'],['Sample image','weeks/week-11/reitaku.jpg','support'],['Ultralytics ↗','https://github.com/ultralytics/ultralytics','support']]
  },
  {
    n:'12', phase:'MAKE', title:'Make the basics available on demand.', jp:'基本を自分の手に戻して、次の作品へつなぐ。',
    learn:'Review variables, collections, conditionals, loops, functions, and pandas with an open-book practice notebook.',
    try:'Complete the TODO cells and use the auto-check only after you have worked through the problems.',
    experiment:'Turn study time and score data into a tiny report: scatter plot, sorted table, and a written observation.',
    make:'Finish any missing work, improve an earlier submission, or choose an open-ended data/creative Python challenge.',
    aha:'Being allowed to look something up is not a shortcut—it is how programmers work when the next step is still theirs to decide.',
    takeaway:'Fluency means you can find, adapt, and explain a solution.',
    resources:[['Lecture PDF','weeks/week-12/lecture.pdf','lecture'],['Review practice','weeks/week-12/review-practice.ipynb','fundamentals'],['Study data','weeks/week-12/study-data.csv','data']]
  },
  {
    n:'13', phase:'MAKE', title:'Give the program a surface.', jp:'計算するだけのコードを、使えるアプリにする。',
    learn:'Tkinter windows, labels, inputs, buttons, callbacks, and event-driven behavior.',
    try:'Run a local .py file, then make an input produce a visible result in a small window.',
    experiment:'Change labels, placement, and the button’s action; study the optional shooter source as a larger Tkinter example.',
    make:'Make a small window app: an even/odd checker, sum calculator, word combiner, prime checker, or a new idea of your own.',
    aha:'A button does nothing by itself. It becomes interactive only when it is connected to a function.',
    takeaway:'An interface is code waiting for a person to trigger it.',
    resources:[['Workshop guide','weeks/week-13/workshop-tkinter.ipynb','lecture'],['Stretch · shooter source','weeks/week-13/stretch-shooter.py','challenge'],['Shooter cannon image','weeks/week-13/canon.png','support'],['Shooter UFO image','weeks/week-13/ufo.png','support']]
  },
  {
    n:'14', phase:'MAKE', title:'Ask a question only you can answer.', jp:'自分の問いを、データとコードで確かめる。',
    learn:'Bring the core pieces together: variables, collections, logic, loops, functions, pandas, analysis, and visualization.',
    try:'Complete the fundamentals section, then inspect the happiness dataset for a question that interests you.',
    experiment:'Compare countries, regions, years, and possible relationships; make claims that another person can inspect.',
    make:'Create a separate happiness-data report with a clear question, three analyses, three charts, Markdown explanation, and a conclusion. Submit the notebook URL.',
    aha:'The final program is not the point. The point is that you can turn a question into a process that produces evidence.',
    takeaway:'You can now make a computer help you think.',
    resources:[['Final exam brief','weeks/week-14/final-exam.ipynb','lecture'],['World happiness data','weeks/week-14/world-happiness-report.csv','data']]
  }
];

function link(label, href, kind) {
  const external = /^https?:/.test(href);
  return `<a class="resource-link" data-kind="${kind}" href="${href}"${external ? ' target="_blank" rel="noopener"' : ''}>${label}${external ? ' ↗' : ' ↓'}</a>`;
}

function agendaWeek(w) {
  return `<article class="week" id="week-${w.n}">
    <div class="week-number">${w.n}<small>${w.phase}</small></div>
    <div><h2>${w.title}</h2><p class="subtitle jp">${w.jp}</p>
      <div class="week-grid"><div class="week-path">
        <div><b>LEARN</b>${w.learn}</div><div><b>TRY</b>${w.try}</div><div><b>EXPERIMENT</b>${w.experiment}</div><div><b>MAKE</b>${w.make}</div>
      </div><aside class="week-insights"><div class="insight"><b>AHA!</b><p>${w.aha}</p></div><div class="insight"><b>TAKEAWAY</b><p>${w.takeaway}</p></div></aside></div>
      <div class="resources">${w.resources.map(([label,href,kind]) => link(label,href,kind)).join('')}</div>
    </div></article>`;
}

function renderAgenda() {
  const root = document.querySelector('[data-agenda]'); if (!root) return;
  const phaseStarts = { '01':'WRITE · write exact instructions', '05':'REPEAT · make a process travel', '09':'COMPOSE · build reusable tools', '12':'MAKE · shape a result of your own' };
  root.innerHTML = weeks.map(w => `${phaseStarts[w.n] ? `<div class="phase-band"><b>${phaseStarts[w.n]}</b><span>${w.n === '01' ? '01–04' : w.n === '05' ? '05–08' : w.n === '09' ? '09–11' : '12–14'}</span></div>` : ''}${agendaWeek(w)}`).join('');
}

function renderRoute() {
  const root = document.querySelector('[data-week-route]'); if (!root) return;
  root.innerHTML = weeks.map(w => `<a href="agenda.html#week-${w.n}"><span>${w.n}</span><small>${w.phase}</small></a>`).join('');
}

function renderMaterials() {
  const root = document.querySelector('[data-materials]'); if (!root) return;
  root.innerHTML = weeks.map(w => `<article class="material-row"><span class="num">W${w.n}</span><div><h3>${w.title}</h3><p class="jp">${w.jp}</p></div><div class="resources">${w.resources.map(([label,href,kind]) => link(label,href,kind)).join('')}</div></article>`).join('');
}

function setupMenu() {
  const button = document.querySelector('.menu-toggle'); const nav = document.querySelector('.site-nav');
  if (!button || !nav) return;
  button.addEventListener('click', () => { const open = nav.classList.toggle('open'); button.setAttribute('aria-expanded', String(open)); });
}

document.addEventListener('DOMContentLoaded', () => { renderRoute(); renderAgenda(); renderMaterials(); setupMenu(); });
