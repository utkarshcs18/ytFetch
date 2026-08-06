import os
import sys
import traceback
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog
import yt_dlp

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  

class YTDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ytFetch - YouTube Downloader")
        self.geometry("600x400")
        self.resizable(False, False)

        self.url_label = ctk.CTkLabel(self, text="YouTube URL:")
        self.url_label.pack(pady=(20, 5))
        self.url_entry = ctk.CTkEntry(self, width=500)
        self.url_entry.pack(pady=5)

        self.folder_path = None
        self.folder_label = ctk.CTkLabel(self, text="No folder selected")
        self.folder_label.pack(pady=5)
        self.select_button = ctk.CTkButton(self, text="Select Download Folder", command=self.select_folder)
        self.select_button.pack(pady=5)

        self.progress = ctk.CTkProgressBar(self, width=500)
        self.progress.set(0)
        self.progress.pack(pady=(20, 5))
        self.status_label = ctk.CTkLabel(self, text="Ready")
        self.status_label.pack(pady=5)

        self.download_button = ctk.CTkButton(self, text="Download", command=self.start_download)
        self.download_button.pack(pady=10)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = Path(folder)
            self.folder_label.configure(text=f"Folder: {self.folder_path}")
        else:
            self.folder_label.configure(text="No folder selected")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(text="Please enter a YouTube URL.")
            return
        if not self.folder_path:
            self.status_label.configure(text="Please select a download folder.")
            return
        self.download_button.configure(state="disabled")
        self.status_label.configure(text="Starting download...")
        self.after(100, lambda: self.download_video(url, self.folder_path))

    def download_video(self, url, save_path: Path):
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": str(save_path / "%(title)s.%(ext)s"),
            "progress_hooks": [self.progress_hook],
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.configure(text="Download completed successfully!")
        except Exception as e:
            err_msg = f"Error: {e}" if str(e) else "An unexpected error occurred."
            self.status_label.configure(text=err_msg)

            traceback.print_exc()
        finally:
            self.progress.set(0)
            self.download_button.configure(state="normal")

    def progress_hook(self, d):
        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded_bytes = d.get("downloaded_bytes", 0)
            if total_bytes:
                percent = downloaded_bytes / total_bytes
                self.progress.set(percent)
                self.status_label.configure(text=f"Downloading... {percent:.0%}")
        elif d["status"] == "finished":
            self.progress.set(1)
            self.status_label.configure(text="Finalizing file...")

if __name__ == "__main__":
    app = YTDownloader()
    app.mainloop()
