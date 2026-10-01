# 2026–2 Programming: 100-minute teaching flow

> This file preserves earlier teaching-planning notes. The current student-facing schedule and grading policy are in `content/weeks/`, `content/course-guide.md`, and `content/final-project.md`.

## Teaching model

This is an introductory, workshop-first course. Students should leave each meeting having made something run, changed it deliberately, and explained one result. Slides frame the problem and demonstrate only the next move; they are not the lesson itself.

### Default 100-minute rhythm

| Time | Purpose | What happens |
|---:|---|---|
| 0–10 | Arrive / reconnect | Open the working folder, retrieval prompt or a short demo of last week's student work. |
| 10–25 | Mini-lecture | One idea, one live example, one common mistake, and the week's challenge brief. Never introduce every feature of the notebook. |
| 25–50 | Fundamentals / “boring” notebook | Students work through selected cells in pairs or individually. Pause twice for a check-in. Unfinished cells become homework only when the challenge needs class time. |
| 50–55 | Reset | Save, commit when appropriate, and state the challenge minimum. |
| 55–90 | Build challenge | Students adapt the week's idea into their own small program or investigation. Teacher circulates, unblocks, and asks for explanations rather than taking over keyboards. |
| 90–100 | Share / exit | 2–4 rapid shares, a visible submission checklist, and a one-sentence exit ticket: “What changed when…?” |

### Operating rules

- Keep slides to 10–20 minutes, with a live prediction or tiny code change every few minutes.
- The fundamentals notebook is practice, not a performance. Mark the must-do cells; label optional depth clearly.
- Every challenge has a **minimum viable submission**, two or three extension paths, and one short reflection prompt.
- Use GitHub for work worth keeping. Do not let a Git problem erase a programming lesson: accept a local file/screenshot temporarily, then repair the workflow in a support window.
- Start class by showing one or two student artifacts from the previous week, with permission. It makes quality concrete and gives revision a purpose.

## Weekly flow

### Week 1 — First instruction / build the workspace

**Concept:** Python runs precise instructions; a notebook is a place to write, run, and explain them.

| Segment | Plan |
|---|---|
| Mini-lecture (15 min) | What programming is; `print()`, code cell versus Markdown cell, Run All versus running one cell, and the idea that errors are useful evidence. Show one deliberately broken line and fix it. |
| Fundamentals (35 min) | Use `fundamentals-first-code.ipynb`. Students run every cell, change strings/numbers, then create two explained code cells. Keep this fully in class because environment friction will be high. |
| Build challenge (35 min) | **My first program:** make a tiny “about me,” calculator, or odd/even program. It must have a title, two code cells, visible output, and a one-sentence explanation for each. |
| Finish (15 min) | Folder/kernel check, photograph the successful workspace if needed, and exit ticket: “What exact instruction made the output change?” |

**Submission:** notebook or a screenshot/temporary LMS upload; GitHub is not required yet.

### Week 2 — Variables and data types / make an input travel

**Concept:** names store values; type and conversion determine what operations can happen.

| Segment | Plan |
|---|---|
| Mini-lecture (15 min) | Variables, strings/numbers, `input()`, `int()`/`float()`, f-strings, and `=` versus `==`. Use a personal calculator example. |
| Fundamentals (30 min) | Selected must-do cells from `fundamentals-variables-data-types.ipynb`: calculation, variables, input, conversion, and f-strings. Unfinished extension cells can be homework. |
| Build challenge (40 min) | **Useful calculator:** students choose a use case—travel budget, café bill, game score, temperature conversion, club fee, etc. It must take one input, calculate a result, and present a readable sentence. Earthquake preview is a 5-minute teaser, not a required task. |
| Finish (15 min) | Partner test: each student gives a classmate one input and checks whether the output makes sense. |

**Submission:** Week 02 notebook; 3–4 sentence reflection including one changed test value.

### Week 3 — Collections / establish GitHub

**Concept:** lists and dictionaries keep related values together; GitHub records work people can revisit.

| Segment | Plan |
|---|---|
| Mini-lecture (15 min) | Show list indexing and a dictionary lookup, then explain repository / commit / push using a visible before-and-after file. Do not teach the whole Git command vocabulary. |
| Fundamentals (25 min) | Must-do portions of `fundamentals-collections.ipynb`: list creation, indexing, append, dictionary lookup. |
| Build challenge (45 min) | **Create the “me” repository:** photo/avatar, a readable self-introduction, three useful links, and one short Python file or notebook containing a collection about the student (favorites, schedule, team, etc.). Students who finish help classmates. |
| Finish (15 min) | Commit/push clinic and browser verification. Students who are blocked submit a local copy and a setup-status form rather than losing the week. |

**Submission:** GitHub repository URL. **Homework option:** finish SSH/Git configuration and make the first commit by the following week.

### Week 4 — Conditionals / make a chatbot choose

**Concept:** `if` / `elif` / `else` turn conditions into paths through a program.

| Segment | Plan |
|---|---|
| Mini-lecture (15 min) | Comparisons, Boolean logic, indentation, and the three-path pattern. Live-code a simple score classifier and predict boundary cases. |
| Fundamentals (25 min) | Core classifier cells in `fundamentals-conditionals.ipynb`. Make 60/59 and equal/not-equal cases non-negotiable. |
| Build challenge (45 min) | **Chatbot with a personality:** adapt `challenge-chatbot.ipynb`. Minimum: three user choices and three distinct responses. Extensions: moods, remembered name, random question, image, history counter. |
| Finish (15 min) | Three live chatbot demonstrations; GitHub recovery clinic for students still not connected. |

**Submission:** committed chatbot notebook plus a short note naming one condition and its possible outcomes.

### Week 5 — For loops / look for a pattern in Japan

**Concept:** a `for` loop applies one process to changing items; an accumulator or new list remembers results.

| Segment | Plan |
|---|---|
| Mini-lecture (15 min) | `for`, `range()`, loop variable, accumulator, and the off-by-one trap. Draw one loop's changing values rather than showing many syntax variations. |
| Fundamentals (25 min) | Essential cells from `fundamentals-for-loops.ipynb`: iterate, total, filter, build a list. |
| Build challenge (45 min) | **Japan demographics mini-report:** use `challenge-japan-demographics.ipynb`. Minimum: answer one question with a loop and one condition, show the result, and write one finding in Markdown. Extensions: ranking, classification, population density, chart. |
| Finish (15 min) | Gallery walk: students leave one question or observation on another student's result. |

**Submission:** GitHub notebook. Make the report reflection homework only if students need the whole build time.

### Week 6 — While loops / live earthquake impact

**Concept:** a `while` loop continues while a condition remains true; state must change so the loop can stop.

| Segment | Plan |
|---|---|
| Mini-lecture (15 min) | Counter, condition, update, infinite loop, and `break`. Live-code a number guesser and intentionally omit the update once. |
| Fundamentals (25 min) | Essential timer/password/guessing sections of `fundamentals-while-loops.ipynb`. |
| Build challenge (45 min) | **Earthquake impact visualization:** use `challenge-earthquakes.ipynb` and the snapshot as the reliable default; live USGS data is an optional enhancement. Minimum: filtered result plus one chart/map and a 200–400 character Japanese summary. |
| Finish (15 min) | Check that every project is saved and that data-source/file-path problems have a recovery plan. |

**Submission:** committed notebook, one visible chart/map, Japanese summary. This is the first substantial portfolio artifact.

### Week 7 — Logic plus loops / improve together

**Concept:** sequence, selection, and repetition combine into an algorithm; `break` and `continue` make control intentional.

| Segment | Plan |
|---|---|
| Mini-lecture (12 min) | Trace a loop with a condition; show when `break` saves work and when it would be wrong. |
| Fundamentals (23 min) | Selected algorithm-tracing and `break`/`continue` cells from `fundamentals-logic-loops.ipynb`. |
| Build challenge (50 min) | **Earthquake upgrade studio:** groups inspect Week 6 work, select one improvement, and implement it. Possible improvements: clearer filtering, correct labels, a new question, a second view, or a better explanation. Each student still commits their own revised notebook or clearly identified contribution. |
| Finish (15 min) | Lightning group share: “We changed ___ because ___; now the reader can see ___.” |

**Submission:** revision link plus a short individual change log. This is a feedback/revision week, not a new large homework task.

### Week 8 — Review and investigation / bicycle theft

**Concept:** basic Python supports an investigation when the question, evidence, and recommendation connect.

| Segment | Plan |
|---|---|
| Mini-lecture (10 min) | Open-book retrieval quiz (rather than slides) followed by how to form an investigable question from a table. |
| Fundamentals (15 min) | Review only the quiz errors as a class; do not spend the session re-teaching every topic. |
| Build challenge (60 min) | **Bicycle-theft prevention report:** use the brief and dataset. Minimum: one question, one summary/table, one chart, one written finding, and one prevention proposal. Extensions: time/location comparison, map, stronger visual design, limitations section. |
| Finish (15 min) | Peer review with a two-question protocol: “What is the claim?” and “Which output supports it?” |

**Submission:** report notebook. This is an appropriate week for a polished homework finish.

### Week 9 — Functions / tell a disaster story

**Concept:** a function packages a useful process; parameters change inputs and `return` gives a result back.

| Segment | Plan |
|---|---|
| Mini-lecture (18 min) | Define/call, parameter, local variable, `return` versus `print`. Write one reusable chart helper in front of the class. |
| Fundamentals (25 min) | Must-do function cells from `fundamentals-functions.ipynb`, including a function that returns a value. |
| Build challenge (42 min) | **Disaster data story:** begin `challenge-disaster-story.ipynb`. Minimum: a chosen focus/question, two visualizations, three observations, and a Markdown conclusion. |
| Finish (15 min) | Students write the question and first chart before leaving; remaining interpretation can become homework. |

**Submission:** GitHub notebook due before Week 10. Require a question in the title to discourage generic charts.

### Week 10 — Functions plus loops / create a small analysis system

**Concept:** a loop calling a function applies one well-defined process across changing inputs.

| Segment | Plan |
|---|---|
| Mini-lecture (15 min) | Refactor copied chart code into a parameterized function, then loop through two countries/types. Emphasize readable names and sample output. |
| Fundamentals (25 min) | Use `lab-functions-loops.ipynb` to trace and alter existing examples. |
| Build challenge (45 min) | **Disaster analysis system:** extend `challenge-disaster-systems.ipynb`. Minimum: one student-written function, one loop calling it more than once, and two results/graphs that answer a comparison question. |
| Finish (15 min) | Code walkthrough pairs: partner identifies function input, output, and what changes each loop iteration. |

**Submission:** notebook plus a 100–200 word explanation of the abstraction. This can supersede Week 9's work rather than becoming a separate heavy project.

### Week 11 — Objects, modules, and responsible AI / face detection

**Concept:** methods belong to objects; modules package capabilities; powerful tools need limits and context.

| Segment | Plan |
|---|---|
| Mini-lecture (15 min) | `text.lower()`, `list.append()`, `import math`; then a short, concrete discussion of consent, privacy, false detections, and why face detection is not identity recognition. |
| Fundamentals (20 min) | Selected string methods and `math` examples in `fundamentals-objects-modules.ipynb`. |
| Build challenge (50 min) | **Image-analysis lab:** face-detection notebook minimum is one appropriate image, visible detection result, count/observation, and strengths/limits reflection. Offer a no-install fallback: use an already prepared output/image, analyze detection conditions, or make a non-face image-analysis notebook with OpenCV/PIL if the model environment fails. |
| Finish (15 min) | Ethics/limitations share, not just “it worked” demonstrations. |

**Submission:** notebook and reflection. Do not require students to use images of classmates or strangers.

### Week 12 — Retrieval, repair, and project proposal

**Concept:** programming fluency is finding, adapting, testing, and explaining a solution.

| Segment | Plan |
|---|---|
| Mini-lecture (10 min) | Explain open-book expectations, debugging workflow, and how the final assessment connects skills rather than rewards memorization. |
| Fundamentals (40 min) | `review-practice.ipynb`, with a visible must-do target: Q1–Q7. Students use notes/search responsibly and run the grader only at the end. Correct the file reference to `study-data.csv` before release. |
| Build challenge (35 min) | **Repair or proposal studio:** students either improve an earlier portfolio artifact or draft a one-page final-project proposal: question/user, dataset or inputs, required Python concepts, intended output, and first milestone. |
| Finish (15 min) | Individual conference/checkpoint: identify the one skill each student should practice before the final. |

**Submission:** completed review notebook; optional project proposal becomes required if a project component is adopted.

### Week 13 — Interface / make a small usable app

**Concept:** event-driven programs wait for a person; a button connects an input to a function and visible output.

| Segment | Plan |
|---|---|
| Mini-lecture (15 min) | Run a prepared Tkinter app from a `.py` file; explain window, widget, callback, and `mainloop()` only as needed. |
| Fundamentals (25 min) | Guided sections of `workshop-tkinter.ipynb`: window, label, input, button, result display. Keep a known-good starter `.py` ready. |
| Build challenge (45 min) | **One-screen app:** even/odd checker, sum calculator, word combiner, prime checker, quiz, budget helper, or student idea. Minimum: input, button, function, and clearly displayed result. |
| Finish (15 min) | App demo circle and final-assessment briefing. |

**Submission:** `.py` file, screenshot/video, and GitHub link if technically possible. Do not make GitHub rendering of GUI the proof of success.

### Week 14 — Final assessment / evidence of independent work

**Concept:** use code to turn a question into inspectable evidence.

| Segment | Plan |
|---|---|
| Assessment (50–60 min) | Keep the Python fundamentals exam from `final-exam.ipynb`, but use a carefully scoped version that samples variables, collections, conditions, loops, functions, and reading a CSV—not ten unrelated tricks. It should be open-notes if that matches the course's actual practice. |
| Project/report (35–40 min) | Use the happiness-data report as a final build or presentation checkpoint. Students create a clear question, three analyses, three appropriate charts, Markdown explanations, and a conclusion. |
| Finish (5–10 min) | Submission check, a short reflection on the first program versus final work, and celebration/showcase of selected artifacts. |

## Current final-assessment model

The student-facing policy is maintained in `content/course-guide.md` and `content/final-project.md`. Weeks 01–12 carry the weekly 3-point assignments; the project is submitted in Week 13; the individual practical challenge is held in Week 14.

| Component | Weight | Evidence |
|---|---:|---|
| Weekly take-home assignments | 60% | Twelve Week 01–12 submissions, each graded 0–3 points; maximum 36 points. |
| Final project | 20% | Small, runnable, tested work with a brief decision and verification record; submitted through UNIPA in Week 13. |
| Individual in-class challenge | 20% | Week 14 code reading, modification, testing, and explanation. |

The project and in-class challenge assess different outcomes. Do not count the Week 13 project as an additional 3-point weekly assignment, or require a second project submission in Week 14.

## Recurring rubrics

Use the same short rubric language for most challenges:

| Criterion | What students must show |
|---|---|
| Works | Code runs or the student clearly documents the remaining error and attempted repair. |
| Uses this week's idea | The targeted concept is present and used meaningfully, not pasted decoratively. |
| Makes a claim or result visible | Output, chart, interface, or report can be inspected. |
| Explains | Markdown/reflection states what the result means and one choice or limitation. |
| Extends (optional) | Originality, a stronger question, useful feature, improved design, or thoughtful iteration. |

## Pre-semester preparation priorities

1. Create a one-page student setup checklist and a Week 1 fallback plan for Python/Jupyter failures.
2. Prepare a GitHub troubleshooting station for Week 3 (account, Git installation, SSH/browser authentication, repository, first push).
3. Mark the exact **must-do** cells in every fundamentals notebook; keep enrichment cells visibly optional.
4. Standardize a GitHub submission template: title, question/purpose, code, visible output, short reflection, source/data note.
5. Update the Week 12 CSV filename and remaining 2025 labels before publication.
6. Test every challenge on a clean student-like computer, especially data paths, map dependencies, and the Week 11 face-detection environment.
