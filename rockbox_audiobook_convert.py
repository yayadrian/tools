#!/usr/bin/env python3
"""Convert an audiobook file into an iPod Video (5G) + Rockbox-friendly .m4b."""

import argparse
import json
import os
import shutil
import subprocess
import sys


def probe_audio(ffprobe: str, path: str) -> dict:
    """Run ffprobe and return a dict with channels, duration, and has_cover."""
    cmd = [
        ffprobe,
        "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        "-show_format",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"ffprobe failed on {path!r}:\n{result.stderr}")

    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    fmt = data.get("format", {})

    audio_channels = None
    audio_codec = None
    audio_profile = None
    has_cover = False

    for s in streams:
        codec_type = s.get("codec_type", "")
        if codec_type == "audio" and audio_channels is None:
            audio_channels = int(s.get("channels", 1))
            audio_codec = s.get("codec_name", "")
            audio_profile = s.get("profile", "")
        elif codec_type == "video":
            # Attached pictures show up as video streams with 1 frame or
            # disposition attached_pic=1.
            disp = s.get("disposition", {})
            if disp.get("attached_pic", 0) == 1:
                has_cover = True
            # Some files mark the cover as a plain video stream.
            codec = s.get("codec_name", "")
            if codec in ("mjpeg", "png", "bmp"):
                has_cover = True

    if audio_channels is None:
        sys.exit(f"No audio stream found in {path!r}")

    duration_sec = None
    raw = fmt.get("duration") or None
    if raw is not None:
        try:
            duration_sec = float(raw)
        except (ValueError, TypeError):
            pass

    container = os.path.splitext(path)[1].lower()

    return {
        "channels": audio_channels,
        "codec": audio_codec,
        "profile": audio_profile,
        "duration": duration_sec,
        "has_cover": has_cover,
        "container": container,
    }


def format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "unknown"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m:02d}m {s:02d}s"


def can_remux(info: dict, keep_stereo: bool, bitrate_override: str | None) -> bool:
    """Check whether we can fast-path with stream copy instead of transcoding."""
    if bitrate_override is not None:
        return False
    if info["container"] not in (".m4b", ".m4a", ".mp4"):
        return False
    # Must already be AAC-LC.
    if info["codec"] != "aac":
        return False
    profile = (info.get("profile") or "").lower()
    if profile and "lc" not in profile.lower():
        return False
    # If we need to downmix but the source is stereo, we must transcode.
    if not keep_stereo and info["channels"] > 1:
        return False
    return True


def build_ffmpeg_cmd(
    ffmpeg: str,
    input_path: str,
    output_path: str,
    info: dict,
    keep_stereo: bool,
    bitrate: str | None,
    remux: bool,
) -> list[str]:
    cmd = [ffmpeg, "-i", input_path]

    # ---- stream mapping ----
    cmd += ["-map", "0:a"]
    if info["has_cover"]:
        cmd += ["-map", "0:v?"]

    # ---- audio codec ----
    if remux:
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-c:a", "aac", "-profile:a", "aac_low", "-ar", "44100"]

        # Channels / downmix
        if not keep_stereo and info["channels"] > 1:
            cmd += ["-ac", "1"]
            effective_channels = 1
        else:
            effective_channels = info["channels"]

        # Bitrate
        if bitrate is not None:
            cmd += ["-b:a", bitrate]
        else:
            cmd += ["-b:a", "64k" if effective_channels == 1 else "96k"]

    # ---- cover art ----
    if info["has_cover"]:
        cmd += ["-c:v", "copy"]
        cmd += ["-disposition:v", "attached_pic"]

    # ---- metadata & chapters ----
    cmd += ["-map_metadata", "0", "-map_chapters", "0"]

    # ---- container flags ----
    cmd += ["-movflags", "+faststart"]

    cmd += ["-y", output_path]
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert an audiobook to iPod Video 5G + Rockbox .m4b format.",
    )
    parser.add_argument(
        "input",
        help="Path to the input audiobook file.",
    )
    parser.add_argument(
        "--keep-stereo",
        action="store_true",
        default=False,
        help="Keep stereo channels instead of downmixing to mono (default: downmix).",
    )
    parser.add_argument(
        "--bitrate",
        default=None,
        help="Override audio bitrate (e.g. 80k). Default: 64k mono / 96k stereo.",
    )
    args = parser.parse_args()

    # -- validate input --
    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"Error: file not found: {input_path!r}", file=sys.stderr)
        return 1

    # -- check external tools --
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg:
        print("Error: 'ffmpeg' not found on PATH. Please install FFmpeg.", file=sys.stderr)
        return 1
    if not ffprobe:
        print("Error: 'ffprobe' not found on PATH. Please install FFmpeg.", file=sys.stderr)
        return 1

    # -- probe input --
    print(f"Probing: {input_path}")
    info = probe_audio(ffprobe, input_path)

    ch_label = "mono" if info["channels"] == 1 else f"{info['channels']}ch"
    print(f"  Codec    : {info['codec']} (profile: {info.get('profile') or 'n/a'})")
    print(f"  Channels : {info['channels']} ({ch_label})")
    print(f"  Duration : {format_duration(info['duration'])}")
    print(f"  Cover art: {'yes' if info['has_cover'] else 'no'}")

    # -- determine output path --
    stem = os.path.splitext(os.path.basename(input_path))[0]
    out_dir = os.path.dirname(os.path.abspath(input_path))
    output_path = os.path.join(out_dir, f"{stem}_rockbox.m4b")

    # -- decide remux vs transcode --
    remux = can_remux(info, args.keep_stereo, args.bitrate)
    if remux:
        print("\nInput is already AAC-LC in a compatible container — using fast remux (stream copy).")
    else:
        print("\nTranscoding to AAC-LC .m4b …")

    # -- build & run ffmpeg --
    cmd = build_ffmpeg_cmd(
        ffmpeg, input_path, output_path, info,
        keep_stereo=args.keep_stereo,
        bitrate=args.bitrate,
        remux=remux,
    )
    print(f"\n> {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        print("FFmpeg failed.", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        print(
            "\nHint: If this is a DRM-protected audiobook, Rockbox/FFmpeg can't "
            "decode it—download a DRM-free copy (e.g., MP3/M4B) from your provider.",
            file=sys.stderr,
        )
        return result.returncode

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Done! Output: {output_path}  ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
