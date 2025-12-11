# Python Tools Agent Rules

## Purpose
Author small, focused Python utilities quickly and predictably. Keep dependencies minimal and DX (developer experience) sharp.

## Python One-Shot Tool Rules

- Each Python tool is a **single file script** that starts with a PEP-723 / uv header, e.g.:
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
- Keep logic **self-contained**; avoid frameworks unless essential.

## General Conventions

- **Small scope**, fast startup, minimal dependencies.
- **Two-space indentation** across all languages.
- Prefer **clarity over cleverness**; write short functions and obvious names.
- Provide a **concise README snippet or usage comment** at the top of each tool.
- Default to **client-side only** for tools; add a tiny server only if required.

## Code Style

- Use type hints where helpful
- Keep functions focused and single-purpose
- Use descriptive variable names
- Include docstrings for public functions
- Handle errors gracefully with clear messages

## Dependencies

- Minimize dependencies - only include what's absolutely necessary
- Prefer standard library when possible
- Use `uv` for dependency management via PEP-723 headers

