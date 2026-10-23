"""Windows desktop app and unattended batch entry point."""
from __future__ import annotations

import argparse
import json
import os
import queue
import sys
import threading
import time
import traceback
from pathlib import Path

from core import Options, run_batch, scan


def save_report(output: Path, report: dict):
    output.mkdir(parents=True, exist_ok=True)
    target = output / ("转换记录_" + time.strftime("%Y%m%d_%H%M%S") + f"_{time.time_ns() % 1000000:06d}.json")
    with target.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    return target


def gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    root = tk.Tk()
    root.title("云音乐本地转换工具")
    root.geometry("940x800")
    root.minsize(820, 720)
    root.configure(bg="#f4f6fa")
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", font=("Microsoft YaHei UI", 10), background="#f4f6fa")
    style.configure("TLabel", foreground="#253248")
    style.configure("TButton", padding=(14, 8))
    style.configure("Accent.TButton", background="#255ad8", foreground="white")
    style.map("Accent.TButton", background=[("active", "#1848b9"), ("disabled", "#8b9fcb")])
    style.configure("TEntry", padding=8, fieldbackground="white")
    style.configure("TLabelframe", padding=14)
    style.configure("Treeview", rowheight=30, fieldbackground="white", background="white")
    style.configure("Treeview.Heading", padding=7, font=("Microsoft YaHei UI", 10, "bold"))
    style.configure("TProgressbar", background="#255ad8", troughcolor="#dde5f3")
    frame = ttk.Frame(root, padding=24)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="让音乐回到常见格式", font=("Microsoft YaHei UI", 22, "bold")).pack(anchor="w")
    ttk.Label(frame, text="NCM 批量恢复 · 常见音频转换 · 时间轴歌词整理", foreground="#617087").pack(anchor="w", pady=(5, 18))
    source, output = tk.StringVar(), tk.StringVar()
    fmt, bitrate = tk.StringVar(value="mp3"), tk.StringVar(value="320")
    recursive, include_audio, audio_enabled = tk.BooleanVar(value=True), tk.BooleanVar(), tk.BooleanVar(value=True)
    lyric_vars = {kind: tk.BooleanVar(value=kind == "lrc") for kind in ("lrc", "srt", "txt")}
    paths = ttk.LabelFrame(frame, text="文件夹")
    paths.pack(fill="x")
    paths.columnconfigure(1, weight=1)
    def browse(var, is_source):
        selected = filedialog.askdirectory(parent=root, title="选择读取文件夹" if is_source else "选择保存文件夹")
        if selected:
            var.set(selected)
            if is_source and not output.get():
                output.set(str(Path(selected) / "已转换"))
    for row, label, var in ((0, "读取路径", source), (1, "保存路径", output)):
        ttk.Label(paths, text=label).grid(row=row, column=0, padx=(0, 12), pady=4)
        ttk.Entry(paths, textvariable=var).grid(row=row, column=1, sticky="ew", pady=4)
        ttk.Button(paths, text="浏览…", command=lambda v=var, r=row: browse(v, r == 0)).grid(row=row, column=2, padx=(10, 0))
    flags = ttk.Frame(paths)
    flags.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))
    ttk.Checkbutton(flags, text="包含子文件夹，并保留目录结构", variable=recursive).pack(side="left")
    ttk.Checkbutton(flags, text="同时转换已有 MP3 / FLAC / WAV", variable=include_audio).pack(side="left", padx=20)
    settings = ttk.LabelFrame(frame, text="输出设置")
    settings.pack(fill="x", pady=14)
    first = ttk.Frame(settings)
    first.pack(fill="x")
    ttk.Checkbutton(first, text="处理音频", variable=audio_enabled).pack(side="left", padx=(0, 18))
    for kind, label in (("mp3", "MP3 · 兼容常见播放器"), ("flac", "FLAC · 无损"), ("wav", "WAV · 未压缩")):
        ttk.Radiobutton(first, text=label, value=kind, variable=fmt).pack(side="left", padx=(0, 18))
    second = ttk.Frame(settings)
    second.pack(fill="x", pady=(12, 0))
    ttk.Label(second, text="MP3 码率").pack(side="left")
    ttk.Combobox(second, textvariable=bitrate, values=("128", "192", "256", "320"), state="readonly", width=6).pack(side="left", padx=(10, 5))
    ttk.Label(second, text="kbps    歌词输出：").pack(side="left")
    for kind, label in (("lrc", "LRC（播放器）"), ("srt", "SRT（字幕）"), ("txt", "TXT（纯文本）")):
        ttk.Checkbutton(second, text=label, variable=lyric_vars[kind]).pack(side="left", padx=(0, 12))
    ttk.Label(settings, text="原 MP3 → MP3 直接恢复原码率；转为 FLAC / WAV 不会提高原有音质。", foreground="#617087").pack(anchor="w", pady=(10, 0))
    ttk.Label(settings, text="歌词支持 LRC、YRC 和网易云歌词 JSON；NCM 不内含歌词，需要已有本地歌词文件。", foreground="#617087").pack(anchor="w", pady=(3, 0))
    actions = ttk.Frame(frame)
    actions.pack(fill="x", pady=(0, 12))
    events, cancel = queue.Queue(), threading.Event()
    running = False
    status = tk.StringVar(value="选择文件夹后点击“扫描文件”，或直接开始转换。")
    def options():
        if not source.get().strip() or not output.get().strip():
            raise ValueError("请先选择读取路径和保存路径")
        return Options(Path(source.get()), Path(output.get()), fmt.get(), int(bitrate.get()),
                       tuple(k for k, v in lyric_vars.items() if v.get()), recursive.get(),
                       include_audio.get(), audio_enabled.get())
    results_frame = ttk.Frame(frame)
    table = ttk.Treeview(results_frame, columns=("name", "status"), show="headings", selectmode="browse", height=5)
    table.heading("name", text="文件")
    table.heading("status", text="状态 / 结果")
    table.column("name", width=360, minwidth=200)
    table.column("status", width=450, minwidth=200)
    def preview():
        try:
            tasks = scan(options())
            table.delete(*table.get_children())
            for kind, file in tasks:
                table.insert("", "end", values=(str(file.relative_to(options().source)), "待处理 · " + ("音频" if kind == "audio" else "歌词")))
            status.set(f"找到 {len(tasks)} 个文件；已有目标文件会跳过，原文件保留。")
        except Exception as error:
            messagebox.showerror("无法扫描", str(error), parent=root)
    def worker(settings):
        try:
            result = run_batch(settings, cancel, lambda *args: events.put(args))
            report = save_report(settings.output, result)
            events.put(("done", result, str(report)))
        except Exception as error:
            events.put(("fatal", str(error)))
    def start():
        nonlocal running
        try:
            settings = options()
            tasks = scan(settings)
            if not tasks:
                raise ValueError("没有找到可处理的文件")
        except Exception as error:
            messagebox.showerror("无法开始", str(error), parent=root)
            return
        table.delete(*table.get_children())
        cancel.clear()
        running = True
        start_button.configure(state="disabled")
        preview_button.configure(state="disabled")
        cancel_button.configure(state="normal")
        progress["value"] = 0
        status.set("开始处理…")
        threading.Thread(target=worker, args=(settings,), daemon=True).start()
    def stop():
        cancel.set()
        status.set("正在取消并清理临时文件…")
        cancel_button.configure(state="disabled")
    def open_output():
        if output.get() and Path(output.get()).is_dir():
            os.startfile(output.get())
        else:
            messagebox.showinfo("保存文件夹", "文件夹会在首次转换时创建。", parent=root)
    preview_button = ttk.Button(actions, text="扫描文件", command=preview)
    preview_button.pack(side="left")
    start_button = ttk.Button(actions, text="开始批量转换", style="Accent.TButton", command=start)
    start_button.pack(side="left", padx=10)
    cancel_button = ttk.Button(actions, text="取消", state="disabled", command=stop)
    cancel_button.pack(side="left")
    ttk.Button(actions, text="打开保存文件夹", command=open_output).pack(side="right")
    table.pack(side="left", fill="both", expand=True)
    scroll = ttk.Scrollbar(results_frame, orient="vertical", command=table.yview)
    scroll.pack(side="right", fill="y")
    table.configure(yscrollcommand=scroll.set)
    footer = ttk.Frame(frame)
    footer.pack(side="bottom", fill="x")
    progress = ttk.Progressbar(footer, maximum=100)
    progress.pack(fill="x", pady=(14, 8))
    ttk.Label(footer, textvariable=status, wraplength=870).pack(anchor="w")
    ttk.Label(footer, text="完全本地处理 · 无需登录 · 不上传文件 · 不覆盖原文件", foreground="#617087").pack(anchor="w", pady=(10, 0))
    results_frame.pack(fill="both", expand=True)
    def poll():
        nonlocal running
        try:
            while True:
                event = events.get_nowait()
                if event[0] == "start":
                    status.set(f"正在处理 {event[1] + 1}/{event[2]}：{event[3]}")
                elif event[0] == "progress":
                    progress["value"] = 100 * (event[1] + event[3]) / event[2]
                elif event[0] == "result":
                    row = event[3]
                    table.insert("", "end", values=(Path(row["input"]).name, row["message"]))
                    table.yview_moveto(1)
                elif event[0] in ("done", "fatal"):
                    running = False
                    start_button.configure(state="normal")
                    preview_button.configure(state="normal")
                    cancel_button.configure(state="disabled")
                    if event[0] == "fatal":
                        status.set("未完成：" + event[1])
                        messagebox.showerror("转换失败", event[1], parent=root)
                    else:
                        result = event[1]
                        counts = {key: sum(row["status"] == key for row in result["results"]) for key in ("success", "skipped", "error")}
                        status.set(f"{'已取消' if result['cancelled'] else '已完成'}：成功 {counts['success']} 项，跳过 {counts['skipped']} 项，失败 {counts['error']} 项。转换记录已保存。")
                        if not result["cancelled"]:
                            progress["value"] = 100
        except queue.Empty:
            pass
        root.after(100, poll)
    def close():
        if running:
            cancel.set()
            status.set("正在停止；清理完成后可关闭窗口。")
        else:
            root.destroy()
    root.protocol("WM_DELETE_WINDOW", close)
    poll()
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="NCM 批量恢复与歌词转换（离线）")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--audio", choices=("mp3", "flac", "wav"), default="mp3")
    parser.add_argument("--bitrate", type=int, choices=(128, 192, 256, 320), default=320)
    parser.add_argument("--lyrics", nargs="*", choices=("lrc", "srt", "txt"), default=["lrc"])
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--include-audio", action="store_true")
    parser.add_argument("--no-audio", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.input and not args.output:
        gui()
        return 0
    if not args.input or not args.output:
        parser.error("--input 与 --output 必须同时指定")
    settings = Options(args.input, args.output, args.audio, args.bitrate, tuple(args.lyrics),
                       args.recursive, args.include_audio, not args.no_audio)
    try:
        result = run_batch(settings, threading.Event())
        save_report(args.output, result)
        if args.report:
            args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        if sys.stdout:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if any(row["status"] == "error" for row in result["results"]) else 0
    except Exception as error:
        if args.report:
            args.report.write_text(json.dumps({"error": str(error)}, ensure_ascii=False), encoding="utf-8")
        if sys.stderr:
            print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Windowed executables have no stderr; surface startup errors in a dialog.
        import tkinter.messagebox
        tkinter.messagebox.showerror("启动失败", traceback.format_exc())
        sys.exit(1)
