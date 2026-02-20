# Anime Renamer GUI - 专为压制组命名习惯设计的番剧重命名工具

这是一个基于 Python + Tkinter 开发的轻量级番剧批量重命名工具。旨在解决自动化刮削软件（如 TinyMediaManager, Plex, Emby）在面对特定压制组命名格式时出现的识别错误问题。

## 🌟 为什么写这个程序？

在使用 **TinyMediaManager (TMM)** 等主流刮削工具时，我发现它们提取集数（Episode Number）的逻辑通常是“匹配文件名中出现的第一个数字”。

这就导致了一个巨大的困境：
- **压制组名称干扰**：很多优秀的压制组（如 `Moozzi2`, `VCB-Studio`）名字里自带数字。
- **参数干扰**：文件名中包含 `1080p`, `x264`, `10bit` 等信息。

**典型错误案例：**
文件名：`[Moozzi2] Nagasarete Airantou - 18 (BD 1920x1080 x.264 Flac).mkv`
- **TMM 逻辑**：识别到 `Moozzi2` 中的 `2` -> 错误识别为第 2 集。
- **本程序逻辑**：
  1. 自动忽略 `[]` 和 `()` 内的所有内容。
  2. 在剩余文本中智能定位最后一个数字。
  3. 精准识别出第 `18` 集。

## ✨ 功能特性

- **智能识别**：精准剔除中括号（压制组信息）和小括号（视频参数）的干扰。
- **全格式兼容**：支持 `.mkv`, `.mp4`, `.avi` 等视频格式，同时兼容 `.ass`, `.srt` 等字幕格式同步重命名。
- **可视化操作**：提供直观的 GUI 界面，支持文件夹一键选择。
- **安全预览**：在正式修改前提供完整的重命名对比表格，防止误操作。
- **标准命名**：统一输出为 `番剧名称 S01E01` 格式，完美契合 Plex/Emby 刮削规范。

## 🚀 如何使用

### 方式一：直接运行（推荐）
前往 [Releases](你的GitHub链接/releases) 页面下载最新的 `Anime_Renamer.exe`，双击即可运行，无需安装 Python 环境。

### 方式二：开发者模式
1. 克隆仓库：`git clone https://github.com/你的用户名/Anime-Renamer.git`
2. 运行脚本：`python src/rename_anime.py`

## 🛠 开发环境
- Python 3.x
- 标准库：tkinter, re, pathlib, os

## 📝 开源协议
[MIT License](LICENSE)

## 📷 界面截图

<img width="1123" height="777" alt="Screenshot 2026-02-20 232259" src="https://github.com/user-attachments/assets/16916bf1-dbe6-4399-b09a-03f7c2fa1bf8" />

