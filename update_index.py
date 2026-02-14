#!/usr/bin/env python3
"""Regenerate the repository tool index list in index.html."""

from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent
INDEX_PATH = REPO_ROOT / "index.html"
START_MARKER = "<!-- TOOLS-LIST START -->"
END_MARKER = "<!-- TOOLS-LIST END -->"
EXCLUDED_DIRS = {".git", ".github", "__pycache__", "node_modules"}


def generate_tools_html() -> str:
  tools = [
    directory.name
    for directory in REPO_ROOT.iterdir()
    if directory.is_dir()
    and not directory.name.startswith(".")
    and directory.name not in EXCLUDED_DIRS
  ]
  tools.sort()

  if not tools:
    return "<p>No tools found.</p>"

  items = "\n".join(f'  <li><a href="{tool}/">{tool}</a></li>' for tool in tools)
  return f"<ul>\n{items}\n</ul>"


def main() -> None:
  content = INDEX_PATH.read_text(encoding="utf-8")
  tools_html = generate_tools_html()
  pattern = re.compile(
    rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
    re.DOTALL,
  )
  replacement = f"{START_MARKER}\n{tools_html}\n{END_MARKER}"
  new_content = re.sub(pattern, replacement, content)

  if new_content != content:
    INDEX_PATH.write_text(new_content, encoding="utf-8")


if __name__ == "__main__":
  main()
