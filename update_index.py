#!/usr/bin/env python3
import os
import re

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(REPO_ROOT, "index.html")
START_MARKER = "<!-- TOOLS-LIST START -->"
END_MARKER = "<!-- TOOLS-LIST END -->"
EXCLUDED_DIRS = {'.git', '.github', '__pycache__', 'node_modules'}

def generate_tools_html():
    tools = [d for d in os.listdir(REPO_ROOT)
             if os.path.isdir(os.path.join(REPO_ROOT, d))
             and not d.startswith('.')
             and d not in EXCLUDED_DIRS]
    tools.sort()
    items = "\n".join(f'  <li><a href="{t}/">{t}</a></li>' for t in tools)
    return f"<ul>\n{items}\n</ul>" if items else "<p>No tools found.</p>"

def main():
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    tools_html = generate_tools_html()
    pattern = re.compile(f"{START_MARKER}.*?{END_MARKER}", re.DOTALL)
    replacement = f"{START_MARKER}\n{tools_html}\n{END_MARKER}"
    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        with open(INDEX_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)

if __name__ == "__main__":
    main()
