# /// script
# requires-python = ">=3.12"
# ///
"""
Convert JSON location tracks to GPX files.

Usage:
  uv run workflow_to_gpx.py [src] [dest]

src  folder with JSON files, searched recursively, or a single JSON file (default: current directory)
dest folder for GPX output (default: same as src)

Notes:
- Emits GPX 1.1 with per-point <time> elements when timestamps are present in the
  source. Accepts timestamps in seconds, milliseconds, or ISO8601 strings under
  common keys (time, timestamp, timestampMs, ts, date, datetime, created_at, ...).
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from typing import Any, Dict, List
import unicodedata

LatLon = Dict[str, Any]
Track = List[LatLon]

def has_lat_lon(point: Dict[str, Any]) -> bool:
  lat_keys = {"lat", "latitude"}
  lon_keys = {"lon", "lng", "longitude"}
  return any(k in point for k in lat_keys) and any(k in point for k in lon_keys)

def find_tracks(obj: Any) -> List[Track]:
  tracks: List[Track] = []
  if isinstance(obj, list):
    if obj and all(isinstance(p, dict) and has_lat_lon(p) for p in obj):
      tracks.append(obj)
    else:
      for item in obj:
        tracks.extend(find_tracks(item))
  elif isinstance(obj, dict):
    for value in obj.values():
      tracks.extend(find_tracks(value))
  return tracks

def parse_time(point: Dict[str, Any]) -> datetime | None:
  """Best-effort parse of a timestamp from a track point.

  Supports keys like time, timestamp, timestampMs, ts, date, datetime, created_at.
  Accepts seconds or milliseconds (auto-detected), and ISO8601 or common
  "YYYY-mm-dd HH:MM:SS [±HHMM]" formats. Returns an aware UTC datetime.
  """
  # Common key candidates in many exports (Shortcuts, iCloud, etc.)
  candidates = (
    "time",
    "timestamp",
    "timestampMs",
    "timestamp_ms",
    "ts",
    "date",
    "datetime",
    "created_at",
    "createdAt",
    "recorded_at",
    "recordedAt",
  )

  t: Any = None
  for k in candidates:
    if k in point and point[k] is not None:
      t = point[k]
      break
  if t is None:
    return None

  # Numeric timestamps: seconds vs milliseconds
  if isinstance(t, (int, float)):
    val = float(t)
    # Heuristic: > 1e12 means milliseconds epoch
    if val > 1e12:
      val /= 1000.0
    return datetime.fromtimestamp(val, tz=timezone.utc)

  if isinstance(t, str):
    # Normalize unicode (handles fancy spaces and characters like narrow no-break space)
    s = unicodedata.normalize("NFKC", t).strip()
    # Collapse whitespace sequences to a single ASCII space
    s = re.sub(r"\s+", " ", s)
    # Normalize lowercase am/pm to uppercase for strptime compatibility
    s = re.sub(r"\b(am|pm)\b", lambda m: m.group(1).upper(), s, flags=re.IGNORECASE)
    # If it's an integer/float string, parse numerically
    if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", s):
      try:
        val = float(s)
        if val > 1e12:
          val /= 1000.0
        return datetime.fromtimestamp(val, tz=timezone.utc)
      except Exception:  # noqa: BLE001
        pass
    # Normalize common Zulu suffix
    s_iso = s.replace("Z", "+00:00")
    # Try python's ISO8601 first (handles offsets like +00:00)
    try:
      dt = datetime.fromisoformat(s_iso)
      # If naive, assume UTC
      if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
      return dt.astimezone(timezone.utc)
    except ValueError:
      pass
    # Try a range of explicit formats including 12-hour clock with AM/PM
    explicit_formats = (
      "%Y-%m-%d %H:%M:%S%z",
      "%Y-%m-%d %H:%M:%S",
      "%Y/%m/%d %H:%M:%S%z",
      "%Y/%m/%d %H:%M:%S",
      "%Y-%m-%d %I:%M:%S %p %z",
      "%Y-%m-%d %I:%M:%S %p",
      "%Y/%m/%d %I:%M:%S %p %z",
      "%Y/%m/%d %I:%M:%S %p",
      "%Y-%m-%d %I:%M %p %z",
      "%Y-%m-%d %I:%M %p",
      "%Y/%m/%d %I:%M %p %z",
      "%Y/%m/%d %I:%M %p",
    )
    for fmt in explicit_formats:
      try:
        dt = datetime.strptime(s, fmt)
        if dt.tzinfo is None:
          dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
      except ValueError:
        continue
    return None

  return None

def track_to_gpx(track: Track) -> ET.ElementTree:
  """Render a GPX 1.1 document with per-point timestamps when available."""
  NS = "http://www.topografix.com/GPX/1/1"
  ET.register_namespace("", NS)

  def q(tag: str) -> str:
    return f"{{{NS}}}{tag}"

  root = ET.Element(q("gpx"), version="1.1", creator="workflow-to-gpx")
  trk = ET.SubElement(root, q("trk"))
  seg = ET.SubElement(trk, q("trkseg"))
  for pt in track:
    lat = float(pt.get("lat") or pt.get("latitude"))
    lon = float(pt.get("lon") or pt.get("lng") or pt.get("longitude"))
    trkpt = ET.SubElement(seg, q("trkpt"), lat=f"{lat}", lon=f"{lon}")
    # Elevation if present
    ele_val = pt.get("ele") or pt.get("elevation") or pt.get("alt") or pt.get("altitude")
    if ele_val is not None:
      try:
        ET.SubElement(trkpt, q("ele")).text = f"{float(ele_val)}"
      except Exception:  # noqa: BLE001 - ignore bad elevation
        pass
    # Timestamp
    t = parse_time(pt)
    if t:
      # Use second precision per common GPX consumers
      t_utc = t.astimezone(timezone.utc).replace(microsecond=0)
      ET.SubElement(trkpt, q("time")).text = t_utc.isoformat().replace("+00:00", "Z")
  return ET.ElementTree(root)

def format_start_time(track: Track) -> tuple[str, str]:
  first_time = None
  for pt in track:
    first_time = parse_time(pt)
    if first_time:
      break
  if first_time:
    date = first_time.strftime("%Y%m%d")
    time = first_time.strftime("%H%M%S")
  else:
    now = datetime.now(timezone.utc)
    date = now.strftime("%Y%m%d")
    time = "000000"
  return date, time

def _slug(s: str) -> str:
  # Keep letters, numbers, dash and underscore; replace others with '-'
  s = re.sub(r"[\s/\\]+", "-", s.strip())
  s = re.sub(r"[^A-Za-z0-9._-]", "-", s)
  s = re.sub(r"-+", "-", s)
  return s.strip("-_")

def process_file(path: str, dest: str, rel_hint: str | None = None) -> int:
  try:
    with open(path, "r", encoding="utf-8") as f:
      data = json.load(f)
  except Exception as e:  # noqa: BLE001 - best-effort batch conversion
    print(f"Skipping {path}: {e}")
    return 0

  tracks = find_tracks(data)
  written = 0

  # Build a safe prefix from either relpath or filename stem
  if rel_hint:
    prefix_base = os.path.splitext(rel_hint)[0]
  else:
    prefix_base = os.path.splitext(os.path.basename(path))[0]
  prefix = _slug(prefix_base)

  for idx, track in enumerate(tracks, start=1):
    tree = track_to_gpx(track)
    date, time = format_start_time(track)
    filename = f"{prefix}_{date}_{time}_track{idx:02d}.gpx" if prefix else f"{date}_{time}_track{idx:02d}.gpx"
    out_path = os.path.join(dest, filename)
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    written += 1
  return written

def main() -> None:
  parser = argparse.ArgumentParser(description="Convert JSON location tracks to GPX files.")
  parser.add_argument("src", nargs="?", default=".", help="Folder with json files")
  parser.add_argument("dest", nargs="?", default=None, help="Folder for gpx output (default: src)")
  args = parser.parse_args()

  src = os.path.abspath(args.src)
  dest = os.path.abspath(args.dest or args.src)
  os.makedirs(dest, exist_ok=True)

  total_tracks = 0
  total_files = 0

  if os.path.isfile(src):
    if src.lower().endswith(".json"):
      total_tracks += process_file(src, dest)
      total_files = 1
    else:
      print(f"Source is a file but not JSON: {src}")
  else:
    # Walk recursively and process all .json files
    for root, _dirs, files in os.walk(src):
      for name in files:
        if name.lower().endswith(".json"):
          file_path = os.path.join(root, name)
          rel = os.path.relpath(file_path, src)
          total_tracks += process_file(file_path, dest, rel_hint=rel)
          total_files += 1

  print(f"Processed {total_files} file(s); written {total_tracks} track(s) to {dest}")

if __name__ == "__main__":
  main()
