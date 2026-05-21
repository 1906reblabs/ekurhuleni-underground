# Ekurhuleni Underground

**The hidden systems of the East Rand**

A weekly long-form publication uncovering the economic geography, informal networks, and overlooked infrastructure of Ekurhuleni Metropolitan Municipality.

🌐 **Live site:** https://1906reblabs.github.io/ekurhuleni-underground/

---

## How this repo works

Content is written in Markdown. A Python + Jinja2 pipeline converts it to HTML. GitHub Actions runs the pipeline automatically on every push. GitHub Pages serves the HTML.

```
Write issue18.md  →  git push  →  Actions builds issue18.html  →  Pages serves it
```

You never touch HTML directly. The templates handle all styling and structure.

---

## Repository structure

```
ekurhuleni-underground/
│
├── .github/
│   └── workflows/
│       └── build.yml            ← GitHub Actions: auto-build on push
│
├── issues/                      ← SOURCE FILES (edit these)
│   ├── issue1.md
│   ├── issue2.md
│   └── issue18.md
│
├── templates/                   ← Jinja2 templates (edit rarely)
│   ├── issue_template.html.j2   ← layout for every issue page
│   └── index_template.html.j2  ← layout for the homepage
│
├── build_all.py                 ← builds all issues + index.html
├── build_issue.py               ← builds a single issue (for local testing)
├── requirements.txt             ← Python dependencies
│
├── index.html                   ← GENERATED — do not edit manually
├── issue1.html                  ← GENERATED — do not edit manually
├── issue18.html                 ← GENERATED — do not edit manually
│
├── about.html                   ← STATIC — edit directly
├── partners.html                ← STATIC — edit directly
├── privacy.html                 ← STATIC — edit directly
├── terms.html                   ← STATIC — edit directly
└── sitemap.xml                  ← STATIC — update manually each week
```

---

## Writing a new issue

### 1. Create the Markdown file

Copy the previous issue file and rename it:

```bash
cp issues/issue18.md issues/issue19.md
```

Edit `issue19.md`. The file has two parts:

**YAML frontmatter** (between `---` markers) — all metadata:

```yaml
---
issue: 19
date: "29 May 2026"
date_iso: "2026-05-29"
title: "Your Issue Title"
deck: "One-sentence summary of the issue for the homepage card."
theme_name: "The Theme Name"
theme_subtitle: "Why this theme matters for the long-term economic story of Ekurhuleni"
editorial_section_title: "Your Editorial Section Title"
essay_title: "Your Long Essay Title"
essay_pull_quote: "A single compelling sentence pulled from the essay body."
map_place: "Specific Place Name, Area"
map_coords: "26°XX′S  28°XX′E"
number_value: "123,456"
number_label: "What the number measures and why it matters"
closing_section_title: "Your Closing Section Title"
next_issue: "**Next Theme Title** — one teaser sentence."
byline: "— Ekurhuleni Underground, 29 May 2026"
url: "https://1906reblabs.github.io/ekurhuleni-underground/"
---
```

**Body sections** — prose content, one `## SECTION_NAME` per block:

```markdown
## THEME_ANALYSIS
Full theme analysis paragraphs. Use **bold** for Deep Story, micro-stories, etc.

## EDITORIAL
Four editorial paragraphs (~400 words total).

## ESSAY_SECTION_I
Section I prose — The Observation (~200 words).

## ESSAY_SECTION_II
Section II prose — The Hidden System (~300 words).

## ESSAY_SECTION_III
Section III prose — The Broader Insight (~200 words).

## ESSAY_SECTION_IV
Section IV prose — The Antifragile Angle (~200 words).

## PROFILE_1_TITLE
The Name of Operation One

## PROFILE_1_LOCATION
Area / Corridor Name

## PROFILE_1_BODY
~80-word profile paragraph.

## PROFILE_2_TITLE
...

## PROFILE_2_LOCATION
...

## PROFILE_2_BODY
...

## PROFILE_3_TITLE
...

## PROFILE_3_LOCATION
...

## PROFILE_3_BODY
...

## MAP
Map of the week description (~150 words).

## NUMBER_BODY
East Rand Number explanatory paragraph (~80 words).

## CLOSING
Closing reflection (~100 words).
```

### 2. Push to GitHub

```bash
git add issues/issue19.md
git commit -m "content: add issue 19 — Your Title"
git push
```

That's it. GitHub Actions takes over from here.

---

## What GitHub Actions does automatically

When you push, the workflow in `.github/workflows/build.yml`:

1. **Checks out** the repo
2. **Installs** `jinja2`, `python-frontmatter`, `markdown`
3. **Runs** `python build_all.py --changed`
   - Scans `issues/` for every `issue*.md`
   - Builds `issueN.html` in the repo root for any `.md` newer than its `.html`
   - Regenerates `index.html` with the full updated archive
4. **Commits** the new/changed HTML files back to `main` with message `build: auto-generate HTML [skip ci]`
5. **Pushes** — GitHub Pages redeploys automatically (usually live within 1–2 minutes)

The `[skip ci]` tag in the commit message prevents the bot's commit from triggering another workflow run.

---

## One-time GitHub repo setup

### 1. Create the repo

```bash
# On GitHub: create a new repo named  ekurhuleni-underground
# Then locally:
git clone https://github.com/YOUR_USERNAME/ekurhuleni-underground.git
cd ekurhuleni-underground
```

### 2. Copy your files into the repo

```
issues/issue1.md … issue18.md
templates/issue_template.html.j2
templates/index_template.html.j2
build_all.py
build_issue.py
requirements.txt
.github/workflows/build.yml
about.html  partners.html  privacy.html  terms.html  sitemap.xml
```

### 3. Run a local first build

```bash
pip install -r requirements.txt
python build_all.py
```

This generates all `issueN.html` and `index.html` locally.

### 4. Commit and push everything

```bash
git add .
git commit -m "init: full site with build pipeline"
git push
```

### 5. Enable GitHub Pages

Go to your repo on GitHub:

```
Settings → Pages → Source
→ Deploy from a branch
→ Branch: main   /   Folder: / (root)
→ Save
```

Your site will be live at:
`https://YOUR_USERNAME.github.io/ekurhuleni-underground/`

### 6. Enable write permissions for Actions

```
Settings → Actions → General → Workflow permissions
→ Read and write permissions   ← required so the bot can push HTML
→ Save
```

---

## Local development

Build a single issue without pushing:

```bash
python build_issue.py issues/issue19.md
# Output: issue19.html in the current directory
```

Force rebuild everything (e.g. after changing a template):

```bash
python build_all.py
# Rebuilds all issues and index.html regardless of modification times
```

Only rebuild changed issues (same logic as Actions uses):

```bash
python build_all.py --changed
```

Preview locally with Python's built-in server:

```bash
python -m http.server 8000
# Open http://localhost:8000
```

---

## Updating templates

If you change `issue_template.html.j2` or `index_template.html.j2`, the Actions workflow detects the change and triggers a **full rebuild** of all issues (the `--changed` flag is bypassed when templates change — remove it from `build.yml` line 55 if you want to force this explicitly, or just push a template edit and all HTML rebuilds automatically).

---

## Token efficiency vs old approach

| Approach | Tokens per issue | Notes |
|---|---|---|
| Generate full HTML | ~9,400 | CSS + structure + content in one pass |
| Generate Markdown only | ~5,800 | Content only; templates reused |
| **Saving** | **~38%** | Compounds over time |

By issue 40, the pipeline approach saves the equivalent of ~9 full issue generations.

---

## Publication: 1906 Reblabs

*Published weekly from Ekurhuleni, South Africa.*
*© 2026 1906 Reblabs. All rights reserved.*
