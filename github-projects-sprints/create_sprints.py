# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///
"""
Create sprints in GitHub Projects v2 from a CSV file.

Usage:
  uv run create_sprints.py --csv <file> --project <project> --sprint-length <days> [--token <token>]

Arguments:
  --csv, -c          Path to CSV file with Sprint Name and Sprint Start Date columns
  --project, -p      GitHub project identifier (owner/project-number or project ID)
  --sprint-length, -l  Sprint length in days (default: 14)
  --token, -t        GitHub personal access token (or set GITHUB_TOKEN env var)

CSV Format:
  The CSV file must have headers: "Sprint Name" and "Sprint Start Date"
  Date format: YYYY-MM-DD

Example:
  uv run create_sprints.py --csv sprints.csv --project myorg/123 --sprint-length 14
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime, timedelta
from typing import Any

import httpx

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


def parse_csv(file_path: str) -> list[dict[str, str]]:
  """Parse CSV file and return list of sprint records."""
  sprints = []
  try:
    with open(file_path, "r", encoding="utf-8") as f:
      reader = csv.DictReader(f)
      required_headers = {"Sprint Name", "Sprint Start Date"}
      if not required_headers.issubset(reader.fieldnames or []):
        missing = required_headers - (reader.fieldnames or set())
        raise ValueError(f"CSV missing required headers: {', '.join(missing)}")
      
      for row_num, row in enumerate(reader, start=2):
        sprint_name = row["Sprint Name"].strip()
        start_date_str = row["Sprint Start Date"].strip()
        
        if not sprint_name:
          print(f"Warning: Row {row_num} has empty Sprint Name, skipping", file=sys.stderr)
          continue
        
        try:
          start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError as e:
          raise ValueError(f"Row {row_num}: Invalid date format '{start_date_str}'. Use YYYY-MM-DD") from e
        
        sprints.append({"name": sprint_name, "start_date": start_date})
  except FileNotFoundError:
    raise FileNotFoundError(f"CSV file not found: {file_path}") from None
  except Exception as e:
    raise ValueError(f"Error parsing CSV: {e}") from e
  
  return sprints


def get_project_info(client: httpx.Client, token: str, project_identifier: str) -> dict[str, str]:
  """Get project ID and iteration field ID from GitHub."""
  # Try to parse as owner/number format
  if "/" in project_identifier:
    owner, number = project_identifier.split("/", 1)
    try:
      project_number = int(number)
    except ValueError:
      raise ValueError(f"Invalid project number: {number}")
    
    query = """
    query GetProject($owner: String!, $number: Int!) {
      organization(login: $owner) {
        projectV2(number: $number) {
          id
          fields(first: 20) {
            nodes {
              ... on ProjectV2IterationField {
                id
                name
              }
            }
          }
        }
      }
    }
    """
    variables = {"owner": owner, "number": project_number}
  else:
    # Assume it's a project ID
    query = """
    query GetProject($id: ID!) {
      node(id: $id) {
        ... on ProjectV2 {
          id
          fields(first: 20) {
            nodes {
              ... on ProjectV2IterationField {
                id
                name
              }
            }
          }
        }
      }
    }
    """
    variables = {"id": project_identifier}
  
  response = client.post(
    GITHUB_GRAPHQL_URL,
    headers={"Authorization": f"Bearer {token}"},
    json={"query": query, "variables": variables},
    timeout=30.0,
  )
  response.raise_for_status()
  data = response.json()
  
  if "errors" in data:
    raise ValueError(f"GraphQL errors: {data['errors']}")
  
  if "/" in project_identifier:
    project = data.get("data", {}).get("organization", {}).get("projectV2")
  else:
    project = data.get("data", {}).get("node")
  
  if not project:
    raise ValueError(f"Project not found: {project_identifier}")
  
  project_id = project["id"]
  iteration_fields = [f for f in project.get("fields", {}).get("nodes", []) if f]
  
  if not iteration_fields:
    raise ValueError("No iteration field found in project. Please create an iteration field first.")
  
  # Use the first iteration field found
  iteration_field_id = iteration_fields[0]["id"]
  iteration_field_name = iteration_fields[0].get("name", "Iteration")
  
  return {
    "project_id": project_id,
    "iteration_field_id": iteration_field_id,
    "iteration_field_name": iteration_field_name,
  }


def get_existing_iterations(client: httpx.Client, token: str, project_id: str, iteration_field_id: str) -> list[str]:
  """Get list of existing iteration names to avoid duplicates."""
  query = """
  query GetIterations($projectId: ID!, $fieldId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        field(id: $fieldId) {
          ... on ProjectV2IterationField {
            configuration {
              iterations {
                id
                title
              }
            }
          }
        }
      }
    }
  }
  """
  
  response = client.post(
    GITHUB_GRAPHQL_URL,
    headers={"Authorization": f"Bearer {token}"},
    json={"query": query, "variables": {"projectId": project_id, "fieldId": iteration_field_id}},
    timeout=30.0,
  )
  response.raise_for_status()
  data = response.json()
  
  if "errors" in data:
    return []
  
  field = data.get("data", {}).get("node", {}).get("field", {})
  config = field.get("configuration", {})
  iterations = config.get("iterations", [])
  
  return [iter["title"] for iter in iterations]


def create_iteration(
  client: httpx.Client,
  token: str,
  project_id: str,
  iteration_field_id: str,
  name: str,
  start_date: str,
  duration: int,
) -> dict[str, Any]:
  """Create a new iteration in the project, preserving existing ones."""
  # Get full iteration data to preserve existing ones
  query = """
  query GetIterations($projectId: ID!, $fieldId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        field(id: $fieldId) {
          ... on ProjectV2IterationField {
            configuration {
              iterations {
                id
                title
                startDate
                duration
              }
            }
          }
        }
      }
    }
  }
  """
  
  response = client.post(
    GITHUB_GRAPHQL_URL,
    headers={"Authorization": f"Bearer {token}"},
    json={"query": query, "variables": {"projectId": project_id, "fieldId": iteration_field_id}},
    timeout=30.0,
  )
  response.raise_for_status()
  data = response.json()
  
  if "errors" in data:
    raise ValueError(f"Failed to fetch existing iterations: {data['errors']}")
  
  field = data.get("data", {}).get("node", {}).get("field", {})
  config = field.get("configuration", {})
  existing_iters = config.get("iterations", [])
  
  # Build iteration inputs preserving existing ones
  iteration_inputs = []
  for iter in existing_iters:
    iteration_inputs.append({
      "id": iter["id"],
      "title": iter["title"],
      "startDate": iter.get("startDate", ""),
      "duration": iter.get("duration", 0),
    })
  
  # Add the new iteration (without id for new iterations)
  iteration_inputs.append({
    "title": name,
    "startDate": start_date,
    "duration": duration,
  })
  
  # Update the field with all iterations
  mutation = """
  mutation UpdateIterationField($projectId: ID!, $fieldId: ID!, $iterations: [ProjectV2IterationInput!]!) {
    updateProjectV2Field(input: {
      projectId: $projectId
      fieldId: $fieldId
      iterationSettings: {
        iterations: $iterations
      }
    }) {
      projectV2Field {
        id
      }
    }
  }
  """
  
  response = client.post(
    GITHUB_GRAPHQL_URL,
    headers={"Authorization": f"Bearer {token}"},
    json={
      "query": mutation,
      "variables": {
        "projectId": project_id,
        "fieldId": iteration_field_id,
        "iterations": iteration_inputs,
      },
    },
    timeout=30.0,
  )
  response.raise_for_status()
  data = response.json()
  
  if "errors" in data:
    raise ValueError(f"Failed to create iteration '{name}': {data['errors']}")
  
  return data


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Create sprints in GitHub Projects v2 from a CSV file",
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  parser.add_argument(
    "--csv",
    "-c",
    required=True,
    help="Path to CSV file with Sprint Name and Sprint Start Date columns",
  )
  parser.add_argument(
    "--project",
    "-p",
    required=True,
    help="GitHub project identifier (owner/project-number or project ID)",
  )
  parser.add_argument(
    "--sprint-length",
    "-l",
    type=int,
    default=14,
    help="Sprint length in days (default: 14)",
  )
  parser.add_argument(
    "--token",
    "-t",
    help="GitHub personal access token (or set GITHUB_TOKEN env var)",
  )
  
  args = parser.parse_args()
  
  # Get authentication token
  token = args.token or os.getenv("GITHUB_TOKEN")
  if not token:
    print("Error: GitHub token required. Set GITHUB_TOKEN env var or use --token", file=sys.stderr)
    sys.exit(1)
  
  if args.sprint_length < 1:
    print("Error: Sprint length must be at least 1 day", file=sys.stderr)
    sys.exit(1)
  
  # Parse CSV
  try:
    sprints = parse_csv(args.csv)
  except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
  
  if not sprints:
    print("No sprints found in CSV file", file=sys.stderr)
    sys.exit(1)
  
  # Connect to GitHub
  with httpx.Client() as client:
    try:
      # Get project info
      print(f"Fetching project information for {args.project}...")
      project_info = get_project_info(client, token, args.project)
      project_id = project_info["project_id"]
      iteration_field_id = project_info["iteration_field_id"]
      iteration_field_name = project_info["iteration_field_name"]
      
      print(f"Found project: {project_id}")
      print(f"Using iteration field: {iteration_field_name} ({iteration_field_id})")
      print()
      
      # Get existing iterations to check for duplicates
      existing = get_existing_iterations(client, token, project_id, iteration_field_id)
      existing_set = set(existing)
      
      # Create sprints
      created = 0
      skipped = 0
      
      for sprint in sprints:
        name = sprint["name"]
        start_date = sprint["start_date"]
        
        if name in existing_set:
          print(f"⏭️  Skipping '{name}' (already exists)")
          skipped += 1
          continue
        
        try:
          print(f"Creating sprint '{name}' ({start_date} to {start_date + timedelta(days=args.sprint_length - 1)})...")
          create_iteration(
            client,
            token,
            project_id,
            iteration_field_id,
            name,
            start_date.strftime("%Y-%m-%d"),
            args.sprint_length,
          )
          print(f"✅ Created sprint '{name}'")
          created += 1
          # Add to existing set to avoid duplicates in the same run
          existing_set.add(name)
        except Exception as e:
          print(f"❌ Failed to create sprint '{name}': {e}", file=sys.stderr)
      
      print()
      print(f"Summary: {created} created, {skipped} skipped")
      
    except Exception as e:
      print(f"Error: {e}", file=sys.stderr)
      sys.exit(1)


if __name__ == "__main__":
  main()

