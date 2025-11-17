# GitHub Copilot Instructions for Tools Repository

## Repository Purpose
A collection of single-use tools and utilities built for quick problem-solving. Each tool is small, focused, and self-contained, designed to solve specific problems quickly and efficiently.

## General Philosophy
- **Small scope, fast startup, minimal dependencies**
- **Clarity over cleverness** - short functions and obvious names
- **Self-contained utilities** that do one thing well
- **Accessible by default** with proper labels and focus order

## HTML/JS Tool Development

### Core Requirements
- Use **plain HTML**, **vanilla JavaScript**, and **minimal CSS** (no React or frameworks)
- Ship a single `index.html` file unless complexity genuinely demands more files
- Default to client-side only; add a tiny server only if absolutely required

### Code Style
- Indentation: **two spaces** for all languages
- JavaScript: Use `<script type="module">` with no indentation at top level
- CSS: Start with `<style>*{box-sizing:border-box}</style>`
- Inputs and textareas: 16px font size
- Font stack: Helvetica or system-UI fallbacks
- Keep styling tiny and inline unless complexity demands a separate file

### Example Structure
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tool Name</title>
  <style>*{box-sizing:border-box}</style>
  <style>
    /* minimal inline styles here */
  </style>
</head>
<body>
  <!-- HTML here -->
  <script type="module">
// JavaScript here (no indent at top level)
  </script>
</body>
</html>
```

## Python Tool Development

### Core Requirements
- Each Python tool is a single file script
- Must include a PEP-723 / uv header at the top
- Run with: `uv run path/to/script.py`
- Keep logic self-contained; avoid frameworks unless essential

### Script Header Format
```python
# /// script
# requires-python = ">=3.12"
# dependencies = []  # optional; list only what you need
# ///
```

## Accessibility Standards
- Include labels for all inputs
- Maintain sensible focus order
- Use semantic HTML elements
- Ensure keyboard navigation works properly

## Documentation Standards
- Provide concise documentation at the top of each tool
- Each tool directory should explain its purpose clearly
- Update the repository index when adding new tools
- Include usage examples in tool documentation

## Repository Structure
- Individual tool directories in repository root (each with `index.html` or Python script)
- `index.html` - Auto-generated listing of all available tools (updated by `update_index.py`)
- `RULES.md` - Development guidelines and conventions
- Tools are automatically discovered by scanning for directories

## Task-Specific Guidelines

### Creating a New Tool
1. Create a new directory in the repository root with a descriptive name (lowercase, hyphenated)
2. Follow the appropriate template (HTML/JS or Python) based on tool requirements
3. Include clear, concise documentation at the top of the file
4. Test for accessibility basics (labels, focus order)
5. Run `uv run update_index.py` to update the tools listing

### Making File Downloads
- When making a page that emits a downloadable file (e.g., ICS, GPX):
  - Render a live preview of the content
  - Provide a clear download link/button
  - No React or frameworks required

### Modifying Existing Tools
- Maintain existing code style and structure
- Preserve the single-file nature of tools unless complexity genuinely requires more
- Keep dependencies minimal
- Test all changes thoroughly before committing

## Security Practices
- Never commit secrets or API keys
- Validate all user inputs in tools that process data
- Use secure defaults for any network operations
- Keep dependencies minimal to reduce attack surface

## Testing Approach
- Test tools manually by opening in a web browser
- For Python scripts, test with `uv run path/to/script.py`
- Verify accessibility with keyboard navigation
- Test on different screen sizes for responsive tools

## Code Quality
- Prefer clarity over cleverness
- Write short, focused functions with obvious names
- Avoid deeply nested logic
- Comment only when necessary to explain "why", not "what"
- Two-space indentation across all languages
