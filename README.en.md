# Otium

[🇪🇸 Español](README.md) · 🇬🇧 English

**A desktop music player for your moments of calm.**

*Otium* is the Latin word for free time spent on what nourishes the soul. This app comes from a simple idea: listening to music is coming home, a refuge. Paste the link of a YouTube playlist and listen to it in one place, with a calm, dark interface.

<!-- Replace this line with a screenshot: ![Otium](screenshot.png) -->

## Features

- Imports YouTube playlists from their link and saves them on your computer.
- Plays audio only, streamed, without downloading the songs.
- Saved playlists tab, with the cover art of each song.
- Search by title or artist, and sort by title, artist or duration.
- Handles large playlists (hundreds of songs): it only draws the visible rows.
- Color themes, with the option to pick your own accent color.
- Shuffle, repeat playlist or repeat one song, volume control and progress bar.
- Automatically hides songs that can't be played (private, deleted or age-restricted).
- Keyboard shortcuts: `Space` (play/pause), `←` `→` (previous/next), `↑` `↓` (volume).

## Tech stack

Python · Tkinter · [python-vlc](https://pypi.org/project/python-vlc/) · [yt-dlp](https://github.com/yt-dlp/yt-dlp) · Pillow

## Installation

Requirements: Windows 10/11, [Python 3.10 or higher](https://www.python.org/downloads/) and [VLC](https://www.videolan.org/vlc/) installed (the 64-bit version if your Python is 64-bit).

```bash
git clone https://github.com/JavieraGGarcia/otium-music-player.git
cd otium-music-player
pip install python-vlc yt-dlp pillow
python reproductor.py
```

## Usage

1. Click **Nueva playlist** (New playlist) in the sidebar and paste the link of a YouTube playlist (public or unlisted).
2. Click a song to play it.
3. Your playlists (`playlists.json`) and your theme settings (`ajustes.json`) are saved in `%APPDATA%\Otium\`, so each person using the app has their own.

## Roadmap

- More color themes.
- Import playlists from a CSV file (for example, exported from other services).
- Build a standalone executable (`.exe`).

## Note

A personal project made for learning and personal use. Otium does not download or redistribute music: it streams YouTube content. Please use it in accordance with YouTube's terms of service.

## Author

Javiera Gutiérrez García · [GitHub](https://github.com/JavieraGGarcia) · [LinkedIn](https://www.linkedin.com/in/javiera-gutierrez-garc%C3%ADa-00733b415/)