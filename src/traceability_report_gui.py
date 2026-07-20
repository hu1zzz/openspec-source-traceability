#!/usr/bin/env python3
"""Clickable Windows GUI for source traceability validation."""

from __future__ import annotations

import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from validate_source_traceability import validate_change, write_markdown_report


REPORT_NAME = "需求追踪验证报告.md"


def discover_changes(project_root: Path) -> list[str]:
    changes_root = Path(project_root) / "openspec" / "changes"
    if not changes_root.exists():
        return []
    return sorted(
        child.name
        for child in changes_root.iterdir()
        if child.is_dir()
        and child.name != "archive"
        and (child / "source-requirements.yaml").is_file()
    )


def default_project_root() -> Path:
    candidates = [Path.cwd()]
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent)
    else:
        candidates.append(Path(__file__).resolve().parents[1])
    for candidate in candidates:
        if (candidate / "openspec").is_dir():
            return candidate.resolve()
    return Path.cwd().resolve()


def run_validation(project_root: Path, change_name: str, output_path: Path):
    report = validate_change(project_root, change_name)
    write_markdown_report(report, output_path)
    return report


class TraceabilityReportApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("OpenSpec 需求追踪验证工具")
        self.root.geometry("820x620")
        self.root.minsize(700, 520)

        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
        style.configure("Hint.TLabel", foreground="#555555")
        style.configure("Result.TLabel", font=("Microsoft YaHei UI", 11, "bold"))

        self.project_var = tk.StringVar(value=str(default_project_root()))
        self.change_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.status_var = tk.StringVar(value="请选择项目和 change，然后生成报告。")
        self.last_report_path: Path | None = None

        self._build_ui()
        self.refresh_changes()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=22)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="OpenSpec 需求追踪验证工具", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            container,
            text="校验源需求、主规范和当前 change 的双向追踪关系，并生成 Markdown 报告。",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(4, 20))

        form = ttk.Frame(container)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="项目目录").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=7)
        ttk.Entry(form, textvariable=self.project_var).grid(row=0, column=1, sticky="ew", pady=7)
        ttk.Button(form, text="浏览…", command=self.browse_project).grid(row=0, column=2, padx=(8, 0), pady=7)

        ttk.Label(form, text="OpenSpec change").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=7)
        self.change_combo = ttk.Combobox(form, textvariable=self.change_var, state="readonly")
        self.change_combo.grid(row=1, column=1, sticky="ew", pady=7)
        ttk.Button(form, text="刷新", command=self.refresh_changes).grid(row=1, column=2, padx=(8, 0), pady=7)

        ttk.Label(form, text="报告文件").grid(row=2, column=0, sticky="w", padx=(0, 12), pady=7)
        ttk.Entry(form, textvariable=self.output_var).grid(row=2, column=1, sticky="ew", pady=7)
        ttk.Button(form, text="选择…", command=self.browse_output).grid(row=2, column=2, padx=(8, 0), pady=7)

        actions = ttk.Frame(container)
        actions.pack(fill="x", pady=(18, 14))
        ttk.Button(actions, text="生成验证报告", command=self.generate_report).pack(side="left")
        self.open_button = ttk.Button(actions, text="打开报告", command=self.open_report, state="disabled")
        self.open_button.pack(side="left", padx=(10, 0))

        ttk.Separator(container).pack(fill="x", pady=(0, 14))
        ttk.Label(container, textvariable=self.status_var, style="Result.TLabel").pack(anchor="w", pady=(0, 8))

        self.result_text = tk.Text(
            container,
            wrap="word",
            height=18,
            font=("Microsoft YaHei UI", 10),
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=10,
            state="disabled",
        )
        self.result_text.pack(fill="both", expand=True)

    def browse_project(self):
        selected = filedialog.askdirectory(initialdir=self.project_var.get() or str(Path.cwd()))
        if selected:
            self.project_var.set(selected)
            self.refresh_changes()

    def browse_output(self):
        selected = filedialog.asksaveasfilename(
            initialdir=str(Path(self.project_var.get() or Path.cwd())),
            initialfile=REPORT_NAME,
            defaultextension=".md",
            filetypes=[("Markdown 文档", "*.md"), ("所有文件", "*.*")],
        )
        if selected:
            self.output_var.set(selected)

    def refresh_changes(self):
        project_root = Path(self.project_var.get()).expanduser()
        changes = discover_changes(project_root)
        self.change_combo["values"] = changes
        if changes:
            if self.change_var.get() not in changes:
                self.change_var.set(changes[0])
            self.status_var.set(f"发现 {len(changes)} 个带 source-requirements.yaml 的 change。")
        else:
            self.change_var.set("")
            self.status_var.set("未找到可验证的 change，请检查项目目录。")
        self.output_var.set(str(project_root / REPORT_NAME))

    def generate_report(self):
        project_root = Path(self.project_var.get()).expanduser().resolve()
        change_name = self.change_var.get().strip()
        output_path = Path(self.output_var.get()).expanduser()
        if not (project_root / "openspec").is_dir():
            messagebox.showerror("项目无效", "所选目录中不存在 openspec 文件夹。")
            return
        if not change_name:
            messagebox.showerror("未选择 change", "请选择需要验证的 OpenSpec change。")
            return
        if not output_path.is_absolute():
            output_path = project_root / output_path
        try:
            report = run_validation(project_root, change_name, output_path)
        except Exception as exc:
            messagebox.showerror("生成失败", str(exc))
            self.status_var.set("报告生成失败。")
            return

        self.last_report_path = output_path
        self.open_button.configure(state="normal")
        result = "通过" if report.passed else "未通过"
        self.status_var.set(f"验证{result}，报告已生成：{output_path}")
        lines = [
            f"验证结果：{result}",
            f"原始文档需求数：{report.source_count}",
            f"主规范覆盖数：{report.main_spec_covered_count}",
            f"当前 change 处理数：{report.current_handled_count}",
            f"问题数：{len(report.issues)}",
            "",
        ]
        if report.issues:
            lines.append("问题明细：")
            lines.extend(f"[{issue.code}] {issue.message}" for issue in report.issues)
        else:
            lines.append("源需求登记完整，且与 Spec 的双向链接一致。")
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "\n".join(lines))
        self.result_text.configure(state="disabled")

    def open_report(self):
        if self.last_report_path and self.last_report_path.exists():
            os.startfile(self.last_report_path)
        else:
            messagebox.showwarning("报告不存在", "请先生成验证报告。")


def smoke_test(project_root: Path, change_name: str) -> int:
    output_path = Path(project_root).resolve() / REPORT_NAME
    report = run_validation(Path(project_root).resolve(), change_name, output_path)
    print(
        f"smoke_ok passed={report.passed} source={report.source_count} "
        f"main={report.main_spec_covered_count} current={report.current_handled_count}"
    )
    return 0 if report.passed else 1


def main() -> int:
    if len(sys.argv) == 4 and sys.argv[1] == "--smoke-test":
        return smoke_test(Path(sys.argv[2]), sys.argv[3])
    root = tk.Tk()
    TraceabilityReportApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
