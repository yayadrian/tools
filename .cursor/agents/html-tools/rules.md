# HTML/JS Tools Agent Rules

## Purpose
Author small, focused HTML/JavaScript utilities quickly and predictably. Keep dependencies minimal and DX (developer experience) sharp.

## HTML/JS Tool Rules

- Use **plain HTML**, **vanilla JavaScript**, and **minimal CSS** (no React or frameworks).
- **Indentation: two spaces**.
- Start CSS with:
  ```html
  <style>*{box-sizing:border-box}</style>
  ```
- Inputs and textareas use **16px font size**; prefer Helvetica (or system-UI fallbacks).
- JavaScript starts with:
  ```html
  <script type="module">
  ```
  The top-level inside that tag is **not indented**.
- Ship a **single index.html** unless a project genuinely needs more files.
- Keep any styling **tiny and inline** unless complexity demands a separate file.

## General Conventions

- **Small scope**, fast startup, minimal dependencies.
- **Two-space indentation** across all languages.
- Prefer **clarity over cleverness**; write short functions and obvious names.
- Provide a **concise README snippet or usage comment** at the top of each tool.
- Include **accessibility basics** (labels for inputs, sensible focus order).
- Default to **client-side only** for HTML tools; add a tiny server only if required.

## Code Style

- Use modern JavaScript (ES6+)
- Prefer `const` and `let` over `var`
- Use arrow functions where appropriate
- Keep functions small and focused
- Use descriptive variable and function names

## Accessibility

- Always include labels for inputs
- Maintain sensible focus order
- Use semantic HTML elements
- Ensure keyboard navigation works
- Provide ARIA labels where helpful

## File Structure

- Single `index.html` file is preferred
- If complexity demands, separate CSS/JS files are acceptable
- Keep file count minimal

## Example Task-Specific Briefs

- When making a page that emits a downloadable file (e.g. ICS), render a live preview and provide a download link. No React.

