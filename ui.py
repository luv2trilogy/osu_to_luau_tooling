from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

from converter import ConversionPipeline

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore

    BaseTk = TkinterDnD.Tk
    DND_SUPPORT = True
except Exception:
    DND_FILES = None
    BaseTk = tk.Tk
    DND_SUPPORT = False


class BetterConverterApp:
    BG = "#0f172a"
    PANEL = "#111827"
    CARD = "#1f2937"
    BORDER = "#334155"
    TEXT = "#e5e7eb"
    MUTED = "#94a3b8"
    ACCENT = "#2563eb"
    ACCENT_HOVER = "#1d4ed8"
    SECONDARY = "#374151"
    SECONDARY_HOVER = "#4b5563"
    ENTRY_BG = "#0b1220"
    DROP_BG = "#0b1220"
    SUCCESS_BG = "#052e16"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(".osu Converter")
        self.root.geometry("980x640")
        self.root.minsize(840, 560)
        self.root.configure(bg=self.BG)

        self.input_path: Optional[Path] = None
        self.last_output_paths: list[Path] = []

        self._configure_fonts()
        self._build_ui()
        self._set_status("Ready. Choose a file or drop one into the window.")

    def _configure_fonts(self) -> None:
        self.root.option_add("*Font", ("Segoe UI", 10))

    def _build_ui(self) -> None:
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        header = tk.Frame(self.root, bg=self.BG, padx=18, pady=14)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title_row = tk.Frame(header, bg=self.BG)
        title_row.grid(row=0, column=0, sticky="ew")
        title_row.grid_columnconfigure(0, weight=1)

        title = tk.Label(
            title_row,
            text=".osu Converter",
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 20, "bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = tk.Label(
            header,
            text="Convert .osu beatmaps to JSON or Luau.",
            bg=self.BG,
            fg=self.MUTED,
            font=("Segoe UI", 10),
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(6, 0))

        main = tk.Frame(self.root, bg=self.BG, padx=18, pady=0)
        main.grid(row=1, column=0, sticky="nsew")
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

        left = tk.Frame(main, bg=self.BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_rowconfigure(0, weight=0)
        left.grid_rowconfigure(1, weight=0)
        left.grid_rowconfigure(2, weight=0)
        left.grid_columnconfigure(0, weight=1)

        right = tk.Frame(main, bg=self.BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self._build_file_card(left)
        self._build_settings_card(left)
        self._build_actions_card(left)
        self._build_preview_card(right)

        status = tk.Frame(self.root, bg=self.PANEL, padx=16, pady=8)
        status.grid(row=2, column=0, sticky="ew")
        status.grid_columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(
            status,
            textvariable=self.status_var,
            bg=self.PANEL,
            fg=self.MUTED,
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="ew")

    def _card(self, parent: tk.Widget, title: str) -> tk.Frame:
        wrapper = tk.Frame(parent, bg=self.BG)
        wrapper.grid_columnconfigure(0, weight=1)

        label = tk.Label(
            wrapper,
            text=title,
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 11, "bold"),
        )
        label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        card = tk.Frame(
            wrapper,
            bg=self.CARD,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.BORDER,
            bd=0,
            padx=14,
            pady=14,
        )
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        wrapper.card = card  # type: ignore[attr-defined]
        return wrapper

    def _build_file_card(self, parent: tk.Widget) -> None:
        wrapper = self._card(parent, "Input file")
        wrapper.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        card = wrapper.card  # type: ignore[attr-defined]

        top = tk.Frame(card, bg=self.CARD)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        self.file_name_var = tk.StringVar(value="No file selected")
        self.file_path_var = tk.StringVar(value="Drop a .osu file here or click Browse")

        tk.Label(
            top,
            textvariable=self.file_name_var,
            bg=self.CARD,
            fg=self.TEXT,
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            top,
            textvariable=self.file_path_var,
            bg=self.CARD,
            fg=self.MUTED,
            wraplength=360,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.drop_zone = tk.Frame(
            card,
            bg=self.DROP_BG,
            height=90,
            highlightthickness=1,
            highlightbackground=self.BORDER,
        )
        self.drop_zone.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        self.drop_zone.grid_propagate(False)
        self.drop_zone.grid_columnconfigure(0, weight=1)
        self.drop_zone.grid_rowconfigure(0, weight=1)

        self.drop_title_var = tk.StringVar(
            value="Drop .osu files here" if DND_SUPPORT else "Drag-and-drop not available"
        )
        self.drop_hint_var = tk.StringVar(
            value="Click anywhere in this box to browse for a file."
            if not DND_SUPPORT
            else "Drop a file here, or click to browse."
        )

        self.drop_title = tk.Label(
            self.drop_zone,
            textvariable=self.drop_title_var,
            bg=self.DROP_BG,
            fg=self.TEXT,
            font=("Segoe UI", 12, "bold"),
        )
        self.drop_title.grid(row=0, column=0, sticky="s", pady=(18, 2))

        self.drop_hint = tk.Label(
            self.drop_zone,
            textvariable=self.drop_hint_var,
            bg=self.DROP_BG,
            fg=self.MUTED,
        )
        self.drop_hint.grid(row=1, column=0, sticky="n")

        for widget in (self.drop_zone, self.drop_title, self.drop_hint):
            widget.bind("<Button-1>", lambda e: self.pick_file())
            widget.bind("<Enter>", self._drop_hover_in)
            widget.bind("<Leave>", self._drop_hover_out)

        if DND_SUPPORT:
            self.drop_zone.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
            self.drop_zone.dnd_bind("<<Drop>>", self.on_drop)  # type: ignore[attr-defined]

        info_row = tk.Frame(card, bg=self.CARD)
        info_row.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        info_row.grid_columnconfigure(0, weight=1)

        self.file_size_var = tk.StringVar(value="File size: —")
        tk.Label(
            info_row,
            textvariable=self.file_size_var,
            bg=self.CARD,
            fg=self.MUTED,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        tk.Button(
            info_row,
            text="Browse…",
            command=self.pick_file,
            bg=self.ACCENT,
            fg="#ffffff",
            activebackground=self.ACCENT_HOVER,
            activeforeground="#ffffff",
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
        ).grid(row=0, column=1, sticky="e", padx=(10, 0))

    def _build_settings_card(self, parent: tk.Widget) -> None:
        wrapper = self._card(parent, "Output settings")
        wrapper.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        card = wrapper.card  # type: ignore[attr-defined]

        self.format_var = tk.StringVar(value="json")

        format_row = tk.Frame(card, bg=self.CARD)
        format_row.grid(row=0, column=0, sticky="ew")
        format_row.grid_columnconfigure(0, weight=1)

        tk.Label(
            format_row,
            text="Output format",
            bg=self.CARD,
            fg=self.TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w")

        radio_row = tk.Frame(card, bg=self.CARD)
        radio_row.grid(row=1, column=0, sticky="ew", pady=(8, 12))

        for idx, (label, value) in enumerate((
            ("JSON", "json"),
            ("Luau", "luau"),
            ("Both", "both"),
        )):
            rb = tk.Radiobutton(
                radio_row,
                text=label,
                value=value,
                variable=self.format_var,
                bg=self.CARD,
                fg=self.TEXT,
                selectcolor=self.BG,
                activebackground=self.CARD,
                activeforeground=self.TEXT,
                command=self._update_status_hint,
                cursor="hand2",
            )
            rb.grid(row=0, column=idx, sticky="w", padx=(0 if idx == 0 else 16, 0))

        out_row = tk.Frame(card, bg=self.CARD)
        out_row.grid(row=2, column=0, sticky="ew")
        out_row.grid_columnconfigure(0, weight=1)

        tk.Label(
            out_row,
            text="Output folder",
            bg=self.CARD,
            fg=self.TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.output_dir_var = tk.StringVar(value="")
        self.output_entry = tk.Entry(
            out_row,
            textvariable=self.output_dir_var,
            bg=self.ENTRY_BG,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.ACCENT,
        )
        self.output_entry.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        tk.Button(
            out_row,
            text="Browse folder",
            command=self.pick_output_dir,
            bg=self.SECONDARY,
            fg=self.TEXT,
            activebackground=self.SECONDARY_HOVER,
            activeforeground=self.TEXT,
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2",
        ).grid(row=1, column=1, sticky="e", padx=(10, 0), pady=(6, 0))

        self.output_note_var = tk.StringVar(
            value="Leave blank to save next to the source file."
        )
        tk.Label(
            card,
            textvariable=self.output_note_var,
            bg=self.CARD,
            fg=self.MUTED,
            wraplength=360,
            justify="left",
        ).grid(row=3, column=0, sticky="w", pady=(12, 0))

    def _build_actions_card(self, parent: tk.Widget) -> None:
        wrapper = self._card(parent, "Actions")
        wrapper.grid(row=2, column=0, sticky="ew")
        card = wrapper.card  # type: ignore[attr-defined]

        button_row = tk.Frame(card, bg=self.CARD)
        button_row.grid(row=0, column=0, sticky="ew")
        button_row.grid_columnconfigure(0, weight=1)

        tk.Button(
            button_row,
            text="Convert",
            command=self.convert_file,
            bg=self.ACCENT,
            fg="#ffffff",
            activebackground=self.ACCENT_HOVER,
            activeforeground="#ffffff",
            relief="flat",
            padx=16,
            pady=10,
            cursor="hand2",
        ).grid(row=0, column=0, sticky="ew")

        secondary_row = tk.Frame(card, bg=self.CARD)
        secondary_row.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        secondary_row.grid_columnconfigure((0, 1, 2), weight=1)

        tk.Button(
            secondary_row,
            text="Clear",
            command=self.clear_selection,
            bg=self.SECONDARY,
            fg=self.TEXT,
            activebackground=self.SECONDARY_HOVER,
            activeforeground=self.TEXT,
            relief="flat",
            padx=10,
            pady=8,
            cursor="hand2",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        tk.Button(
            secondary_row,
            text="Open output",
            command=self.open_output_folder,
            bg=self.SECONDARY,
            fg=self.TEXT,
            activebackground=self.SECONDARY_HOVER,
            activeforeground=self.TEXT,
            relief="flat",
            padx=10,
            pady=8,
            cursor="hand2",
        ).grid(row=0, column=1, sticky="ew", padx=6)

        tk.Button(
            secondary_row,
            text="Exit",
            command=self.root.destroy,
            bg=self.SECONDARY,
            fg=self.TEXT,
            activebackground=self.SECONDARY_HOVER,
            activeforeground=self.TEXT,
            relief="flat",
            padx=10,
            pady=8,
            cursor="hand2",
        ).grid(row=0, column=2, sticky="ew", padx=(6, 0))

    def _build_preview_card(self, parent: tk.Widget) -> None:
        wrapper = self._card(parent, "Preview")
        wrapper.grid(row=0, column=1, sticky="nsew")
        card = wrapper.card  # type: ignore[attr-defined]
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        preview_header = tk.Frame(card, bg=self.CARD)
        preview_header.grid(row=0, column=0, sticky="ew")
        preview_header.grid_columnconfigure(0, weight=1)

        self.preview_title_var = tk.StringVar(value="Output preview")
        tk.Label(
            preview_header,
            textvariable=self.preview_title_var,
            bg=self.CARD,
            fg=self.TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.preview_meta_var = tk.StringVar(value="Nothing converted yet.")
        tk.Label(
            preview_header,
            textvariable=self.preview_meta_var,
            bg=self.CARD,
            fg=self.MUTED,
        ).grid(row=0, column=1, sticky="e")

        text_frame = tk.Frame(card, bg=self.CARD)
        text_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        self.output_box = tk.Text(
            text_frame,
            wrap="word",
            bg=self.ENTRY_BG,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.ACCENT,
            padx=10,
            pady=10,
            font=("Consolas", 10),
        )
        self.output_box.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(text_frame, command=self.output_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_box.configure(yscrollcommand=scrollbar.set)

        self._set_output_text(
            "Drop or choose an .osu file, pick an output format, then click Convert.\n"
            "The preview panel will show the converted text and output paths."
        )
        self.output_box.configure(state="disabled")

    def _drop_hover_in(self, _event: tk.Event) -> None:
        self.drop_zone.configure(bg="#14213d")
        self.drop_title.configure(bg="#14213d")
        self.drop_hint.configure(bg="#14213d")

    def _drop_hover_out(self, _event: tk.Event) -> None:
        self.drop_zone.configure(bg=self.DROP_BG)
        self.drop_title.configure(bg=self.DROP_BG)
        self.drop_hint.configure(bg=self.DROP_BG)

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _update_status_hint(self) -> None:
        self._set_status(f"Selected output format: {self.format_var.get().upper()}")

    def _set_output_text(self, text: str) -> None:
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", text)
        self.output_box.configure(state="disabled")

    def _parse_dropped_paths(self, data: str) -> list[str]:
        try:
            return list(self.root.tk.splitlist(data))
        except tk.TclError:
            return [data.strip()]

    def _set_input_file(self, path: str) -> None:
        file_path = Path(path).expanduser()

        if not file_path.exists():
            messagebox.showerror("File not found", f"That file does not exist:\n{file_path}")
            return

        if file_path.suffix.lower() != ".osu":
            messagebox.showwarning(
                "Not an .osu file",
                "The selected file does not end in .osu. It may still work, but this converter is intended for .osu beatmaps.",
            )

        self.input_path = file_path
        self.file_name_var.set(file_path.name)
        self.file_path_var.set(str(file_path))

        try:
            size_kb = file_path.stat().st_size / 1024
            self.file_size_var.set(f"File size: {size_kb:.1f} KB")
        except OSError:
            self.file_size_var.set("File size: —")

        self._set_status(f"Loaded {file_path.name}")

    def pick_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select .osu file",
            filetypes=[("osu files", "*.osu"), ("All files", "*.*")],
        )
        if path:
            self._set_input_file(path)

    def on_drop(self, event: tk.Event) -> None:
        paths = self._parse_dropped_paths(getattr(event, "data", ""))
        if not paths:
            return
        self._set_input_file(paths[0])

    def pick_output_dir(self) -> None:
        directory = filedialog.askdirectory(title="Choose output folder")
        if directory:
            self.output_dir_var.set(directory)
            self._set_status(f"Output folder set to {directory}")

    def clear_selection(self) -> None:
        self.input_path = None
        self.last_output_paths = []
        self.file_name_var.set("No file selected")
        self.file_path_var.set("Drop a .osu file here or click Browse")
        self.file_size_var.set("File size: —")
        self._set_output_text("Preview cleared.")
        self.preview_title_var.set("Output preview")
        self.preview_meta_var.set("Nothing converted yet.")
        self._set_status("Selection cleared.")

    def _get_target_dir(self) -> Path:
        raw = self.output_dir_var.get().strip()
        if raw:
            return Path(raw).expanduser()
        if self.input_path is not None:
            return self.input_path.parent
        return Path.cwd()

    def _convert_payload(self, content: str, output_format: str) -> tuple[Optional[str], Optional[str], str]:
        pipeline = ConversionPipeline()
        result = pipeline.convert(content, output_format=output_format)

        if output_format == "json":
            return str(result), None, "json"
        if output_format == "luau":
            return None, str(result), "luau"

        if isinstance(result, str):
            if "\n\n" in result:
                json_text, luau_text = result.split("\n\n", 1)
                return json_text, luau_text, "both"
            return result, result, "both"

        json_text = getattr(result, "json", None)
        luau_text = getattr(result, "luau", None)
        return json_text, luau_text, "both"

    def convert_file(self) -> None:
        if self.input_path is None:
            messagebox.showwarning("No file selected", "Please choose a .osu file first.")
            return

        try:
            content = self.input_path.read_text(encoding="utf-8")
        except Exception as exc:
            messagebox.showerror("Read error", str(exc))
            return

        output_format = self.format_var.get()
        json_text, luau_text, resolved_format = self._convert_payload(content, output_format)

        target_dir = self._get_target_dir()
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            messagebox.showerror("Output folder error", str(exc))
            return

        output_paths: list[Path] = []
        try:
            if resolved_format == "json":
                if json_text is None:
                    raise RuntimeError("JSON output was not produced.")
                out = target_dir / f"{self.input_path.stem}.json"
                out.write_text(json_text, encoding="utf-8")
                output_paths.append(out)

            elif resolved_format == "luau":
                if luau_text is None:
                    raise RuntimeError("Luau output was not produced.")
                out = target_dir / f"{self.input_path.stem}.lua"
                out.write_text(luau_text, encoding="utf-8")
                output_paths.append(out)

            else:
                if json_text is None or luau_text is None:
                    raise RuntimeError("Both outputs were not produced.")
                json_path = target_dir / f"{self.input_path.stem}.json"
                luau_path = target_dir / f"{self.input_path.stem}.lua"
                json_path.write_text(json_text, encoding="utf-8")
                luau_path.write_text(luau_text, encoding="utf-8")
                output_paths.extend([json_path, luau_path])

        except Exception as exc:
            messagebox.showerror("Write error", str(exc))
            return

        self.last_output_paths = output_paths

        preview_parts = [
            "Converted successfully.",
            "",
            "Saved to:",
            *[str(path) for path in output_paths],
            "",
            "--- Preview ---",
        ]

        preview_source = json_text if json_text is not None else luau_text or ""
        preview_parts.append(preview_source if len(preview_source) <= 4000 else preview_source[:4000] + "\n...")
        preview_text = "\n".join(preview_parts)

        self._set_output_text(preview_text)
        self.preview_title_var.set("Output preview")
        self.preview_meta_var.set(f"{resolved_format.upper()} • {len(output_paths)} file(s)")
        self._set_status(f"Saved {len(output_paths)} file(s) to {target_dir}")

        messagebox.showinfo(
            "Conversion complete",
            "Saved:\n" + "\n".join(str(path) for path in output_paths),
        )

    def open_output_folder(self) -> None:
        if self.last_output_paths:
            folder = self.last_output_paths[0].parent
        elif self.input_path is not None:
            folder = self.input_path.parent
        else:
            messagebox.showwarning("No folder to open", "Convert a file first, or choose an input file.")
            return

        try:
            if sys.platform.startswith("win"):
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(folder)], check=False)
            else:
                subprocess.run(["xdg-open", str(folder)], check=False)
        except Exception as exc:
            messagebox.showerror("Open folder error", str(exc))


def main() -> int:
    root = BaseTk()
    BetterConverterApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())