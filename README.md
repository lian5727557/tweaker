# tweaker
*An all-in-one Windows 11 tweaking tool for teachers &amp; students* 
# System Tweaker v4.2

**面向师生的一站式 Windows 11 系统调教工具** / *An all-in-one Windows 11 tweaking tool for teachers & students*

基于 Python + Tkinter，以教学练习方式展示系统底层操作，同时提供开箱即用的视觉界面。
*Built with Python + Tkinter — teaches low-level system operations through hands-on exercises, while also working as a ready-to-use GUI tool.*

---

## ✨ 功能 / Features

### 六大模块，一键开关 / Six modules, one click toggle
- **Windows Update** — 暂停上限延长至 27 年的绕路策略（24H2 适用） / *Extend pause to 27 years via bypass strategy*
- **Security Center** — 四层防线：策略 + 服务 + 驱动 + 计划任务，彻底禁用 Defender / *4-layer defense: policy + service + driver + scheduled tasks*
- **Win11 Right-Click Menu** — 一键切回经典完整菜单 / *Switch back to classic full context menu*
- **Firewall** — 三配置文件一键开关，netsh 即时生效 / *Toggle all 3 profiles instantly via netsh*
- **App Theme** — Catppuccin 暗色 / 亮色一键切换 / *Dark / Light theme toggle*
- **Anime-Friendly Mode** — 全窗口壁纸背景，暗色/亮色自动换图 / *Full-window wallpaper with auto theme-switching*

### 工程亮点 / Highlights
- 🔄 中英双语切换 / *Chinese ↔ English toggle*
- 🖼️ 壁纸 cover 铺满 + 窗口自适应缩放 / *Cover-fit wallpaper with resize adaption*
- 🔧 PyInstaller 打包支持（含 `sys._MEIPASS` 适配） / *Packaging ready*
- 📚 含完整学生练习版 + 参考答案 / *Includes student exercises + answer key*

---

## 🚀 快速开始 / Quick Start

```powershell
# 安装依赖 / Install dependencies
pip install Pillow

# 以管理员身份运行 / Run as Administrator
python tweaker.py
```

## 📦 打包 / Build

```powershell
pyinstaller --onedir --noconsole ^
  --add-data "huajia.jpg;." ^
  --add-data "heihua.png;." ^
  --add-data "chino.ico;." ^
  --icon=chino.ico -y tweaker.py
```

## 📁 项目结构 / Structure

```
├── tweaker.py              # 主程序 / Main program
├── exercise/               # 教学练习包 / Student exercises
│   ├── tweaker_student.py  # 学生版（8 个 TODO 任务）
│   ├── tweaker_answer.py   # 参考答案 / Answer key
│   └── README.md
├── huajia.jpg              # 亮色壁纸 / Light wallpaper
├── heihua.png              # 暗色壁纸 / Dark wallpaper
├── chino.ico               # 窗口图标 / App icon
└── 打包命令.txt             # Build notes
```

## ⚠️ 注意 / Notes

- 需管理员权限运行 / *Requires Administrator privileges*
- 仅建议在了解操作后果的情况下使用 / *Use at your own risk*
- 部分功能修改后需重启生效 / *Some changes require a restart to take effect*
