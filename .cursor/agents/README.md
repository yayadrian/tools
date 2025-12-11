# Cursor Agents

This directory contains agent configurations for Cursor.

## Structure

Each agent should have its own subdirectory containing:
- `rules.md` - Agent-specific rules, guidelines, and constraints
- `plan.md` - Agent plans, workflows, and task definitions

## Usage

Agents can be referenced in Cursor to provide context-specific guidance and rules for different types of tasks or projects.

## Example Agent Structure

```
agents/
  ├── default/
  │   ├── rules.md      # Default rules for general development
  │   └── plan.md       # Default plans and workflows
  ├── python-tools/
  │   ├── rules.md      # Rules specific to Python tool development
  │   └── plan.md       # Plans for Python tool creation
  └── html-tools/
      ├── rules.md      # Rules specific to HTML/JS tool development
      └── plan.md       # Plans for HTML tool creation
```

