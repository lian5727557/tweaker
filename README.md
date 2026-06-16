# System Tweaker v4.2 🐾

[![中文](https://img.shields.io/badge/中文-简体-red)](#中文) | [![English](https://img.shields.io/badge/English-read-blue)](#english)

**面向师生的一站式 Windows 11 系统调教工具**
*An all-in-one Windows 11 tweaking tool for teachers & students*

---

<a name="中文"></a>

## 🇨🇳 中文

### 简介

System Tweaker v4.2 是一款基于 Python + Tkinter 的 Windows 11 系统调教工具。它将底层的注册表操作、服务管理、驱动控制封装为一键开关，同时提供了完整的双语 GUI 界面。项目的另一个身份是 **Python 教学练习包**——`exercise/` 目录中包含 8 个任务的 TODO 学生版和完整参考答案，涵盖了 `ctypes`、`subprocess`、`reg.exe`、`sc.exe`、`netsh`、`tkinter`、`threading` 等核心模块的使用。

### 六大模块

| 模块 | 禁用 (DISABLE) | 启用 (ENABLE) |
|------|---------------|--------------|
| **Windows 更新** | 恢复默认暂停上限（35 天） | 延长暂停至 25000 天（~27 年） |
| **安全中心** | 四层防线彻底禁用 Defender | 一键完整恢复 |
| **Win11 右键菜单** | 切回 Win10 经典完整菜单 | 恢复 Win11 简洁菜单 |
| **防火墙** | 关闭三配置文件 | 打开三配置文件（netsh 即时生效） |
| **程序主题** | 暗色（Catppuccin Mocha） | 亮色（Catppuccin Latte） |
| **二次元友好模式** | 隐藏壁纸 | 显示全窗口壁纸（暗色/亮色自动换图） |

### 安全中心：四层防线详解

Win11 24H2 中微软大幅强化了 Defender 的自保护机制，传统的 `DisableAntiSpyware` 注册表键已被废除。本工具参考了 TairikuOokami/defender-remover 等开源方案，采用四层策略：

1. **注册表策略层** — `DisableAntiVirus` + `DisableRealtimeMonitoring` + 云防护/通知关闭
2. **服务层** — 停止所有 Defender 相关服务并设 `Start=4`（禁止启动）
3. **驱动层** — `WdBoot` / `WdFilter` / `WdNisDrv` 驱动级禁用
4. **计划任务层** — 禁用缓存维护/清理/扫描/验证四个定时任务

恢复时完整清理策略键、恢复服务为自动启动、恢复驱动默认值、启用计划任务并刷新组策略。

### 功能亮点

- 🔄 **中英双语切换** — 底部两个按钮，所有 UI 文字即时切换
- 🎨 **Catppuccin 主题** — 暗色 Mocha + 亮色 Latte，卡片式布局
- 🖼️ **二次元壁纸** — 全窗口 cover 铺满，窗口拉伸时自适缩放
- 📦 **PyInstaller 打包** — `--onedir` 模式，解压即用，无需安装 Python
- 📚 **教学练习包** — `exercise/` 含 8 个 TODO 任务 + 参考答案

### 快速开始

```powershell
# 方式一：源码运行
pip install Pillow
python tweaker.py          # 以管理员身份

# 方式二：打包运行
# 下载 dist_release/tweaker.zip → 解压 → 双击 tweaker.exe
```

### 打包命令

```powershell
pyinstaller --onedir --noconsole ^
  --add-data "huajia.jpg;." ^
  --add-data "heihua.png;." ^
  --add-data "chino.ico;." ^
  --icon=chino.ico -y tweaker.py
```

### 项目结构

```
├── tweaker.py              # 主程序
├── exercise/               # 教学练习包
│   ├── tweaker_student.py  # 学生版 — 8 个 TODO 留空
│   ├── tweaker_answer.py   # 参考答案 — 完整可运行
│   └── README.md           # 练习说明
├── huajia.jpg              # 亮色壁纸
├── heihua.png              # 暗色壁纸
├── chino.ico               # 窗口图标
├── README.md               # 本文件
└── 打包命令.txt
```

### 注意事项

- ⚠️ 需要**管理员权限**运行
- ⚠️ 部分修改需重启后完全生效
- ⚠️ 禁用安全中心后系统将不再受 Defender 保护，建议仅在对操作后果有充分了解时使用

---

<a name="english"></a>

## 🇬🇧 English

### Overview

System Tweaker v4.2 is a Windows 11 system tweaking tool built with Python + Tkinter. It wraps low-level operations — registry manipulation, service management, driver control — into simple one-click toggles with a fully bilingual GUI. It also doubles as a **Python teaching exercise pack**; the `exercise/` directory contains 8 scaffolded TODO tasks for students plus a complete answer key.

### Six Modules

| Module | DISABLE | ENABLE |
|--------|---------|--------|
| **Windows Update** | Restore default pause (35 days) | Extend pause to ~27 years |
| **Security Center** | 4-layer defense disables Defender entirely | One-click full restore |
| **Win11 Context Menu** | Switch to classic Win10 full menu | Restore Win11 compact menu |
| **Firewall** | Turn off all 3 profiles | Turn on all 3 profiles (netsh instant) |
| **App Theme** | Dark (Catppuccin Mocha) | Light (Catppuccin Latte) |
| **Anime Mode** | Hide wallpaper | Show full-window wallpaper |

### Security Center: 4-Layer Detail

Microsoft significantly hardened Defender's self-protection in Win11 24H2 — the traditional `DisableAntiSpyware` registry key is now defunct. This tool draws on community solutions (TairikuOokami/defender-remover) to apply a 4-layer strategy:

1. **Registry Policy** — `DisableAntiVirus` + `DisableRealtimeMonitoring` + cloud protection & notification blocks
2. **Service Layer** — Stop all Defender services and set `Start=4` (prevent startup)
3. **Driver Layer** — Disable `WdBoot` / `WdFilter` / `WdNisDrv` at the kernel level
4. **Scheduled Tasks** — Disable cache maintenance, cleanup, scan, and verification tasks

Restoration fully cleans policy trees, resets services to auto, restores driver defaults, re-enables tasks, and refreshes group policy.

### Highlights

- 🔄 **Bilingual UI** — Chinese ↔ English toggle with instant text switching
- 🎨 **Catppuccin Themes** — Dark Mocha + Light Latte with card-based layout
- 🖼️ **Anime Wallpaper** — Full-window cover-fit with live resize adaption
- 📦 **PyInstaller Ready** — `--onedir` build, extract-and-run, no Python required
- 📚 **Exercise Pack** — 8 TODO tasks + answer key in `exercise/`

### Quick Start

```powershell
# Option 1: Run from source
pip install Pillow
python tweaker.py          # Run as Administrator

# Option 2: Run pre-built
# Download dist_release/tweaker.zip → extract → double-click tweaker.exe
```

### Build

```powershell
pyinstaller --onedir --noconsole ^
  --add-data "huajia.jpg;." ^
  --add-data "heihua.png;." ^
  --add-data "chino.ico;." ^
  --icon=chino.ico -y tweaker.py
```

### Project Structure

```
├── tweaker.py              # Main program
├── exercise/               # Student exercise pack
│   ├── tweaker_student.py  # Student version — 8 TODO tasks
│   ├── tweaker_answer.py   # Answer key — full runnable
│   └── README.md           # Exercise guide
├── huajia.jpg              # Light wallpaper
├── heihua.png              # Dark wallpaper
├── chino.ico               # App icon
├── README.md               # This file
└── 打包命令.txt             # Build notes (Chinese)
```

### Notes

- ⚠️ **Administrator privileges** required
- ⚠️ Some changes take effect after a system restart
- ⚠️ Disabling the Security Center removes Defender protection — use with understanding

---

### Star History 💫

If you find this useful, consider giving it a ⭐ on GitHub!

---

[⬆ 回到顶部 / Back to top](#system-tweaker-v42-)
