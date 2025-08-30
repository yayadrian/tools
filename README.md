# Tools

A collection of single-use tools and utilities built for quick problem-solving.

This repository is inspired by [Simon Willison's tools](https://github.com/simonw/tools) - a collection of small, focused utilities designed to solve specific problems quickly and efficiently.

## Philosophy

Each tool in this repository follows a philosophy of:
- **Small scope, fast startup, minimal dependencies**
- **Clarity over cleverness** - short functions and obvious names
- **Self-contained utilities** that do one thing well
- **Accessible by default** with proper labels and focus order

## Available Tools

- [**nutri-calculator**](nutri-calculator/) - Calculate nutrition information for bread recipes, including calories, protein, and fiber per loaf and per slice

## Development Guidelines

All tools follow the conventions outlined in [RULES.md](RULES.md):

### HTML/JS Tools
- Plain HTML, vanilla JavaScript, minimal CSS (no frameworks)
- Two-space indentation
- Single `index.html` file unless complexity demands otherwise
- 16px font size for inputs, system font fallbacks

### Python Tools  
- Single-file scripts with PEP-723/uv headers
- Run with `uv run path/to/script.py`
- Self-contained logic, minimal frameworks

### General Principles
- Fast startup and minimal dependencies
- Client-side first for HTML tools
- Concise documentation at the top of each tool
- Accessibility basics included

## Repository Structure

The repository includes:
- Individual tool directories (each containing `index.html` and assets)
- `index.html` - Auto-generated listing of all available tools  
- `update_index.py` - Script to automatically update the tools listing
- `RULES.md` - Development guidelines and conventions

Tools are automatically discovered and listed by scanning for directories in the repository root.

## Usage

1. **Browse tools**: Visit the repository's [index page](index.html) to see all available tools
2. **Use a tool**: Click on any tool name to open it
3. **Run locally**: Clone the repository and open `index.html` in a web browser
4. **Add a tool**: Create a new directory with an `index.html` file following the guidelines in `RULES.md`

## License

MIT License - see [LICENSE](LICENSE) for details.