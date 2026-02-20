import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path


class AnimeRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("番剧一键重命名工具")
        self.root.geometry("900x600")

        # 支持的后缀名扩展 (视频 + 字幕)
        self.valid_exts = {
            '.mkv', '.mp4', '.avi', '.rmvb', '.flv', '.wmv', '.mov', '.ts', '.webm',  # 视频
            '.ass', '.srt', '.ssa', '.vtt', '.sub'  # 字幕
        }

        self.setup_ui()

    def setup_ui(self):
        # --- 顶部：路径选择 ---
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="文件夹路径:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(top_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(top_frame, text="选择文件夹", command=self.browse_folder).pack(side=tk.LEFT)

        # --- 中部：配置参数 ---
        config_frame = ttk.LabelFrame(self.root, text="命名配置", padding="10")
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(config_frame, text="番剧名称:").grid(row=0, column=0, sticky=tk.W)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(config_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(config_frame, text="第几季 (数字):").grid(row=0, column=2, padx=(20, 0), sticky=tk.W)
        self.season_var = tk.StringVar(value="1")
        self.season_entry = ttk.Entry(config_frame, textvariable=self.season_var, width=10)
        self.season_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Button(config_frame, text="刷新/生成预览", command=self.generate_preview).grid(row=0, column=4, padx=20)

        # --- 下部：列表展示 ---
        list_frame = ttk.Frame(self.root, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格预览
        columns = ("old_name", "new_name")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        self.tree.heading("old_name", text="原文件名")
        self.tree.heading("new_name", text="重命名预览 (确认无误后再执行)")
        self.tree.column("old_name", width=400)
        self.tree.column("new_name", width=400)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- 底部：执行按钮 ---
        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(fill=tk.X)
        self.run_btn = ttk.Button(btn_frame, text="🚀 确认并开始批量重命名", command=self.execute_rename,
                                  state=tk.DISABLED)
        self.run_btn.pack(side=tk.RIGHT)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
            self.generate_preview()

    def clean_filename_to_ep(self, filename):
        """核心提取逻辑：排除干扰项提取集数"""
        # 1. 移除 [] 和 () 内容
        cleaned = re.sub(r'\[.*?\]|\(.*?\)', '', filename)
        # 2. 移除 v2/v3 等标识
        cleaned = re.sub(r'v\d+', '', cleaned, flags=re.IGNORECASE)
        # 3. 提取所有数字
        numbers = re.findall(r'\d+', cleaned)
        if numbers:
            return int(numbers[-1])
        return None

    def generate_preview(self):
        path = self.path_var.get()
        show_name = self.name_var.get().strip()
        season_str = self.season_var.get().strip()

        if not path or not os.path.exists(path):
            return

        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.rename_tasks = []
        folder = Path(path)

        try:
            season_num = int(season_str)
        except:
            season_num = 1

        # 遍历文件
        files = sorted(list(folder.iterdir()))  # 排序一下看起来更整齐
        for file_path in files:
            if file_path.is_file() and file_path.suffix.lower() in self.valid_exts:
                ep_num = self.clean_filename_to_ep(file_path.name)

                if ep_num is not None:
                    new_name = f"{show_name} S{season_num:02d}E{ep_num:02d}{file_path.suffix}"
                    self.tree.insert("", tk.END, values=(file_path.name, new_name))
                    self.rename_tasks.append((file_path, file_path.with_name(new_name)))

        if self.rename_tasks:
            self.run_btn.config(state=tk.NORMAL)
        else:
            self.run_btn.config(state=tk.DISABLED)

    def execute_rename(self):
        if not self.rename_tasks:
            return

        if not messagebox.askyesno("确认操作", f"确定要重命名这 {len(self.rename_tasks)} 个文件吗？"):
            return

        success_count = 0
        for old_path, new_path in self.rename_tasks:
            try:
                if old_path.exists() and not new_path.exists():
                    old_path.rename(new_path)
                    success_count += 1
            except Exception as e:
                print(f"重命名失败 {old_path.name}: {e}")

        messagebox.showinfo("完成", f"成功重命名 {success_count} 个文件！")
        self.generate_preview()  # 重命名完成后刷新列表


if __name__ == "__main__":
    root = tk.Tk()
    app = AnimeRenamerGUI(root)
    root.mainloop()