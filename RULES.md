# Tools Rules

## Purpose
Author small, focused utilities quickly and predictably. Keep dependencies minimal and DX (developer experience) sharp.

## HTML/JS Tool Rules
- Use **plain HTML**, **vanilla JavaScript**, and **minimal CSS** (no React or frameworks).
- Indentation: **two spaces**.
- Start CSS with:
  ```html
  <style>*{box-sizing:border-box}</style>
  ```
- Inputs and textareas use 16px font size; prefer Helvetica (or system-UI fallbacks).
- JavaScript starts with:
  ```html
  <script type="module">
  ```
  The top-level inside that tag is not indented.
- Ship a single index.html unless a project genuinely needs more files.
- Keep any styling tiny and inline unless complexity demands a separate file.

## Python One-Shot Tool Rules
- Each Python tool is a single file script that starts with a PEP-723 / uv header, e.g.:
  ```
  # /// script
  # requires-python = ">=3.12"
  # dependencies = ["..."]  # optional; list only what you need
  # ///
  ```
- Must run with:
  ```
  uv run path/to/script.py
  ```
- Keep logic self-contained; avoid frameworks unless essential.

## General Conventions
- Small scope, fast startup, minimal dependencies.
- Two-space indentation across all languages.
- Prefer clarity over cleverness; write short functions and obvious names.
- Provide a concise README snippet or usage comment at the top of each tool.
- Include accessibility basics (labels for inputs, sensible focus order).
- Default to client-side only for HTML tools; add a tiny server only if required.

## Example Task-Specific Briefs
- When making a page that emits a downloadable file (e.g. ICS), render a live preview and provide a download link. No React.

## How This File Is Used
- At the start of any new tool request in this repo, the assistant will:
  1. Read RULES.md.
  2. Confirm adherence.
  3. Apply the rules to the new tool.

