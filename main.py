import os
import sys
import traceback
import threading
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FORMAT_OPTIONS = {
    "Best Quality (MP4)":  "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "720p (MP4)":          "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]",
    "480p (MP4)":          "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]",
    "360p (MP4)":          "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best[height<=360]",
    "Audio Only (MP3)":    "bestaudio/best",
}

class YTDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ytFetch  ·  YouTube Downloader")
        self.geometry("680x520")
        self.resizable(False, False)
        self.configure(fg_color="#0f0f13")

        self._build_ui()
        self.folder_path: Path | None = None
        self._download_thread: threading.Thread | None = None

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="#1a1a24", corner_radius=0, height=64)
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="▶  ytFetch",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#4fc3f7",
        ).pack(side="left", padx=24, pady=12)
        ctk.CTkLabel(
            header,
            text="YouTube Downloader",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#7a7a9a",
        ).pack(side="left", pady=12)

        card = ctk.CTkFrame(self, fg_color="#1e1e2e", corner_radius=18)
        card.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(
            card, text="YouTube URL",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#8888aa",
        ).pack(anchor="w", padx=20, pady=(20, 2))

        url_row = ctk.CTkFrame(card, fg_color="transparent")
        url_row.pack(fill="x", padx=20, pady=(0, 12))

        self.url_entry = ctk.CTkEntry(
            url_row,
            placeholder_text="Paste YouTube link here…",
            height=42,
            corner_radius=10,
            border_color="#3a3a5c",
            fg_color="#12121c",
            text_color="#e0e0f0",
            font=ctk.CTkFont(size=13),
        )
        self.url_entry.pack(fill="x")

        ctk.CTkLabel(
            card, text="Quality / Format",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#8888aa",
        ).pack(anchor="w", padx=20, pady=(0, 2))

        self.quality_var = ctk.StringVar(value="Best Quality (MP4)")
        self.quality_menu = ctk.CTkOptionMenu(
            card,
            values=list(FORMAT_OPTIONS.keys()),
            variable=self.quality_var,
            height=38,
            corner_radius=10,
            fg_color="#12121c",
            button_color="#2a2a4c",
            button_hover_color="#3a3a6c",
            dropdown_fg_color="#1e1e2e",
            text_color="#e0e0f0",
            font=ctk.CTkFont(size=13),
        )
        self.quality_menu.pack(fill="x", padx=20, pady=(0, 14))

        ctk.CTkLabel(
            card, text="Save To",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#8888aa",
        ).pack(anchor="w", padx=20, pady=(0, 2))

        folder_row = ctk.CTkFrame(card, fg_color="transparent")
        folder_row.pack(fill="x", padx=20, pady=(0, 16))

        self.folder_label = ctk.CTkLabel(
            folder_row,
            text="No folder selected",
            text_color="#5a5a7a",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self.folder_label.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            folder_row,
            text="Browse…",
            width=100,
            height=34,
            corner_radius=8,
            fg_color="#2a2a4c",
            hover_color="#3a3a6c",
            command=self.select_folder,
        ).pack(side="right")

        self.progress = ctk.CTkProgressBar(
            card, height=10, corner_radius=5,
            progress_color="#4fc3f7",
            fg_color="#12121c",
        )
        self.progress.set(0)
        self.progress.pack(fill="x", padx=20, pady=(0, 6))

        self.status_label = ctk.CTkLabel(
            card, text="Ready",
            font=ctk.CTkFont(size=12),
            text_color="#6a6a8a",
        )
        self.status_label.pack(pady=(0, 12))

        self.download_button = ctk.CTkButton(
            card,
            text="⬇  Download",
            height=46,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#1565c0",
            hover_color="#1e88e5",
            command=self.start_download,
        )
        self.download_button.pack(fill="x", padx=20, pady=(0, 20))

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = Path(folder)
            display = str(self.folder_path)
            if len(display) > 55:
                display = "…" + display[-52:]
            self.folder_label.configure(text=display, text_color="#c0c0e0")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self._set_status("⚠  Please enter a YouTube URL.", "#ffb74d")
            return
        if not url.startswith("http"):
            self._set_status("⚠  URL must start with http:// or https://", "#ffb74d")
            return
        if not self.folder_path:
            self._set_status("⚠  Please select a download folder.", "#ffb74d")
            return
        if not self.folder_path.exists():
            self._set_status("⚠  Selected folder no longer exists.", "#ffb74d")
            return

        self.download_button.configure(state="disabled")
        self.quality_menu.configure(state="disabled")
        self.progress.set(0)
        self._set_status("Starting download…", "#4fc3f7")

        self._download_thread = threading.Thread(
            target=self._download_worker,
            args=(url, self.folder_path, self.quality_var.get()),
            daemon=True,
        )
        self._download_thread.start()

    def _download_worker(self, url: str, save_path: Path, quality_label: str):
        fmt = FORMAT_OPTIONS[quality_label]
        is_audio_only = "Audio Only" in quality_label

        ydl_opts: dict = {
            "outtmpl": str(save_path / "%(title)s.%(ext)s"),
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "format": fmt,
        }

        if is_audio_only:
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
           
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise ValueError("Could not retrieve video information. Check the URL.")
                title = info.get("title", "Video")
                self._set_status(f"Downloading: {title[:50]}…", "#4fc3f7")
                ydl.download([url])
            self.after(0, self._on_success)

        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            if "ffmpeg" in msg.lower():
                self.after(0, lambda: self._set_status("⚙  Retrying without merging…", "#ffb74d"))
                self._retry_no_ffmpeg(url, save_path)
            elif "Private video" in msg:
                self.after(0, lambda: self._set_status("🔒  Video is private.", "#ef5350"))
            elif "Video unavailable" in msg or "not available" in msg.lower():
                self.after(0, lambda: self._set_status("❌  Video unavailable in your region.", "#ef5350"))
            elif "Sign in" in msg or "age" in msg.lower():
                self.after(0, lambda: self._set_status("🔞  Age-restricted video – cannot download.", "#ef5350"))
            else:
                self.after(0, lambda: self._set_status(f"❌  {msg[:120]}", "#ef5350"))
            self.after(0, self._re_enable)

        except ValueError as e:
            self.after(0, lambda: self._set_status(f"⚠  {e}", "#ffb74d"))
            self.after(0, self._re_enable)

        except PermissionError:
            self.after(0, lambda: self._set_status("🚫  Permission denied. Choose a different folder.", "#ef5350"))
            self.after(0, self._re_enable)

        except OSError as e:
            self.after(0, lambda: self._set_status(f"💾  Disk error: {e}", "#ef5350"))
            self.after(0, self._re_enable)

        except Exception as e:
            traceback.print_exc()
            self.after(0, lambda: self._set_status(f"❌  Unexpected error: {e}", "#ef5350"))
            self.after(0, self._re_enable)

    def _retry_no_ffmpeg(self, url: str, save_path: Path):
        ydl_opts = {
            "format": "best[ext=mp4]/best[ext=webm]/best",
            "outtmpl": str(save_path / "%(title)s.%(ext)s"),
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, self._on_success)
        except Exception as e:
            traceback.print_exc()
            self.after(0, lambda: self._set_status(f"❌  {e}", "#ef5350"))
        finally:
            self.after(0, self._re_enable)

    def _progress_hook(self, d: dict):
        status = d.get("status", "")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            done  = d.get("downloaded_bytes", 0)
            speed = d.get("speed") or 0
            if total:
                pct = done / total
                speed_mb = speed / 1_048_576
                eta = d.get("eta") or 0
                label = f"Downloading… {pct:.0%}  •  {speed_mb:.1f} MB/s  •  ETA {eta}s"
                self.after(0, lambda p=pct, l=label: (
                    self.progress.set(p),
                    self._set_status(l, "#4fc3f7"),
                ))
        elif status == "finished":
            self.after(0, lambda: (
                self.progress.set(1),
                self._set_status("Merging / finalizing file…", "#aed6f1"),
            ))

    def _set_status(self, text: str, color: str = "#6a6a8a"):
        self.status_label.configure(text=text, text_color=color)

    def _on_success(self):
        self.progress.set(1)
        self._set_status("✅  Download completed!", "#66bb6a")
        self._re_enable()

    def _re_enable(self):
        self.download_button.configure(state="normal")
        self.quality_menu.configure(state="normal")


if __name__ == "__main__":
    app = YTDownloader()
    app.mainloop()
