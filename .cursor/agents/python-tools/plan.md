# Python Tools Agent Plan

## Overview
Plans and workflows for creating and maintaining Python tools in this repository.

## Creating a New Python Tool

### Step 1: Setup
1. Create a new directory for the tool (if needed)
2. Create a single Python script file
3. Add PEP-723 header with Python version and dependencies

### Step 2: Implementation
1. Start with a usage comment or docstring at the top
2. Implement core functionality in a single file
3. Use type hints for clarity
4. Keep functions small and focused
5. Use two-space indentation

### Step 3: Testing
1. Test with `uv run path/to/script.py`
2. Verify it works as expected
3. Check error handling

### Step 4: Documentation
1. Add a README.md if the tool needs explanation
2. Include usage examples
3. Document any required environment variables or setup

## Updating Existing Python Tools

1. Review current implementation
2. Identify changes needed
3. Maintain single-file structure
4. Update dependencies in PEP-723 header if needed
5. Test with `uv run`
6. Update documentation if behavior changes

## Common Patterns

### CLI Tools
- Use `argparse` or similar for command-line arguments
- Provide clear help text
- Handle missing arguments gracefully

### File Processing
- Use pathlib for path handling
- Handle file not found errors
- Provide clear error messages

### API Interactions
- Use `requests` or `httpx` if needed
- Handle network errors
- Include authentication handling

