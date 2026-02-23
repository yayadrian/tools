#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Serve the repo with a tiny static HTTP server."""
from __future__ import annotations

import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    description="Serve the repository over a static HTTP server."
  )
  parser.add_argument(
    "--host",
    default="127.0.0.1",
    help="Host address to bind (default: 127.0.0.1).",
  )
  parser.add_argument(
    "--port",
    type=int,
    default=8000,
    help="Port to bind (default: 8000).",
  )
  parser.add_argument(
    "--directory",
    default=".",
    help="Directory to serve (default: current directory).",
  )
  return parser


def main() -> None:
  parser = build_parser()
  args = parser.parse_args()
  directory = Path(args.directory).resolve()
  if not directory.is_dir():
    parser.error(f"{directory} is not a directory")

  handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
  server = ThreadingHTTPServer((args.host, args.port), handler)
  print(f"Serving {directory} at http://{args.host}:{args.port}")
  try:
    server.serve_forever()
  except KeyboardInterrupt:
    print("\nShutting down.")
  finally:
    server.server_close()


if __name__ == "__main__":
  main()
