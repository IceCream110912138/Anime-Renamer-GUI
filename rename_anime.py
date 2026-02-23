import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import ctypes

# --- 解决 Windows 高分屏模糊问题 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class AnimeRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Anime Renamer GUI v1.1.0")
        self.root.geometry("1000x700")

        self.valid_exts = {
            '.mkv', '.mp4', '.avi', '.rmvb', '.flv', '.wmv', '.mov', '.ts', '.webm',
            '.ass', '.srt', '.ssa', '.vtt', '.sub'
        }

        self.setup_ui()

    def setup_ui(self):
        # 顶部：路径选择
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="文件夹路径:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(top_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(top_frame, text="浏览", command=self.browse_folder).pack(side=tk.LEFT)

        # 中部：配置参数
        config_frame = ttk.LabelFrame(self.root, text="命名配置", padding="10")
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        row1 = ttk.Frame(config_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="番剧名称:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.name_var, width=30).pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="第几季:").pack(side=tk.LEFT, padx=(20, 0))
        self.season_var = tk.StringVar(value="1")
        ttk.Entry(row1, textvariable=self.season_var, width=10).pack(side=tk.LEFT, padx=5)

        row2 = ttk.Frame(config_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Label(row2, text="命名格式:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="{n} S{s}E{e}")
        ttk.Entry(row2, textvariable=self.format_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Label(row2, text="(变量: {n}名称, {s}季, {e}集)", foreground="gray").pack(side=tk.LEFT)

        ttk.Button(row2, text="生成预览", command=self.generate_preview).pack(side=tk.RIGHT, padx=5)

        # 下部：表格展示
        list_frame = ttk.Frame(self.root, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("old_name", "new_name")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        self.tree.heading("old_name", text="原文件名 (不可编辑)")
        self.tree.heading("new_name", text="新文件名 (双击对应的单元格直接编辑)")
        self.tree.column("old_name", width=450)
        self.tree.column("new_name", width=450)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定双击事件
        self.tree.bind("<Double-1>", self.on_double_click)

        # 底部按钮
        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(fill=tk.X)
        ttk.Label(btn_frame, text="提示: 双击新文件名单元格即可原位修改结果", foreground="#005fb8").pack(side=tk.LEFT)
        self.run_btn = ttk.Button(btn_frame, text="确认并执行重命名", command=self.execute_rename, state=tk.DISABLED)
        self.run_btn.pack(side=tk.RIGHT)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
            self.generate_preview()

    def clean_filename_to_ep(self, filename):
        cleaned = re.sub(r'\[.*?\]|\(.*?\)', '', filename)
        cleaned = re.sub(r'v\d+', '', cleaned, flags=re.IGNORECASE)
        numbers = re.findall(r'\d+', cleaned)
        if numbers:
            return int(numbers[-1])
        return None

    def generate_preview(self):
        path = self.path_var.get()
        show_name = self.name_var.get().strip()
        season_str = self.season_var.get().strip()
        fmt = self.format_var.get()

        if not path or not os.path.exists(path): return
        for item in self.tree.get_children(): self.tree.delete(item)

        folder = Path(path)
        try:
            season_num = int(season_str)
        except:
            season_num = 1

        files = sorted(list(folder.iterdir()))
        for file_path in files:
            if file_path.is_file() and file_path.suffix.lower() in self.valid_exts:
                ep_num = self.clean_filename_to_ep(file_path.name)
                if ep_num is not None:
                    new_stem = fmt.replace("{n}", show_name) \
                        .replace("{s}", f"{season_num:02d}") \
                        .replace("{e}", f"{ep_num:02d}")
                    new_name = f"{new_stem}{file_path.suffix}"
                    self.tree.insert("", tk.END, values=(file_path.name, new_name))

        self.run_btn.config(state=tk.NORMAL if self.tree.get_children() else tk.DISABLED)

    def on_double_click(self, event):
        """核心改进：实现真正的一体化原位编辑"""
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return

        column = self.tree.identify_column(event.x)
        if column != "#2": return  # 仅限新文件名列

        item_id = self.tree.focus()
        item_values = self.tree.item(item_id, "values")

        # 获取单元格相对于 Treeview 内部的精确坐标
        bbox = self.tree.bbox(item_id, column)
        if not bbox: return
        x, y, w, h = bbox

        # 核心改动：将 Entry 的父组件设为 self.tree
        # 这样 Entry 就会直接画在表格里的单元格上方
        edit_entry = ttk.Entry(self.tree)
        edit_entry.insert(0, item_values[1])
        edit_entry.select_range(0, tk.END)  # 自动全选

        # 使用 place 覆盖单元格
        edit_entry.place(x=x, y=y, width=w, height=h)
        edit_entry.focus_set()

        def save_edit(event=None):
            new_val = edit_entry.get()
            self.tree.set(item_id, column="#2", value=new_val)
            edit_entry.destroy()

        def cancel_edit(event=None):
            edit_entry.destroy()

        edit_entry.bind("<Return>", save_edit)  # 回车保存
        edit_entry.bind("<FocusOut>", save_edit)  # 失去焦点保存
        edit_entry.bind("<Escape>", cancel_edit)  # Esc 取消

    def execute_rename(self):
        path = self.path_var.get()
        items = self.tree.get_children()
        if not items: return

        if not messagebox.askyesno("确认", f"确定重命名这 {len(items)} 个文件吗？"):
            return

        success = 0
        folder = Path(path)
        for item_id in items:
            old_name, new_name = self.tree.item(item_id, "values")
            old_path = folder / old_name
            new_path = folder / new_name

            try:
                if old_path.exists() and old_name != new_name:
                    old_path.rename(new_path)
                    success += 1
            except Exception as e:
                print(f"失败: {old_name} -> {e}")

        messagebox.showinfo("完成", f"成功重命名 {success} 个文件！")
        self.generate_preview()


if __name__ == "__main__":
    root = tk.Tk()
    app = AnimeRenamerGUI(root)
    root.mainloop()