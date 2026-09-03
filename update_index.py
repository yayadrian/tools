#!/usr/bin/env python3
"""Regenerate the repository tool index list in index.html.

Tool directories are discovered automatically. Display metadata (icon, name,
description) comes from tools.json; directories missing from that file fall
back to a generic entry so nothing is ever left off the page.

Directories without an index.html are treated as command-line tools and link
to their source on GitHub instead of a page that would 404 on GitHub Pages.
"""

from html import escape
from pathlib import Path
import json
import re

REPO_ROOT = Path(__file__).resolve().parent
INDEX_PATH = REPO_ROOT / "index.html"
METADATA_PATH = REPO_ROOT / "tools.json"
START_MARKER = "<!-- TOOLS-LIST START -->"
END_MARKER = "<!-- TOOLS-LIST END -->"
EXCLUDED_DIRS = {".git", ".github", "__pycache__", "node_modules"}
SOURCE_URL = "https://github.com/yayadrian/tools/tree/main"
DEFAULT_ICON = "🧰"


def load_metadata() -> dict:
  if not METADATA_PATH.exists():
    return {}
  return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def discover_tools() -> list[Path]:
  tools = [
    directory
    for directory in REPO_ROOT.iterdir()
    if directory.is_dir()
    and not directory.name.startswith(".")
    and directory.name not in EXCLUDED_DIRS
  ]
  return sorted(tools, key=lambda directory: directory.name.lower())


def humanise(slug: str) -> str:
  return " ".join(part.capitalize() for part in re.split(r"[-_]+", slug))


def render_card(directory: Path, meta: dict) -> str:
  slug = directory.name
  icon = escape(meta.get("icon", DEFAULT_ICON))
  name = escape(meta.get("name", humanise(slug)))
  description = escape(meta.get("description", ""))
  is_web = (directory / "index.html").exists()
  href = f"{slug}/" if is_web else f"{SOURCE_URL}/{slug}"
  kind = "Web" if is_web else "CLI"

  lines = [
    "<li>",
    f'  <a class="tool" href="{href}">',
    f'    <span class="tool-icon" aria-hidden="true">{icon}</span>',
    '    <span class="tool-body">',
    f'      <span class="tool-name">{name} <span class="tool-kind">{kind}</span></span>',
  ]
  if description:
    lines.append(f'      <span class="tool-desc">{description}</span>')
  lines += [
    "    </span>",
    "  </a>",
    "</li>",
  ]
  return "\n".join(lines)


def generate_tools_html() -> str:
  metadata = load_metadata()
  tools = discover_tools()

  if not tools:
    return "<p>No tools found.</p>"

  cards = "\n".join(render_card(tool, metadata.get(tool.name, {})) for tool in tools)
  return f'<ul class="tools">\n{cards}\n</ul>'


def main() -> None:
  content = INDEX_PATH.read_text(encoding="utf-8")
  tools_html = generate_tools_html()

  pattern = re.compile(
    rf"(?m)^(?P<indent>[ \t]*){re.escape(START_MARKER)}.*?^[ \t]*{re.escape(END_MARKER)}",
    re.DOTALL,
  )

  def replace_block(match: re.Match) -> str:
    indent = match.group("indent")
    indented_html = "\n".join(
      f"{indent}{line}" if line else indent
      for line in tools_html.splitlines()
    )
    return f"{indent}{START_MARKER}\n{indented_html}\n{indent}{END_MARKER}"

  new_content, count = pattern.subn(replace_block, content)

  if count == 0:
    raise RuntimeError(
      "Tool list markers not found in index.html; no changes made"
    )
  if new_content != content:
    INDEX_PATH.write_text(new_content, encoding="utf-8")


if __name__ == "__main__":
  main()
