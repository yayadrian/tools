# /// script
# requires-python = ">=3.12"
# dependencies = ["requests"]
# ///

"""
Jellyfin Watched Cleaner

Deletes watched videos from a Jellyfin library via the API.
Dry-run by default — pass --confirm to actually delete.

Setup:
    1. Copy config.toml.example to config.toml
    2. Fill in your Jellyfin server URL, API key, user ID, and library name

Usage:
    # Preview what would be deleted (dry-run)
    uv run jellyfin_watched_cleaner.py

    # Actually delete watched videos
    uv run jellyfin_watched_cleaner.py --confirm
"""

import argparse
import sys
import tomllib
from pathlib import Path

import requests

CONFIG_PATH = Path(__file__).resolve().parent / "config.toml"


def load_config():
  """Load and validate config from config.toml."""
  if not CONFIG_PATH.exists():
    print(f"Error: config file not found at {CONFIG_PATH}", file=sys.stderr)
    print("Copy config.toml.example to config.toml and fill in your details.", file=sys.stderr)
    sys.exit(1)

  with open(CONFIG_PATH, "rb") as f:
    config = tomllib.load(f)

  jellyfin = config.get("jellyfin", {})
  required = ["server_url", "api_key", "user_id", "library_name"]
  missing = [k for k in required if not jellyfin.get(k)]
  if missing:
    print(f"Error: missing config keys: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

  # Strip trailing slash from server URL
  jellyfin["server_url"] = jellyfin["server_url"].rstrip("/")
  # Normalise exclude list to lowercase for case-insensitive matching
  jellyfin["exclude"] = [
    name.lower() for name in jellyfin.get("exclude", [])
  ]
  return jellyfin


def api_get(config, endpoint, params=None):
  """Make an authenticated GET request to the Jellyfin API."""
  url = f"{config['server_url']}{endpoint}"
  headers = {"Authorization": f"MediaBrowser Token=\"{config['api_key']}\""}
  resp = requests.get(url, headers=headers, params=params, timeout=30)
  resp.raise_for_status()
  return resp.json()


def api_delete(config, endpoint):
  """Make an authenticated DELETE request to the Jellyfin API."""
  url = f"{config['server_url']}{endpoint}"
  headers = {"Authorization": f"MediaBrowser Token=\"{config['api_key']}\""}
  resp = requests.delete(url, headers=headers, timeout=30)
  resp.raise_for_status()


def find_library(config):
  """Find the library ID by name."""
  data = api_get(config, f"/Users/{config['user_id']}/Views")
  for item in data.get("Items", []):
    if item["Name"].lower() == config["library_name"].lower():
      return item["Id"]
  available = [item["Name"] for item in data.get("Items", [])]
  print(f"Error: library '{config['library_name']}' not found.", file=sys.stderr)
  print(f"Available libraries: {', '.join(available)}", file=sys.stderr)
  sys.exit(1)


def get_watched_items(config, library_id):
  """Fetch all watched video items from the library."""
  params = {
    "ParentId": library_id,
    "Recursive": "true",
    "IsPlayed": "true",
    "IncludeItemTypes": "Movie,Episode",
    "Fields": "Path",
    "StartIndex": 0,
    "Limit": 500,
  }
  all_items = []
  while True:
    data = api_get(config, f"/Users/{config['user_id']}/Items", params)
    items = data.get("Items", [])
    all_items.extend(items)
    if not items or len(all_items) >= data.get("TotalRecordCount", 0):
      break
    params["StartIndex"] += len(items)
  return all_items


def main():
  parser = argparse.ArgumentParser(
    description="Delete watched videos from a Jellyfin library",
  )
  parser.add_argument(
    "--confirm",
    action="store_true",
    help="Actually delete items. Without this flag, runs in dry-run mode.",
  )
  args = parser.parse_args()

  config = load_config()

  print(f"Connecting to {config['server_url']}...")
  library_id = find_library(config)
  print(f"Found library: {config['library_name']} ({library_id})")

  print("Fetching watched items...")
  items = get_watched_items(config, library_id)

  # Filter out excluded shows/movies
  exclude = config.get("exclude", [])
  if exclude:
    before = len(items)
    items = [
      item for item in items
      if item.get("SeriesName", item.get("Name", "")).lower() not in exclude
    ]
    skipped = before - len(items)
    if skipped:
      print(f"Excluded {skipped} item(s) matching exclude list.")

  if not items:
    print("No watched items found. Nothing to do.")
    return

  print(f"\n{'=' * 60}")
  print(f"Found {len(items)} watched item(s):")
  print(f"{'=' * 60}")
  for item in items:
    name = item.get("Name", "Unknown")
    series = item.get("SeriesName")
    path = item.get("Path", "N/A")
    if series:
      episode = item.get("IndexNumber")
      season = item.get("ParentIndexNumber")
      if isinstance(season, int) and isinstance(episode, int):
        se_str = f"S{season:02d}E{episode:02d}"
      else:
        se_str = "S??E??"
      print(f"  {series} - {se_str} - {name}")
    else:
      print(f"  {name}")
    print(f"    Path: {path}")
  print(f"{'=' * 60}\n")

  if not args.confirm:
    print("DRY RUN — no files were deleted.")
    print("Run again with --confirm to delete these items.")
    return

  print("Deleting watched items...")
  deleted = 0
  errors = 0
  for item in items:
    name = item.get("Name", "Unknown")
    item_id = item["Id"]
    try:
      api_delete(config, f"/Items/{item_id}")
      print(f"  Deleted: {name}")
      deleted += 1
    except requests.HTTPError as e:
      print(f"  Failed to delete {name}: {e}", file=sys.stderr)
      errors += 1

  print(f"\nDone. Deleted {deleted} item(s), {errors} error(s).")


if __name__ == "__main__":
  main()
