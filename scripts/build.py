from pathlib import Path
from markdown import markdown
from jinja2 import Environment, FileSystemLoader

ISSUES_DIR = Path("issues")
OUTPUT_DIR = Path("output")
TEMPLATES_DIR = Path("templates")

OUTPUT_DIR.mkdir(exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
template = env.get_template("article.html")

markdown_files = list(ISSUES_DIR.glob("*.md"))

if not markdown_files:
    raise Exception("No markdown files found in issues/")

latest_file = sorted(markdown_files)[-1]

content = latest_file.read_text(encoding="utf-8")
html_body = markdown(content)

rendered = template.render(
    title=latest_file.stem,
    content=html_body
)

output_file = OUTPUT_DIR / f"{latest_file.stem}.html"
output_file.write_text(rendered, encoding="utf-8")

print(f"Generated: {output_file}")
