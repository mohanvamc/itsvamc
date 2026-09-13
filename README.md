# itsvamc

My personal portfolio/CV site, hosted free on GitHub Pages.

**Live site:** https://mohanvamc.github.io/itsvamc/

## How this works

All real content lives in plain Markdown/YAML files under `content/`:

- `content/profile.yml` — name, title, tagline, contact links, resume path
- `content/about.md` — the About section
- `content/skills.md` — skills grouped under `## Category` headings
- `content/experience.md` — work history, one job per block separated by `===`
- `content/credentials.md` — certifications and education
- `content/projects/*.md` — one file per project; add a new `.md` file here to add a project card
- `assets/resume/` — the downloadable resume PDF

To edit the site, just edit these Markdown/YAML files (works great from Obsidian or any text editor) — no HTML or JS required.

## Building

After editing content, regenerate the static site:

```bash
pip install -r requirements.txt
python3 build.py
```

This writes `index.html` and `resume.html` at the repo root, which is what GitHub Pages serves directly from the `gh-pages` branch.

A GitHub Action (`.github/workflows/build.yml`) also runs this automatically on every push to `gh-pages`, so pushing content changes alone is enough — the build and commit of the generated HTML happens for you.

## Repo layout

```
content/        source of truth (Markdown/YAML you edit)
templates/      Jinja2 HTML templates + CSS (rarely touched)
assets/         resume PDF, images
build.py        the whole build script (~130 lines, pure Python)
index.html      generated output — served by GitHub Pages, do not hand-edit
resume.html     generated output — served by GitHub Pages, do not hand-edit
```
