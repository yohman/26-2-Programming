# Weekly course content

Each file in `content/weeks/` is the live, editable source for one teaching week. The site reads these Markdown files directly when it loads—there is no build step.

`content/course-guide.md` drives `guide.html`: edit it to update learning goals, submission rules, and grading. The current plan is twelve 3-point assignments in Weeks 01–12 (60%), a Week 13 project (20%), and a Week 14 individual in-class challenge (20%). Keep the guide, `content/final-project.md`, and Weeks 10–14 aligned if this policy changes.

`content/final-project.md` drives the dedicated `final-project.html` page. Keep its `EN:` and `JP:` versions together in each section; the site shows only the selected language. Links to the project brief in weekly resource lists open this page, not the raw Markdown file.

Edit the front matter for the week number, titles, phase, and publication controls. The agenda renders: `Lecture Flow`, `In-Class Notebook`, `In-Class Challenge`, `Take-Home Assignment`, `Aha!`, `Takeaway`, and `Resources`. The In-Class Notebook should make independent Human Coding and carefully checked AI Completion clear. Keep the `EN:` and `JP:` lines for the bilingual layout.

Weeks 01–13 also have `homework_due` in front matter. Use a Japan-time ISO timestamp such as `2026-10-07T23:59:00+09:00`; the agenda displays its date and time above that week's homework. Week 14 has no take-home homework or `homework_due`.

```yaml
week: 1
publish_at: 2026-09-29T09:00:00+09:00
preview: true
```

`publish_at` uses Japan time. Week 01 is available; later weeks stay collapsed and locked until their `publish_at` time. Use `?preview=all` on `agenda.html` to inspect every week before release. The legacy `preview:` front-matter field is not used by the current renderer.

The two programming practices are intentional: every week requires independent tracing and writing; AI may support bounded completion and review, with the student responsible for checking every result. Every `Take-Home Assignment` must state what is due, how to submit, and what demonstrates individual understanding.

Resources use one line each:

```md
- [Lecture PDF](weeks/week-01/lecture.pdf) {lecture}
```

Valid resource types include `lecture`, `notebook`, `fundamentals`, `challenge`, `homework`, `data`, `experiment`, and `support`.
