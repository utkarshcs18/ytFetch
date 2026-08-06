# ytFetch — YouTube Downloader

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-lightgrey" />
  <img src="https://img.shields.io/badge/Backend-yt--dlp-red?logo=youtube&logoColor=white" />
  <img src="https://img.shields.io/badge/Theme-Light-brightgreen" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

A clean, lightweight **YouTube video downloader** with a modern desktop GUI built on top of **CustomTkinter** and **yt-dlp**.  
No ffmpeg required for standard video downloads.

---

## Screenshots

> Launch the app and you'll see a clean light-theme window like this:

| State | Description |
|-------|-------------|
| Idle | URL field, quality picker, folder selector, Download button |
| Downloading | Progress bar with speed & ETA, Stop button |
| Done | Green "Download completed!" status, Close button |

---

## Features

- **Modern Light-Theme GUI** — clean white/grey card layout, no neon, no clutter
- **yt-dlp backend** — actively maintained, works with current YouTube signature encryption (unlike the abandoned `pytube`)
- **No ffmpeg required** — uses pre-merged progressive streams so the app works out of the box on any machine
- **Quality / Format selector** — choose from five presets:
  - Best Quality (MP4)
  - 720p (MP4)
  - 480p (MP4)
  - 360p (MP4)
  - Audio Only (m4a / webm)
- **Real-time progress bar** — shows percentage, download speed (MB/s), and estimated time remaining
- **Stop button** — cancel a running download cleanly at any time; no zombie processes or corrupt files
- **Close button** — appears after a successful download so you can quit in one click
- **Full exception handling** — user-friendly messages for every failure case:
  - Empty / invalid URL
  - Private or age-restricted video
  - Geo-blocked / unavailable video
  - Network / HTTP errors
  - Permission denied on save folder
  - Disk write errors
- **Background threading** — the UI stays fully responsive during downloads; no freezing
- **Automatic ffmpeg fallback** — if a merged format is somehow requested, the app automatically retries with a guaranteed single-file stream

---

## Requirements

| Package | Purpose | Min version |
|---------|---------|-------------|
| `yt-dlp` | YouTube download engine | 2024.x |
| `customtkinter` | Modern Tkinter theme | 5.x / 6.x |
| `pillow` | Image support for CustomTkinter | 9.x |
| `requests` | HTTP (used internally by yt-dlp) | 2.x |

> **Python 3.12** is recommended. Python 3.14 is not yet supported by all dependencies.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/utkarshcs18/ytFetch.git
cd ytFetch
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows cmd:
.\.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install yt-dlp customtkinter pillow requests
```

### 4. Run the app

```bash
python main.py
```

---

## Usage

1. **Paste** a YouTube URL into the URL field.  
2. **Select** a quality/format from the dropdown.  
3. **Choose** a save folder via the Browse button.  
4. Click **Download** — the progress bar will show live speed and ETA.  
5. Click **Stop** at any time to cancel cleanly.  
6. Once done, click **Close** or download another video.

---

## Quality Notes

| Preset | What you get | ffmpeg needed? |
|--------|-------------|---------------- |
| Best Quality (MP4) | Highest resolution single-file MP4 available | ❌ No |
| 720p / 480p / 360p | Pre-merged progressive MP4 at that height | ❌ No |
| Audio Only | Best available audio stream (m4a or webm) | ❌ No |

> **Want 1080p or 4K?** YouTube only offers those as separate video+audio streams that require merging.  
> Install [ffmpeg](https://www.gyan.dev/ffmpeg/builds/) and add it to your system PATH, then the app will automatically use the best available quality without any code changes.

---

## Project Structure

```
ytFetch/
├── main.py          # Application entry point + full GUI + download logic
├── .gitignore       # Git ignore rules
└── README.md        # This file
```

---

## How It Works

```
User clicks Download
        │
        ▼
Validate URL + folder
        │
        ▼
Spin up background threading.Thread
        │
        ▼
yt-dlp extract_info()  ──► fetch title (no download yet)
        │
        ▼
yt-dlp download()  ──► streams progress via _hook()
        │                        │
        │               UI updated via self.after(0, …)
        │               (thread-safe Tkinter scheduling)
        ▼
On success  ──► show "Download completed!" + Close button
On error    ──► show friendly message + restore Download button
On stop     ──► InterruptedError raised inside _hook → clean abort
```

---

## Known Limitations

- Audio-only MP3 conversion requires **ffmpeg** (the app saves raw m4a/webm without it).
- Playlists are intentionally disabled (`noplaylist=True`); only single videos are supported.
- Private, age-restricted, and member-only videos cannot be downloaded without cookies.

---

## License

MIT — do whatever you want, just don't remove attribution.
