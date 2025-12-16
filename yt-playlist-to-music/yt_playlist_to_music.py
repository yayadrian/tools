# /// script
# requires-python = ">=3.12"
# dependencies = ["yt-dlp", "mutagen"]
# ///

"""
YouTube Playlist to M4A Downloader

Downloads YouTube playlists (or individual videos) as m4a audio files with embedded
metadata and cover art.

Usage:
    # Download a playlist
    uv run yt_playlist_to_music.py "https://www.youtube.com/playlist?list=..."
    
    # Download a single video
    uv run yt_playlist_to_music.py "https://www.youtube.com/watch?v=..." --single
    
    # Specify output directory
    uv run yt_playlist_to_music.py "URL" --output ~/Music
    
    # Set audio quality (bitrate)
    uv run yt_playlist_to_music.py "URL" --quality 256K
    
    # Skip already downloaded files
    uv run yt_playlist_to_music.py "URL" --skip-existing
    
    # Verbose output
    uv run yt_playlist_to_music.py "URL" --verbose

Requirements:
    - ffmpeg must be installed on your system
    - Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

import yt_dlp


def check_ffmpeg():
  """Check if ffmpeg is available in PATH."""
  if not shutil.which('ffmpeg'):
    print("Error: ffmpeg is not installed or not found in PATH.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Please install ffmpeg:", file=sys.stderr)
    print("  macOS:   brew install ffmpeg", file=sys.stderr)
    print("  Linux:   sudo apt install ffmpeg", file=sys.stderr)
    print("  Windows: Download from https://ffmpeg.org/download.html", file=sys.stderr)
    sys.exit(1)


def create_progress_hook(verbose=False):
  """Create a progress hook for yt_dlp to report download status."""
  def progress_hook(d):
    if d['status'] == 'downloading':
      if verbose:
        filename = d.get('filename', 'Unknown')
        percent = d.get('_percent_str', '0%')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        print(f"Downloading: {filename} - {percent} at {speed} ETA: {eta}", end='\r')
    elif d['status'] == 'finished':
      filename = d.get('filename', 'Unknown')
      print(f"Downloaded: {filename}")
      if verbose:
        print("Converting to m4a and embedding metadata...")
    elif d['status'] == 'error':
      print(f"Error during download", file=sys.stderr)
  
  return progress_hook


def download_audio(url, output_dir, quality, is_single, skip_existing, verbose):
  """Download audio from YouTube URL(s) as m4a with metadata."""
  
  # Determine output template based on single/playlist mode
  if is_single:
    outtmpl = str(Path(output_dir) / '%(title)s.%(ext)s')
  else:
    outtmpl = str(Path(output_dir) / '%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s')
  
  # Configure yt_dlp options
  ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'postprocessors': [
      {
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
        'preferredquality': quality,
      },
      {
        'key': 'FFmpegThumbnailsConvertor',
        'format': 'jpg',
        'when': 'before_dl',
      },
      {
        'key': 'FFmpegMetadata',
        'add_metadata': True,
      },
      {
        'key': 'EmbedThumbnail',
        'already_have_thumbnail': False,
      },
    ],
    'writethumbnail': True,
    'postprocessor_args': {
      'ffmpeg_thumbnail': ['-vf', 'crop=min(iw\\,ih):min(iw\\,ih)'],
    },
    'outtmpl': outtmpl,
    'progress_hooks': [create_progress_hook(verbose)],
    'quiet': not verbose,
    'no_warnings': not verbose,
  }
  
  # Add skip existing files option
  if skip_existing:
    ydl_opts['download_archive'] = str(Path(output_dir) / '.yt_archive.txt')
  
  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      print(f"Starting download from: {url}")
      if is_single:
        print("Mode: Single video")
      else:
        print("Mode: Playlist")
      print(f"Output directory: {output_dir}")
      print(f"Audio quality: {quality}")
      print("")
      
      ydl.download([url])
      
      print("")
      print("Download completed successfully!")
      
  except yt_dlp.utils.DownloadError as e:
    print(f"Download error: {e}", file=sys.stderr)
    sys.exit(1)
  except Exception as e:
    print(f"Unexpected error: {e}", file=sys.stderr)
    sys.exit(1)


def main():
  parser = argparse.ArgumentParser(
    description='Download YouTube playlists or videos as m4a audio files with metadata',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  %(prog)s "https://www.youtube.com/playlist?list=..."
  %(prog)s "https://www.youtube.com/watch?v=..." --single
  %(prog)s "URL" --output ~/Music --quality 256K --verbose
    """
  )
  
  parser.add_argument(
    'url',
    help='YouTube playlist or video URL'
  )
  
  parser.add_argument(
    '-o', '--output',
    default='.',
    help='Output directory (default: current directory)'
  )
  
  parser.add_argument(
    '-q', '--quality',
    default='192K',
    help='Audio quality as bitrate (e.g., 128K, 192K, 256K, 320K) or VBR 0-10 (default: 192K)'
  )
  
  parser.add_argument(
    '-s', '--single',
    action='store_true',
    help='Download as single video instead of playlist'
  )
  
  parser.add_argument(
    '--skip-existing',
    action='store_true',
    help='Skip already downloaded files (maintains a download archive)'
  )
  
  parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help='Enable verbose output'
  )
  
  args = parser.parse_args()
  
  # Check for ffmpeg
  check_ffmpeg()
  
  # Clean URL by removing escape backslashes
  # Remove backslashes that escape special characters like \?, \=, \&
  cleaned_url = args.url.replace('\\', '')
  
  # Create output directory if it doesn't exist
  output_path = Path(args.output).expanduser().resolve()
  output_path.mkdir(parents=True, exist_ok=True)
  
  # Download
  download_audio(
    cleaned_url,
    output_path,
    args.quality,
    args.single,
    args.skip_existing,
    args.verbose
  )


if __name__ == '__main__':
  main()
