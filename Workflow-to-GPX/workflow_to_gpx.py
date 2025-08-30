# /// script
# requires-python = ">=3.12"
# ///
"""
Convert JSON location tracks to GPX files.

Usage:
  uv run workflow_to_gpx.py [src] [dest]

src  folder with json files (default: current directory)
dest folder for GPX output (default: same as src)
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from typing import Any, Dict, List

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
  t = point.get("time") or point.get("timestamp")
  if t is None:
    return None
  if isinstance(t, (int, float)):
    return datetime.fromtimestamp(t, tz=timezone.utc)
  if isinstance(t, str):
    try:
      return datetime.fromisoformat(t.replace("Z", "+00:00"))
    except ValueError:
      return None
  return None

def track_to_gpx(track: Track) -> ET.ElementTree:
  ET.register_namespace("", "http://www.topografix.com/GPX/1/1")
  root = ET.Element("gpx", version="1.1", creator="workflow-to-gpx")
  trk = ET.SubElement(root, "trk")
  seg = ET.SubElement(trk, "trkseg")
  for pt in track:
    lat = float(pt.get("lat") or pt.get("latitude"))
    lon = float(pt.get("lon") or pt.get("lng") or pt.get("longitude"))
    trkpt = ET.SubElement(seg, "trkpt", lat=f"{lat}", lon=f"{lon}")
    t = parse_time(pt)
    if t:
      ET.SubElement(trkpt, "time").text = t.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
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

def process_file(path: str, dest: str) -> int:
  with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
  tracks = find_tracks(data)
  written = 0
  for idx, track in enumerate(tracks, start=1):
    tree = track_to_gpx(track)
    date, time = format_start_time(track)
    filename = f"{date}_{time}_track{idx:02d}.gpx"
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

  count = 0
  for name in os.listdir(src):
    if name.lower().endswith(".json"):
      count += process_file(os.path.join(src, name), dest)
  print(f"Written {count} track(s) to {dest}")

if __name__ == "__main__":
  main()
