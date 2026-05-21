#!/usr/bin/env python3
"""
Ekurhuleni Underground — Issue Builder
--------------------------------------
Pipeline:  issue{N}.md  →  parse  →  Jinja2 render  →  issue{N}.html

Usage:
    python build_issue.py issues/issue18.md
    python build_issue.py issues/issue18.md --out ../issue18.html
"""

import re
import sys
import argparse
from pathlib import Path

import frontmatter          # pip install python-frontmatter
import markdown             # pip install markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape


# ── Markdown converter ────────────────────────────────────────────────────────

MD = markdown.Markdown(extensions=["extra", "smarty"])

def md_to_html(text: str) -> str:
    """Convert a markdown string to an HTML fragment, wrapping bare paragraphs."""
    MD.reset()
    raw = MD.convert(text.strip())
    # Wrap bare <p> tags so the template can apply class="body" via CSS cascade
    raw = re.sub(r"<p>", '<p class="body">', raw)
    return raw


# ── Section extractor ─────────────────────────────────────────────────────────

def extract_sections(body: str) -> dict:
    """
    Split the markdown body on ## SECTION_NAME markers.
    Returns a dict of { 'SECTION_NAME': 'raw markdown content' }.
    """
    pattern = re.compile(r"^## ([A-Z0-9_]+)\s*$", re.MULTILINE)
    parts   = pattern.split(body)

    # parts is: [preamble, NAME1, content1, NAME2, content2, ...]
    sections = {}
    for i in range(1, len(parts) - 1, 2):
        name    = parts[i].strip()
        content = parts[i + 1].strip()
        sections[name] = content
    return sections


# ── Essay section builder ─────────────────────────────────────────────────────

ESSAY_LABELS = [
    "Section I — The Observation",
    "Section II — The Hidden System",
    "Section III — The Broader Insight",
    "Section IV — The Antifragile Angle",
]

def build_essay_sections(sections: dict, pull_quote: str) -> list:
    """
    Assemble the four essay sections with labels.
    The pull quote is injected after Section I.
    """
    keys = ["ESSAY_SECTION_I", "ESSAY_SECTION_II", "ESSAY_SECTION_III", "ESSAY_SECTION_IV"]
    result = []
    for i, key in enumerate(keys):
        raw  = sections.get(key, "")
        html = md_to_html(raw) if raw else ""
        result.append({
            "label":      ESSAY_LABELS[i],
            "html":       html,
            "pull_quote": pull_quote if i == 0 else None,
        })
    return result


# ── Profile builder ───────────────────────────────────────────────────────────

def build_profiles(sections: dict) -> list:
    """Extract the three hidden-economy micro-profiles."""
    profiles = []
    for n in range(1, 4):
        title_key    = f"PROFILE_{n}_TITLE"
        location_key = f"PROFILE_{n}_LOCATION"
        body_key     = f"PROFILE_{n}_BODY"
        profiles.append({
            "title":    sections.get(title_key, f"Profile {n}").strip(),
            "location": sections.get(location_key, "").strip(),
            "html":     md_to_html(sections.get(body_key, "")),
        })
    return profiles


# ── Main build function ───────────────────────────────────────────────────────

def build(md_path: Path, template_dir: Path, out_path: Path) -> None:
    # 1. Parse frontmatter + body
    post     = frontmatter.load(str(md_path))
    meta     = dict(post.metadata)
    sections = extract_sections(post.content)

    # 2. Assemble template context
    pull_quote = meta.get("essay_pull_quote", "")

    context = {
        # Frontmatter scalars
        **meta,
        # Rendered HTML blocks
        "theme_html":    md_to_html(sections.get("THEME_ANALYSIS", "")),
        "editorial_html": md_to_html(sections.get("EDITORIAL", "")),
        "essay_sections": build_essay_sections(sections, pull_quote),
        "profiles":       build_profiles(sections),
        "map_html":       md_to_html(sections.get("MAP", "")),
        "number_html":    md_to_html(sections.get("NUMBER_BODY", "")),
        "closing_html":   md_to_html(sections.get("CLOSING", "")),
    }

    # 3. Render via Jinja2
    env  = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html"]),
    )
    # We push safe HTML via | safe in the template, so disable auto-escape for our vars
    env  = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,          # content is already trusted HTML from md_to_html
    )
    tmpl = env.get_template("issue_template.html.j2")
    html = tmpl.render(**context)

    # 4. Write output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"✓  Built {out_path}  ({len(html):,} bytes, "
          f"~{len(html.split()) } words in HTML)")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build an Ekurhuleni Underground issue HTML.")
    parser.add_argument("md_file",  type=Path, help="Path to the issue markdown file")
    parser.add_argument("--out",    type=Path, default=None,
                        help="Output HTML path (default: same dir as md, .html extension)")
    parser.add_argument("--templates", type=Path,
                        default=Path(__file__).parent / "templates",
                        help="Directory containing issue_template.html.j2")
    args = parser.parse_args()

    md_path = args.md_file.resolve()
    if not md_path.exists():
        sys.exit(f"Error: {md_path} not found")

    out_path = args.out.resolve() if args.out else md_path.with_suffix(".html")

    print(f"Building:  {md_path.name}  →  {out_path.name}")
    build(md_path, args.templates.resolve(), out_path)


if __name__ == "__main__":
    main()
