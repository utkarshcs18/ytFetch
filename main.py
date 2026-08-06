import traceback
import threading
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog
import yt_dlp

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

FORMAT_OPTIONS = {
    "Best Quality (MP4)": "best[ext=mp4]/best[ext=webm]/best",
    "720p (MP4)":         "best[height<=720][ext=mp4]/best[height<=720]/best",
    "480p (MP4)":         "best[height<=480][ext=mp4]/best[height<=480]/best",
    "360p (MP4)":         "best[height<=360][ext=mp4]/best[height<=360]/best",
    "Audio Only":         "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
}

BG        = "#f5f6fa"
CARD      = "#ffffff"
HEADER_BG = "#ffffff"
BORDER    = "#d8dae5"
TEXT_MAIN = "#1a1a2e"
TEXT_SUB  = "#6b7280"
TEXT_HINT = "#9ca3af"
ENTRY_BG  = "#f9fafb"
BTN_PRIM  = "#2563eb"
BTN_PRIM_H= "#1d4ed8"
BTN_SEC   = "#e5e7eb"
BTN_SEC_H = "#d1d5db"
BTN_STOP  = "#dc2626"
BTN_STOP_H= "#b91c1c"
BTN_OK    = "#16a34a"
BTN_OK_H  = "#15803d"
PROG_FG   = "#2563eb"
PROG_BG   = "#e5e7eb"
OK_C      = "#16a34a"
WARN_C    = "#d97706"
ERR_C     = "#dc2626"
INFO_C    = "#2563eb"


class YTDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ytFetch  -  YouTube Downloader")
        self.geometry("680x560")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.folder_path = None
        self._stop_event = threading.Event()

        self._build_ui()

    def _build_ui(self):
        hdr = ctk.CTkFrame(self, fg_color=HEADER_BG, corner_radius=0,
                           height=62, border_width=1, border_color=BORDER)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="ytFetch",
                     font=ctk.CTkFont("Segoe UI", 22, "bold"),
                     text_color=BTN_PRIM).pack(side="left", padx=22)
        ctk.CTkLabel(hdr, text="YouTube Downloader",
                     font=ctk.CTkFont("Segoe UI", 13),
                     text_color=TEXT_SUB).pack(side="left")

        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14,
                            border_width=1, border_color=BORDER)
        card.pack(fill="both", expand=True, padx=24, pady=18)

        def slabel(txt):
            ctk.CTkLabel(card, text=txt,
                         font=ctk.CTkFont("Segoe UI", 11, "bold"),
                         text_color=TEXT_SUB
                         ).pack(anchor="w", padx=20, pady=(16, 3))

        slabel("YouTube URL")
        self.url_entry = ctk.CTkEntry(
            card, placeholder_text="Paste a YouTube link here...",
            height=40, corner_radius=8,
            border_color=BORDER, fg_color=ENTRY_BG,
            text_color=TEXT_MAIN, placeholder_text_color=TEXT_HINT,
            font=ctk.CTkFont("Segoe UI", 13))
        self.url_entry.pack(fill="x", padx=20, pady=(0, 2))

        slabel("Quality / Format")
        self.quality_var = ctk.StringVar(value="Best Quality (MP4)")
        self.quality_menu = ctk.CTkOptionMenu(
            card, values=list(FORMAT_OPTIONS.keys()),
            variable=self.quality_var,
            height=38, corner_radius=8,
            fg_color=ENTRY_BG, button_color=BTN_SEC,
            button_hover_color=BTN_SEC_H, dropdown_fg_color=CARD,
            text_color=TEXT_MAIN, dropdown_text_color=TEXT_MAIN,
            font=ctk.CTkFont("Segoe UI", 13))
        self.quality_menu.pack(fill="x", padx=20, pady=(0, 2))

        slabel("Save To")
        frow = ctk.CTkFrame(card, fg_color="transparent")
        frow.pack(fill="x", padx=20, pady=(0, 14))
        self.folder_label = ctk.CTkLabel(
            frow, text="No folder selected",
            text_color=TEXT_HINT,
            font=ctk.CTkFont("Segoe UI", 12), anchor="w")
        self.folder_label.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            frow, text="Browse...", width=90, height=34, corner_radius=8,
            fg_color=BTN_SEC, hover_color=BTN_SEC_H, text_color=TEXT_MAIN,
            font=ctk.CTkFont("Segoe UI", 12),
            command=self._select_folder).pack(side="right")

        self.progress = ctk.CTkProgressBar(
            card, height=8, corner_radius=4,
            progress_color=PROG_FG, fg_color=PROG_BG)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=20, pady=(0, 6))

        self.status_label = ctk.CTkLabel(
            card, text="Ready",
            font=ctk.CTkFont("Segoe UI", 12), text_color=TEXT_HINT)
        self.status_label.pack(pady=(0, 10))

        self.btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=20, pady=(0, 18))

        self.btn_download = ctk.CTkButton(
            self.btn_frame, text="Download",
            height=44, corner_radius=10,
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            fg_color=BTN_PRIM, hover_color=BTN_PRIM_H,
            text_color="#ffffff", command=self._start_download)
        self.btn_download.pack(fill="x")

        self.btn_stop = ctk.CTkButton(
            self.btn_frame, text="Stop Download",
            height=44, corner_radius=10,
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            fg_color=BTN_STOP, hover_color=BTN_STOP_H,
            text_color="#ffffff", command=self._stop_download)

        self.btn_close = ctk.CTkButton(
            self.btn_frame, text="Close",
            height=44, corner_radius=10,
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            fg_color=BTN_OK, hover_color=BTN_OK_H,
            text_color="#ffffff", command=self.destroy)

    def _select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = Path(folder)
            d = str(self.folder_path)
            if len(d) > 56:
                d = "..." + d[-53:]
            self.folder_label.configure(text=d, text_color=TEXT_MAIN)

    def _start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self._status("Please enter a YouTube URL.", WARN_C); return
        if not url.startswith("http"):
            self._status("URL must start with http:// or https://", WARN_C); return
        if not self.folder_path:
            self._status("Please select a download folder.", WARN_C); return
        if not self.folder_path.exists():
            self._status("Selected folder does not exist.", WARN_C); return

        self._stop_event.clear()

        self.btn_download.pack_forget()
        self.btn_close.pack_forget()
        self.btn_stop.pack(fill="x")
        self.quality_menu.configure(state="disabled")
        self.progress.set(0)
        self._status("Starting...", INFO_C)

        threading.Thread(
            target=self._worker,
            args=(url, self.folder_path, self.quality_var.get()),
            daemon=True).start()

    def _stop_download(self):
        self._stop_event.set()
        self._status("Stopping...", WARN_C)
        self.btn_stop.configure(state="disabled")

    def _worker(self, url, save_path, quality_label):
        fmt = FORMAT_OPTIONS[quality_label]
        opts = {
            "format": fmt,
            "outtmpl": str(save_path / "%(title)s.%(ext)s"),
            "progress_hooks": [self._hook],
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise ValueError("Could not get video info. Check the URL.")
                if self._stop_event.is_set():
                    raise InterruptedError()
                title = info.get("title", "Video")
                self.after(0, lambda t=title: self._status(
                    "Downloading: " + t[:50] + "...", INFO_C))
                ydl.download([url])
            self.after(0, self._on_done)

        except InterruptedError:
            self.after(0, lambda: self._status("Stopped.", WARN_C))
            self.after(0, self._reset_btns)

        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            if self._stop_event.is_set():
                self.after(0, lambda: self._status("Stopped.", WARN_C))
            elif "ffmpeg" in msg.lower():
                self.after(0, lambda: self._status("Retrying (single-file mode)...", WARN_C))
                self._retry(url, save_path)
                return
            elif "Private video" in msg:
                self.after(0, lambda: self._status("Video is private.", ERR_C))
            elif "unavailable" in msg.lower():
                self.after(0, lambda: self._status("Video unavailable.", ERR_C))
            elif "age" in msg.lower() or "Sign in" in msg:
                self.after(0, lambda: self._status("Age-restricted video.", ERR_C))
            else:
                self.after(0, lambda m=msg: self._status(m[:100], ERR_C))
            self.after(0, self._reset_btns)

        except ValueError as e:
            self.after(0, lambda: self._status(str(e), WARN_C))
            self.after(0, self._reset_btns)
        except PermissionError:
            self.after(0, lambda: self._status("Permission denied. Try another folder.", ERR_C))
            self.after(0, self._reset_btns)
        except OSError as e:
            self.after(0, lambda: self._status("Disk error: " + str(e), ERR_C))
            self.after(0, self._reset_btns)
        except Exception as e:
            traceback.print_exc()
            self.after(0, lambda: self._status("Error: " + str(e), ERR_C))
            self.after(0, self._reset_btns)

    def _retry(self, url, save_path):
        opts = {
            "format": "best[ext=mp4]/best[ext=webm]/best",
            "outtmpl": str(save_path / "%(title)s.%(ext)s"),
            "progress_hooks": [self._hook],
            "quiet": True, "no_warnings": True, "noplaylist": True,
        }
        try:
            if self._stop_event.is_set():
                raise InterruptedError()
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.after(0, self._on_done)
        except InterruptedError:
            self.after(0, lambda: self._status("Stopped.", WARN_C))
            self.after(0, self._reset_btns)
        except Exception as e:
            traceback.print_exc()
            self.after(0, lambda: self._status("Error: " + str(e), ERR_C))
            self.after(0, self._reset_btns)

    def _hook(self, d):
        if self._stop_event.is_set():
            raise InterruptedError("Stopped.")
        st = d.get("status", "")
        if st == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            done  = d.get("downloaded_bytes", 0)
            spd   = d.get("speed") or 0
            if total:
                pct = done / total
                mb  = spd / 1_048_576
                eta = d.get("eta") or 0
                lbl = "Downloading " + str(int(pct * 100)) + "%  -  " + \
                      f"{mb:.1f} MB/s  -  ETA {eta}s"
                self.after(0, lambda p=pct, l=lbl: (
                    self.progress.set(p), self._status(l, INFO_C)))
        elif st == "finished":
            self.after(0, lambda: (
                self.progress.set(1), self._status("Finalizing...", TEXT_SUB)))

    def _status(self, text, color=None):
        self.status_label.configure(
            text=text, text_color=color if color else TEXT_HINT)

    def _on_done(self):
        self.progress.set(1)
        self._status("Download completed!", OK_C)
        self.btn_stop.pack_forget()
        self.quality_menu.configure(state="normal")
        self.btn_download.pack(fill="x", pady=(0, 8))
        self.btn_close.pack(fill="x")

    def _reset_btns(self):
        self.btn_stop.pack_forget()
        self.btn_stop.configure(state="normal")
        self.btn_close.pack_forget()
        self.quality_menu.configure(state="normal")
        self.btn_download.pack(fill="x")


if __name__ == "__main__":
    app = YTDownloader()
    app.mainloop()
