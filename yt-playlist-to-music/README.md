# YouTube Playlist to M4A Downloader

Download YouTube playlists or individual videos as high-quality m4a audio files with embedded metadata and cover art.

## Features

- Downloads entire YouTube playlists or single videos
- Converts to m4a format with configurable quality
- Embeds metadata (title, artist, album, track number)
- Embeds thumbnail as cover art
- Organizes playlist downloads by playlist name with track numbering
- Skip already downloaded files with download archive
- Progress reporting during download

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (for running the script)
- **ffmpeg** (must be installed on your system)

### Installing ffmpeg

```bash
# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Usage

### Basic Usage

```bash
# Download a playlist
uv run yt_playlist_to_music.py "https://www.youtube.com/playlist?list=PLxxxxxx"

# Download a single video
uv run yt_playlist_to_music.py "https://www.youtube.com/watch?v=xxxxx" --single
```

### Options

- `-o, --output DIR` - Output directory (default: current directory)
- `-q, --quality QUALITY` - Audio quality as bitrate, e.g., `128K`, `192K`, `256K`, `320K` (default: `192K`)
- `-s, --single` - Download as single video instead of playlist
- `--skip-existing` - Skip already downloaded files (maintains download archive)
- `-v, --verbose` - Enable verbose output with detailed progress

### Examples

```bash
# Download playlist to specific directory with high quality
uv run yt_playlist_to_music.py "PLAYLIST_URL" --output ~/Music --quality 320K

# Download single video with verbose output
uv run yt_playlist_to_music.py "VIDEO_URL" --single --verbose

# Download playlist and skip existing files
uv run yt_playlist_to_music.py "PLAYLIST_URL" --skip-existing
```

## Output Structure

### Playlist Mode (default)
```
output_dir/
  Playlist Name/
    01 - First Song.m4a
    02 - Second Song.m4a
    ...
```

### Single Mode
```
output_dir/
  Video Title.m4a
```

## Metadata

Each m4a file includes:
- **Title** - Video title
- **Artist** - Channel/uploader name
- **Album** - Playlist title (playlist mode only)
- **Track Number** - Position in playlist (playlist mode only)
- **Cover Art** - Video thumbnail

## Notes

- The `--skip-existing` option creates a `.yt_archive.txt` file in the output directory to track downloaded videos
- Downloads use the best available audio quality up to the specified bitrate
- Conversion to m4a and metadata embedding happen automatically via ffmpeg
