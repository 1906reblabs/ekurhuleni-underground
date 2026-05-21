#!/usr/bin/env python3
"""
Ekurhuleni Underground — Full Site Builder
------------------------------------------
Scans issues/ for every *.md file, builds issue{N}.html in the repo
root, then regenerates index.html from the complete archive.

Usage:
    python build_all.py              # build everything
    python build_all.py --changed    # only rebuild issues whose .md is
                                     # newer than the corresponding .html
Run from the repo root.
"""

import re
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

import frontmatter
import markdown as md_lib
from jinja2 import Environment, FileSystemLoader

# ── shared markdown converter ─────────────────────────────────────────────────

_MD = md_lib.Markdown(extensions=["extra", "smarty"])

def md_to_html(text: str) -> str:
    _MD.reset()
    raw = _MD.convert(text.strip())
    return re.sub(r"<p>", '<p class="body">', raw)


# ── section extractor ─────────────────────────────────────────────────────────

def extract_sections(body: str) -> dict:
    pattern = re.compile(r"^## ([A-Z0-9_]+)\s*$", re.MULTILINE)
    parts   = pattern.split(body)
    sections = {}
    for i in range(1, len(parts) - 1, 2):
        sections[parts[i].strip()] = parts[i + 1].strip()
    return sections


# ── essay + profile builders ──────────────────────────────────────────────────

ESSAY_LABELS = [
    "Section I — The Observation",
    "Section II — The Hidden System",
    "Section III — The Broader Insight",
    "Section IV — The Antifragile Angle",
]

def build_essay_sections(sections: dict, pull_quote: str) -> list:
    keys = ["ESSAY_SECTION_I", "ESSAY_SECTION_II",
            "ESSAY_SECTION_III", "ESSAY_SECTION_IV"]
    result = []
    for i, key in enumerate(keys):
        result.append({
            "label":      ESSAY_LABELS[i],
            "html":       md_to_html(sections.get(key, "")),
            "pull_quote": pull_quote if i == 0 else None,
        })
    return result

def build_profiles(sections: dict) -> list:
    profiles = []
    for n in range(1, 4):
        profiles.append({
            "title":    sections.get(f"PROFILE_{n}_TITLE", f"Profile {n}").strip(),
            "location": sections.get(f"PROFILE_{n}_LOCATION", "").strip(),
            "html":     md_to_html(sections.get(f"PROFILE_{n}_BODY", "")),
        })
    return profiles


# ── single issue builder ──────────────────────────────────────────────────────

def build_issue(md_path: Path, env: Environment, out_dir: Path) -> dict:
    """Build one issue HTML. Returns archive metadata dict."""
    post     = frontmatter.load(str(md_path))
    meta     = dict(post.metadata)
    sections = extract_sections(post.content)

    context = {
        **meta,
        "theme_html":     md_to_html(sections.get("THEME_ANALYSIS", "")),
        "editorial_html": md_to_html(sections.get("EDITORIAL", "")),
        "essay_sections": build_essay_sections(sections, meta.get("essay_pull_quote", "")),
        "profiles":       build_profiles(sections),
        "map_html":       md_to_html(sections.get("MAP", "")),
        "number_html":    md_to_html(sections.get("NUMBER_BODY", "")),
        "closing_html":   md_to_html(sections.get("CLOSING", "")),
    }

    tmpl     = env.get_template("issue_template.html.j2")
    html     = tmpl.render(**context)
    slug     = f"issue{meta['issue']}"
    out_path = out_dir / f"{slug}.html"
    out_path.write_text(html, encoding="utf-8")

    # parse date for archive / JSON-LD
    date_str = str(meta.get("date", ""))
    try:
        dt       = datetime.strptime(date_str, "%d %B %Y")
        date_iso = dt.strftime("%Y-%m-%d")
    except ValueError:
        date_iso = meta.get("date_iso", "2026-01-01")

    print(f"  ✓  {slug}.html  ({len(html):,} bytes)")
    return {
        "num":        int(meta["issue"]),
        "slug":       slug,
        "title":      meta.get("title", ""),
        "subtitle":   meta.get("theme_name", meta.get("title", "")),
        "deck":       meta.get("deck", ""),
        "date":       date_str,
        "date_short": date_str,
        "date_iso":   date_iso,
    }


# ── index builder ─────────────────────────────────────────────────────────────

def build_index(archive: list, env: Environment, out_dir: Path) -> None:
    """Render the homepage from the full sorted archive."""
    latest = archive[0]
    tmpl   = env.get_template("index_template.html.j2")
    html   = tmpl.render(archive=archive, latest=latest)
    out    = out_dir / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"  ✓  index.html  ({len(html):,} bytes)  [{len(archive)} issues]")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build all Ekurhuleni Underground issues.")
    parser.add_argument("--changed", action="store_true",
                        help="Only rebuild .md files newer than their .html output")
    parser.add_argument("--root",    type=Path, default=Path("."),
                        help="Repo root directory (default: current directory)")
    args = parser.parse_args()

    root       = args.root.resolve()
    issues_dir = root / "issues"
    tmpl_dir   = root / "templates"

    if not issues_dir.exists():
        sys.exit(f"Error: {issues_dir} not found. Run from repo root.")
    if not tmpl_dir.exists():
        sys.exit(f"Error: {tmpl_dir} not found.")

    # Collect all issue markdown files
    md_files = sorted(issues_dir.glob("issue*.md"),
                      key=lambda p: int(re.search(r"\d+", p.stem).group()))

    if not md_files:
        sys.exit("No issue*.md files found in issues/")

    env = Environment(loader=FileSystemLoader(str(tmpl_dir)), autoescape=False)

    print(f"\nBuilding {len(md_files)} issue(s) → {root}\n")

    archive = []
    built   = 0

    for md_path in md_files:
        slug     = f"issue{re.search(r'\\d+', md_path.stem).group()}"
        out_html = root / f"{slug}.html"

        if args.changed and out_html.exists():
            if out_html.stat().st_mtime >= md_path.stat().st_mtime:
                print(f"  –  {slug}.html  (up to date, skipped)")
                # Still need metadata for archive even if we skip rebuilding
                post = frontmatter.load(str(md_path))
                meta = dict(post.metadata)
                date_str = str(meta.get("date", ""))
                try:
                    dt       = datetime.strptime(date_str, "%d %B %Y")
                    date_iso = dt.strftime("%Y-%m-%d")
                except ValueError:
                    date_iso = meta.get("date_iso", "2026-01-01")
                archive.append({
                    "num":        int(meta["issue"]),
                    "slug":       slug,
                    "title":      meta.get("title", ""),
                    "subtitle":   meta.get("theme_name", meta.get("title", "")),
                    "deck":       meta.get("deck", ""),
                    "date":       date_str,
                    "date_short": date_str,
                    "date_iso":   date_iso,
                })
                continue

        meta_entry = build_issue(md_path, env, root)
        archive.append(meta_entry)
        built += 1

    # Sort newest-first for homepage
    archive.sort(key=lambda x: x["num"], reverse=True)

    print()
    build_index(archive, env, root)

    print(f"\nDone. Built {built} issue(s), index updated.")
    print(f"Archive: {len(archive)} total issues.\n")


if __name__ == "__main__":
    main()
