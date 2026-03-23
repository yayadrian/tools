#!/usr/bin/env python3
"""Regenerate the repository tool index list in index.html."""

from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent
INDEX_PATH = REPO_ROOT / "index.html"
EXCLUDED_DIRS = {".git", ".github", "__pycache__", "node_modules"}

MARKERS = {
  "web": ("<!-- WEB-TOOLS-LIST START -->", "<!-- WEB-TOOLS-LIST END -->"),
  "python": ("<!-- PYTHON-TOOLS-LIST START -->", "<!-- PYTHON-TOOLS-LIST END -->"),
}


def classify_tools() -> tuple[list[str], list[str]]:
  web_tools = []
  python_tools = []
  for directory in REPO_ROOT.iterdir():
    if not directory.is_dir():
      continue
    if directory.name.startswith(".") or directory.name in EXCLUDED_DIRS:
      continue
    if (directory / "index.html").exists():
      web_tools.append(directory.name)
    else:
      python_tools.append(directory.name)
  web_tools.sort()
  python_tools.sort()
  return web_tools, python_tools


def build_list_html(tools: list[str], link: bool = True) -> str:
  if not tools:
    return "<p>No tools found.</p>"
  if link:
    items = "\n".join(
      f'  <li><a href="{tool}/">{tool}</a></li>' for tool in tools
    )
  else:
    items = "\n".join(f"  <li>{tool}</li>" for tool in tools)
  return f"<ul>\n{items}\n</ul>"


def replace_marker_block(content: str, start: str, end: str, html: str) -> tuple[str, int]:
  pattern = re.compile(
    rf"(?m)^(?P<indent>[ \t]*){re.escape(start)}.*?^[ \t]*{re.escape(end)}",
    re.DOTALL,
  )

  def replace_block(match: re.Match) -> str:
    indent = match.group("indent")
    indented_html = "\n".join(
      f"{indent}{line}" if line else indent
      for line in html.splitlines()
    )
    return f"{indent}{start}\n{indented_html}\n{indent}{end}"

  return pattern.subn(replace_block, content)


def main() -> None:
  content = INDEX_PATH.read_text(encoding="utf-8")
  web_tools, python_tools = classify_tools()

  web_html = build_list_html(web_tools, link=True)
  python_html = build_list_html(python_tools, link=False)

  web_start, web_end = MARKERS["web"]
  py_start, py_end = MARKERS["python"]

  content, web_count = replace_marker_block(content, web_start, web_end, web_html)
  content, py_count = replace_marker_block(content, py_start, py_end, python_html)

  if web_count == 0 or py_count == 0:
    raise RuntimeError(
      "One or more tool list markers not found in index.html; no changes made"
    )

  INDEX_PATH.write_text(content, encoding="utf-8")


if __name__ == "__main__":
  main()
