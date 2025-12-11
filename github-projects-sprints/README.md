# GitHub Projects Sprint Creator

A CLI tool to create sprints (iterations) in GitHub Projects v2 from a CSV file.

## Usage

```bash
uv run create_sprints.py --csv <file> --project <project> --sprint-length <days> [--token <token>]
```

## Arguments

- `--csv, -c`: Path to CSV file with `Sprint Name` and `Sprint Start Date` columns (required)
- `--project, -p`: GitHub project identifier in format `owner/project-number` or project ID (required)
- `--sprint-length, -l`: Sprint length in days (default: 14)
- `--token, -t`: GitHub personal access token (optional, can also set `GITHUB_TOKEN` env var)

## CSV Format

The CSV file must have the following headers:
- `Sprint Name`: Name of the sprint
- `Sprint Start Date`: Start date in `YYYY-MM-DD` format

Example:
```csv
Sprint Name,Sprint Start Date
Sprint 1,2024-01-01
Sprint 2,2024-01-15
Sprint 3,2024-01-29
```

## Authentication

You need a GitHub Personal Access Token with the following scopes:
- `repo` (for repository access)
- `project` (for project access)

Set it via:
- Environment variable: `export GITHUB_TOKEN=your_token_here`
- CLI argument: `--token your_token_here`

## Project Setup

Before using this tool, ensure your GitHub Project v2 has an **Iteration field** configured. The tool will use the first iteration field it finds in the project.

## Example

```bash
# Using environment variable for token
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
uv run create_sprints.py --csv sprints.csv --project myorg/123 --sprint-length 14

# Using CLI argument for token
uv run create_sprints.py --csv sprints.csv --project myorg/123 --sprint-length 14 --token ghp_xxxxxxxxxxxxx
```

## Notes

- The tool will skip sprints that already exist (by name)
- Sprint end dates are calculated as `start_date + sprint_length - 1` days
- All dates should be in `YYYY-MM-DD` format





