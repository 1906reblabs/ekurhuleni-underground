from pathlib import Path
from markdown import markdown
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import re

# ---------------------------------------------------
# PATHS
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

ISSUES_DIR = BASE_DIR / "issues"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "docs"

OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------
# JINJA ENVIRONMENT
# ---------------------------------------------------

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR)
)

issue_template = env.get_template("issue_template.html.j2")
index_template = env.get_template("index_template.html.j2")

# ---------------------------------------------------
# FIND MARKDOWN FILES
# ---------------------------------------------------

markdown_files = sorted(
    ISSUES_DIR.glob("*.md"),
    reverse=True
)

if not markdown_files:
    raise Exception("No markdown files found in issues/")

generated_articles = []

# ---------------------------------------------------
# BUILD EACH ISSUE
# ---------------------------------------------------

for md_file in markdown_files:

    raw_markdown = md_file.read_text(encoding="utf-8")

    # Extract title from first heading
    title_match = re.search(r"^#\\s+(.+)", raw_markdown, re.MULTILINE)

    if title_match:
        title = title_match.group(1).strip()
    else:
        title = md_file.stem

    html_content = markdown(
        raw_markdown,
        extensions=["extra", "tables", "fenced_code"]
    )

    slug = md_file.stem

    rendered_issue = issue_template.render(
        title=title,
        content=html_content,
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        slug=slug
    )

    issue_output_path = OUTPUT_DIR / f"{slug}.html"

    issue_output_path.write_text(
        rendered_issue,
        encoding="utf-8"
    )

    generated_articles.append({
        "title": title,
        "slug": slug,
        "filename": f"{slug}.html"
    })

    print(f"Generated issue page: {issue_output_path}")

# ---------------------------------------------------
# BUILD INDEX PAGE
# ---------------------------------------------------

rendered_index = index_template.render(
    articles=generated_articles,
    generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
)

index_output_path = OUTPUT_DIR / "index.html"

index_output_path.write_text(
    rendered_index,
    encoding="utf-8"
)

print(f"Generated index page: {index_output_path}")

print("Build completed successfully.")
