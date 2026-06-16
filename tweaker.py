"""
System Tweaker v4.2
 Windows Update: 绕路策略 — reg_set 改写值突破 Win11 24H2 锁
 Defender     : 四层防线 — 注册表 + 服务 + 计划任务 + 防篡改
 Win11 Menu  : 经典完整右键菜单开关
 Firewall    : 三个配置文件防火墙开关
 Theme       : 程序内暗色 / 亮色主题一键切换（Catppuccin 风格）
 Anime Mode  : 二次元友好模式 — chino 装饰图开关
 Requires: Admin | Python 3.12+
"""
import os, sys, subprocess, ctypes, threading, time

# ── Auto-elevate ──────────────────────────────────────────
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable,
        f'"{os.path.abspath(__file__)}"',
        os.path.dirname(os.path.abspath(__file__)),  # 工作目录
        1)
    sys.exit()

import tkinter as tk
from tkinter import ttk, messagebox

RUNNING = False
_RUNNING_LOCK = threading.Lock()

# ── Shell helpers ─────────────────────────────────────────
def _run(cmd, silent=True):
    return subprocess.run(cmd, shell=True,
        stdout=subprocess.DEVNULL if silent else None,
        stderr=subprocess.DEVNULL if silent else None)

def reg_set(path, name, value, reg_type="dword"):
    t = f"REG_{reg_type.upper()}"
    if name:
        _run(f'reg add "{path}" /v {name} /t {t} /d {value} /f')
    else:
        _run(f'reg add "{path}" /ve /f')

def svc_set(name, action):
    """action = auto | demand | disabled（映射 SC 命令 start= 参数）"""
    _run(f'sc config {name} start= {action}')

def svc_stop(name): _run(f'sc stop {name}')
def svc_start(name): _run(f'sc start {name}')

def task_set(name, action):
    """action = disable | enable"""
    _run(f'schtasks /change /tn "{name}" /{action}')

def restart_explorer():
    _run('taskkill /f /im explorer.exe')
    time.sleep(1)
    subprocess.Popen('explorer.exe', shell=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ═══════════════════════════════════════════════════════════
#  MODULE 1: Windows Update
# ═══════════════════════════════════════════════════════════

UPDATE_REG_BASE = r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
UPDATE_PAUSE_PATH = r"HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"
UPDATE_SERVICES = ["wuauserv", "UsoSvc", "WaaSMedicSvc", "BITS"]
UPDATE_TASKS = [
    r"Microsoft\Windows\WindowsUpdate\Scheduled Start",
    r"Microsoft\Windows\WindowsUpdate\sih",
    r"Microsoft\Windows\WindowsUpdate\sihboot",
    r"Microsoft\Windows\WindowsUpdate\Automatic App Update",
    r"Microsoft\Windows\UpdateOrchestrator\Schedule Scan",
    r"Microsoft\Windows\UpdateOrchestrator\Schedule Scan Static Task",
    r"Microsoft\Windows\UpdateOrchestrator\Refresh Settings",
    r"Microsoft\Windows\UpdateOrchestrator\USO_UxBroker",
]

def disable_update():
    """延长暂停上限至 25000 天（约 68 年），实质禁用自动更新"""
    reg_set(UPDATE_PAUSE_PATH, "FlightSettingsMaxPauseDays", 25000)
    return True

def enable_update():
    """恢复默认暂停上限 5 周（35 天）"""
    reg_set(UPDATE_PAUSE_PATH, "FlightSettingsMaxPauseDays", 35)
    return True

# ═══════════════════════════════════════════════════════════
#  MODULE 2: Windows Defender & Security Center
#  基于社区开源方案 (TairikuOokami/defender-remover) 优化
#  关键：24H2 需要驱动级禁用 WdBoot/WdFilter + 安全中心关闭
# ═══════════════════════════════════════════════════════════

DEF_BASE = r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender"
DEF_SERVICES = [
    "WinDefend", "WdNisSvc", "SecurityHealthService",
    "wscsvc", "WdFilter", "SgrmBroker", "MpKslDrv",
    "MDCoreSvc",  # 24H2 新增核心服务
]
DEF_DRIVERS = ["WdBoot", "WdFilter", "WdNisDrv"]  # 驱动级，需设 Start=4
DEF_TASKS = [
    r"Microsoft\Windows\Windows Defender\Windows Defender Cache Maintenance",
    r"Microsoft\Windows\Windows Defender\Windows Defender Cleanup",
    r"Microsoft\Windows\Windows Defender\Windows Defender Scheduled Scan",
    r"Microsoft\Windows\Windows Defender\Windows Defender Verification",
]

def disable_defender():
    """彻底禁用 Defender — 四层：注册表策略 + 服务 + 驱动 + 计划任务"""
    # ── 第零层：关闭 Tamper Protection ──
    reg_set(r"HKLM\SOFTWARE\Microsoft\Windows Defender\Features", "TamperProtection", 0)
    reg_set(r"HKLM\SOFTWARE\Microsoft\Windows Defender\Features", "MpTamperProtectionSource", 0)

    # ── 第一层：注册表策略（24H2 兼容）──
    reg_set(DEF_BASE, "DisableAntiSpyware", 1)
    reg_set(DEF_BASE, "DisableAntiVirus", 1)
    reg_set(DEF_BASE, "DisableRoutinelyTakingAction", 1)
    reg_set(DEF_BASE, "AllowFastServiceStartup", 0)
    reg_set(DEF_BASE, "DisableLocalAdminMerge", 1)
    # 实时防护子键
    rtp = f"{DEF_BASE}\\Real-Time Protection"
    reg_set(rtp, "DisableRealtimeMonitoring", 1)
    reg_set(rtp, "DisableBehaviorMonitoring", 1)
    reg_set(rtp, "DisableOnAccessProtection", 1)
    reg_set(rtp, "DisableScanOnRealtimeEnable", 1)
    reg_set(rtp, "DisableIOAVProtection", 1)
    # 云防护/样本提交
    reg_set(f"{DEF_BASE}\\Spynet", "DisableBlockAtFirstSeen", 1)
    reg_set(f"{DEF_BASE}\\Spynet", "SpynetReporting", 0)
    reg_set(f"{DEF_BASE}\\Spynet", "SubmitSamplesConsent", 2)
    # 通知
    scn = r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender Security Center\Notifications"
    reg_set(scn, "DisableNotifications", 1)
    reg_set(scn, "DisableEnhancedNotifications", 1)

    # ── 第二层：服务停止 + 设为禁用 ──
    for svc in DEF_SERVICES:
        svc_stop(svc)
        svc_set(svc, "disabled")
        # 直写注册表 Start=4 防反弹（24H2 关键）
        reg_set(f"HKLM\\SYSTEM\\CurrentControlSet\\Services\\{svc}", "Start", 4)

    # ── 第三层：驱动级禁用 ──
    for drv in DEF_DRIVERS:
        reg_set(f"HKLM\\SYSTEM\\CurrentControlSet\\Services\\{drv}", "Start", 4)

    # ── 第四层：计划任务 ──
    for task in DEF_TASKS:
        task_set(task, "disable")

    # ── 额外：隐藏安全中心托盘图标 ──
    reg_set(r"HKLM\SOFTWARE\Microsoft\Windows Defender Security Center", "DisableTrayIcon", 1)

    # ── 移除自启托盘进程（SecurityHealthSystray.exe）──
    SYSTRAY_KEY = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
    _run(f'reg add "{SYSTRAY_KEY}" /v SecurityHealth.DisableBg /t REG_SZ /d "SecurityHealth" /f')
    _run(f'reg delete "{SYSTRAY_KEY}" /v SecurityHealth /f')

    return True


def enable_defender():
    """完整恢复 Defender 到默认状态"""
    # 删除所有策略键
    _run(f'reg delete "{DEF_BASE}" /f')
    _run(r'reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender Security Center" /f')
    _run(r'reg delete "HKLM\SOFTWARE\Microsoft\Windows Defender Security Center" /v DisableTrayIcon /f')

    # 恢复 Tamper Protection
    reg_set(r"HKLM\SOFTWARE\Microsoft\Windows Defender\Features", "TamperProtection", 5)
    _run(r'reg delete "HKLM\SOFTWARE\Microsoft\Windows Defender\Features" /v MpTamperProtectionSource /f')

    # 恢复所有服务为自动启动
    for svc in DEF_SERVICES:
        _run(f'reg delete "HKLM\\SYSTEM\\CurrentControlSet\\Services\\{svc}" /v Start /f')
        svc_set(svc, "auto")

    # 恢复驱动为默认
    for drv in DEF_DRIVERS:
        _run(f'reg delete "HKLM\\SYSTEM\\CurrentControlSet\\Services\\{drv}" /v Start /f')

    # 恢复计划任务
    for task in DEF_TASKS:
        task_set(task, "enable")

    # 恢复自启托盘进程
    SYSTRAY_KEY = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
    _run(f'reg add "{SYSTRAY_KEY}" /v SecurityHealth /t REG_SZ /d "C:\\Windows\\System32\\SecurityHealthSystray.exe" /f')
    _run(f'reg delete "{SYSTRAY_KEY}" /v SecurityHealth.DisableBg /f')

    # 刷新组策略
    _run('gpupdate /force')
    return True

# ═══════════════════════════════════════════════════════════
#  MODULE 3: Win11 Right-Click Menu (Classic)
# ═══════════════════════════════════════════════════════════

CTX_KEY = r"HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
CTX_SUB = f"{CTX_KEY}\\InprocServer32"

def disable_win11_context():
    _run(f'reg add "{CTX_SUB}" /ve /f')
    threading.Thread(target=restart_explorer, daemon=True).start()
    return True

def enable_win11_context():
    _run(f'reg delete "{CTX_KEY}" /f')
    threading.Thread(target=restart_explorer, daemon=True).start()
    return True

# ═══════════════════════════════════════════════════════════
#  MODULE 4: Windows Firewall
# ═══════════════════════════════════════════════════════════

FW_BASE = r"HKLM\SOFTWARE\Policies\Microsoft\WindowsFirewall"
FW_PROFILES = ["DomainProfile", "PrivateProfile", "PublicProfile"]

def disable_firewall():
    """关闭三配置文件防火墙 — 策略注册表 + netsh 即时生效"""
    for profile in FW_PROFILES:
        reg_set(f"{FW_BASE}\\{profile}", "EnableFirewall", 0)
        _run(f'netsh advfirewall set {profile.lower().replace("profile","")}profile state off')
    return True

def enable_firewall():
    """开启防火墙 — 删策略键值 + 设默认值 1 + netsh"""
    for profile in FW_PROFILES:
        _run(f'reg delete "{FW_BASE}\\{profile}" /v EnableFirewall /f')
        # 删完策略键后，设回默认开启
        reg_set(f"{FW_BASE}\\{profile}", "EnableFirewall", 1)
        short = profile.lower().replace("profile", "")
        _run(f'netsh advfirewall set {short}profile state on')
    return True

# ═══════════════════════════════════════════════════════════
#  GUI — Theme & Widget System
# ═══════════════════════════════════════════════════════════

# Catppuccin Mocha Dark  /  Catppuccin Latte Light
THEMES = {
    "dark": {
        "bg": "#1e1e2e", "surf_bg": "#313244", "ovl_bg": "#45475a",
        "text_fg": "#cdd6f4", "dim": "#a6adc8", "accent": "#cba6f7",
        "subtle": "#a6adc8",
    },
    "light": {
        "bg": "#eff1f5", "surf_bg": "#ccd0da", "ovl_bg": "#bcc0cc",
        "text_fg": "#4c4f69", "dim": "#5c5f77", "accent": "#8839ef",
        "subtle": "#6c6f85",
    },
}

# ═══════════════════════════════════════════════════════════
#  中英双语字典
# ═══════════════════════════════════════════════════════════
L = {
    "zh": {
        "title": "系统调教工具  v4.2",
        "subtitle": "每个模块独立开关 · 点ENABLE即可恢复 · 需管理员权限",
        "card1_title": "Windows 更新",
        "card1_desc": "暂停上限延长至27年 · 仅写一条注册表\n不碰服务/策略/计划任务 · ENABLE即恢复",
        "card2_title": "Windows 安全中心",
        "card2_desc": "四层防线：策略+服务+驱动+计划任务\n保留防火墙  |  ENABLE一键恢复",
        "card3_title": "Win11 右键菜单",
        "card3_desc": "DISABLE = 恢复 Win10 经典完整菜单\nENABLE  = 回到 Win11 简洁菜单",
        "card4_title": "Windows 防火墙",
        "card4_desc": "关闭域/专用/公用三配置文件防火墙\nDISABLE=关  ENABLE=开",
        "card5_title": "程序主题 — 暗色 / 亮色",
        "card5_desc": "DISABLE = 暗色（Catppuccin Mocha）\nENABLE  = 亮色（Catppuccin Latte）",
        "card6_title": "二次元友好模式",
        "card6_desc": "ENABLE  = 显示 huajia 装饰图  ✨\nDISABLE = 隐藏装饰",
        "status_ready": "就绪",
        "status_running": "操作进行中，请稍候...",
        "bottom_hint": "操作完成后建议重启系统以完全生效",
        "btn_disable": "DISABLE",
        "btn_enable": "ENABLE",
        "running_suffix": "禁用中...",
        "done_suffix": "已完成",
        "fail_suffix": "失败",
    },
    "en": {
        "title": "System Tweaker  v4.2",
        "subtitle": "Independent module toggles · Admin required",
        "card1_title": "Windows Update",
        "card1_desc": "Extend pause limit to 27 years · Single registry write\nNo service/policy/task changes · ENABLE to restore",
        "card2_title": "Windows Security Center",
        "card2_desc": "4-layer defense: Policy + Service + Driver + Tasks\nKeeps Firewall  |  ENABLE to restore",
        "card3_title": "Win11 Right-Click Menu",
        "card3_desc": "DISABLE = Restore Win10 classic full menu\nENABLE  = Use Win11 compact menu",
        "card4_title": "Windows Firewall",
        "card4_desc": "Turn off Domain/Private/Public firewall profiles\nDISABLE=Off  ENABLE=On",
        "card5_title": "App Theme — Dark / Light",
        "card5_desc": "DISABLE = Dark (Catppuccin Mocha)\nENABLE  = Light (Catppuccin Latte)",
        "card6_title": "Anime-Friendly Mode",
        "card6_desc": "ENABLE  = Show huajia wallpaper  ✨\nDISABLE = Hide wallpaper",
        "status_ready": "Ready",
        "status_running": "Operation in progress, please wait...",
        "bottom_hint": "A system restart is recommended for full effect",
        "btn_disable": "DISABLE",
        "btn_enable": "ENABLE",
        "running_suffix": "disabling...",
        "done_suffix": "Done",
        "fail_suffix": "Failed",
    },
}

class TweakerApp:
    def __init__(self, root):
        self.root = root
        self.theme_name = "dark"
        self.c = THEMES["dark"].copy()
        self.anime_on = False
        self.lang = "zh"  # 当前语言: zh / en
        self._text_widgets = []  # (widget, key) 用于语言切换
        self._tw = []          # (widget, attr, dark_val, light_val)
        self.anime_label = None  # 全窗口背景 label
        self._chino_photo = None
        self.card_frames = []  # card outer frames for surf_bg swap

        # ── 预加载原图（不缩放，运行时按窗口动态计算）──
        self._chino_raw = None   # 亮色壁纸 (huajia.jpg)
        self._heihua_raw = None  # 暗色壁纸 (heihua.png)
        try:
            from PIL import Image, ImageTk
            self.Image = Image
            self.ImageTk = ImageTk
            # 兼容 PyInstaller 打包和直接运行
            if getattr(sys, 'frozen', False):
                base = sys._MEIPASS
            else:
                base = os.path.dirname(os.path.abspath(__file__))
            src_light = os.path.join(base, 'huajia.jpg')
            src_dark = os.path.join(base, 'heihua.png')
            if os.path.exists(src_light):
                self._chino_raw = Image.open(src_light)
            else:
                print("[tweaker] huajia.jpg not found")
            if os.path.exists(src_dark):
                self._heihua_raw = Image.open(src_dark)
            else:
                print("[tweaker] heihua.png not found")
        except Exception as e:
            print(f"[tweaker] preload image: {e}")

        root.title(self.T("title"))
        root.geometry("660x900")
        root.resizable(True, True)
        root.minsize(660, 760)
        root.configure(bg=self.c["bg"])
        self._add_tw(root, "bg", THEMES["dark"]["bg"], THEMES["light"]["bg"])

        # Header
        hdr = tk.Frame(root, bg=self.c["bg"])
        hdr.pack(pady=(14, 4))
        self._add_tw(hdr, "bg", THEMES["dark"]["bg"], THEMES["light"]["bg"])

        self.head_lbl = tk.Label(hdr, text=self.T("title"),
                                  font=("Microsoft YaHei UI", 14, "bold"))
        self.t(self.head_lbl, "fg", "accent")
        self.t(self.head_lbl, "bg", "bg")
        self._bind_text(self.head_lbl, "title")
        self.head_lbl.pack()

        self.sub_lbl = tk.Label(hdr, text=self.T("subtitle"),
                                 font=("Microsoft YaHei UI", 8))
        self.t(self.sub_lbl, "fg", "ovl_bg")
        self.t(self.sub_lbl, "bg", "bg")
        self._bind_text(self.sub_lbl, "subtitle")
        self.sub_lbl.pack()

        # Section 1-4: system tweaks
        self.make_card("card1_title", "card1_desc",
                       disable_update, enable_update)
        self.make_card("card2_title", "card2_desc",
                       disable_defender, enable_defender)
        self.make_card("card3_title", "card3_desc",
                       disable_win11_context, enable_win11_context)
        self.make_card("card4_title", "card4_desc",
                       disable_firewall, enable_firewall)

        # Section 5: App Theme Toggle
        self.make_card("card5_title", "card5_desc",
                       self._disable_theme, self._enable_theme)

        # Section 6: Anime-Friendly Mode
        self.make_card("card6_title", "card6_desc",
                       self._disable_anime, self._enable_anime)

        # ── 全窗口背景图（place 在 root 底层）──
        self.bg_label = tk.Label(root, bg=self.c["bg"], bd=0)
        # 默认隐藏，由 _set_anime 控制

        # Status bar
        self.status_label = tk.Label(root, text=self.T("status_ready"),
                                      font=("Microsoft YaHei UI", 9))
        self.t(self.status_label, "fg", "ovl_bg")
        self.t(self.status_label, "bg", "bg")
        self._bind_text(self.status_label, "status_ready")
        self.status_label.pack(side="bottom", pady=(6, 2))

        self.bottom_lbl = tk.Label(root, text=self.T("bottom_hint"),
                                    font=("Microsoft YaHei UI", 8))
        self.t(self.bottom_lbl, "fg", "subtle")
        self.t(self.bottom_lbl, "bg", "bg")
        self._bind_text(self.bottom_lbl, "bottom_hint")
        self.bottom_lbl.pack(side="bottom", pady=(0, 14))

        # ── 语言切换按钮 ──
        lang_frame = tk.Frame(root, bg=self.c["bg"])
        self._add_tw(lang_frame, "bg", THEMES["dark"]["bg"], THEMES["light"]["bg"])
        lang_frame.pack(side="bottom", pady=(0, 8))

        self.btn_zh = tk.Button(lang_frame, text="中文", font=("Microsoft YaHei UI", 9, "bold"),
                                bg="#a6e3a1", fg="#1e1e2e", relief="flat",
                                padx=10, pady=3, cursor="hand2",
                                command=self._switch_zh)
        self.btn_zh.pack(side="left", padx=(0, 4))

        self.btn_en = tk.Button(lang_frame, text="English", font=("Segoe UI", 9, "bold"),
                                bg="#89b4fa", fg="#1e1e2e", relief="flat",
                                padx=10, pady=3, cursor="hand2",
                                command=self._switch_en)
        self.btn_en.pack(side="left")

        # 强制刷新主题：解决 Tkinter 在 Windows 上初始渲染时的白色闪烁
        root.update_idletasks()
        self._apply_theme("light")  # 默认亮色主题
        self._set_lang("zh")  # 初始语言高亮
        # ── 默认开启二次元友好模式 ──
        self.root.after(200, lambda: self._set_anime(True))

    # ── Theme helpers ────────────────────────────────────
    def t(self, widget, attr, color_key):
        self._tw.append((widget, attr, THEMES["dark"][color_key], THEMES["light"][color_key]))

    def _add_tw(self, widget, attr, dark_val, light_val):
        self._tw.append((widget, attr, dark_val, light_val))

    def T(self, key):
        """获取当前语言的文字"""
        return L[self.lang].get(key, key)

    def _bind_text(self, widget, key):
        """注册一个需要语言切换的 Label/控件"""
        self._text_widgets.append((widget, key))

    # ── Theme switch ─────────────────────────────────────
    def _disable_theme(self):
        """Switch to dark theme"""
        self._apply_theme("dark")
        return True

    def _enable_theme(self):
        """Switch to light theme"""
        self._apply_theme("light")
        return True

    def _apply_theme(self, name):
        self.theme_name = name
        self.c = THEMES[name].copy()
        for widget, attr, dark_val, light_val in self._tw:
            try:
                widget.configure(**{attr: light_val if name == "light" else dark_val})
            except Exception:
                pass
        # Also update card frames' surf_bg
        surf_d, surf_l = THEMES["dark"]["surf_bg"], THEMES["light"]["surf_bg"]
        for f in self.card_frames:
            try:
                f.configure(bg=surf_l if name == "light" else surf_d)
            except Exception:
                pass
        # ── 二次元模式下切换壁纸 ──
        if self.anime_on:
            self._refresh_bg_image()

    # ── Anime mode ───────────────────────────────────────
    def _disable_anime(self):
        """DISABLE = 隐藏壁纸"""
        return self._set_anime(False)

    def _enable_anime(self):
        """ENABLE = 显示壁纸"""
        return self._set_anime(True)

    def _set_anime(self, show):
        self.root.after(0, self._set_anime_main, show)
        return True

    def _set_anime_main(self, show):
        if show:
            if self._chino_raw is None:
                return
            self.anime_on = True
            self._refresh_bg_image()
            self.root.bind("<Configure>", self._on_resize)
        else:
            self.anime_on = False
            self.root.unbind("<Configure>")
            self.bg_label.place_forget()

    def _on_resize(self, event):
        """窗口尺寸变化时重新缩放背景图"""
        if not self.anime_on:
            return
        # 防抖：延迟 100ms 执行
        if hasattr(self, '_resize_after_id'):
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(100, self._refresh_bg_image)

    def _refresh_bg_image(self):
        """按窗口当前尺寸缩放并铺满背景"""
        if not self.anime_on:
            return
        # 亮色主题 → huajia.jpg，暗色主题 → heihua.png
        raw = self._chino_raw if self.theme_name == "light" else self._heihua_raw
        if raw is None:
            return
        self.root.update_idletasks()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        if win_w < 50 or win_h < 50:
            self.root.after(50, self._refresh_bg_image)
            return

        # 按比例缩放填满窗口（cover 模式，会裁切多余部分）
        scale = max(win_w / raw.width, win_h / raw.height)  # 用 max 保证 cover
        new_w = max(1, int(raw.width * scale))
        new_h = max(1, int(raw.height * scale))
        img = raw.resize((new_w, new_h), self.Image.LANCZOS)

        # 居中裁剪到窗口尺寸
        left = (new_w - win_w) // 2
        top = (new_h - win_h) // 2
        img = img.crop((left, top, left + win_w, top + win_h))

        self._chino_photo = self.ImageTk.PhotoImage(img)
        self.bg_label.configure(image=self._chino_photo)
        # place 铺满整个窗口，放在最底层
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        # 确保背景在最底层
        self.bg_label.lower()
        # 同时把卡片帧提升到背景之上
        for f in self.card_frames:
            f.lift()

    # ── Card builder ─────────────────────────────────────
    def make_card(self, title_key, desc_key, disable_fn, enable_fn):
        frame = tk.Frame(self.root, bg=self.c["surf_bg"], bd=0, highlightthickness=0)
        frame.pack(fill="x", padx=24, pady=6)
        self.card_frames.append(frame)

        inner = tk.Frame(frame, bg=self.c["surf_bg"])
        inner.pack(padx=16, pady=14, fill="x")
        self._add_tw(inner, "bg", THEMES["dark"]["surf_bg"], THEMES["light"]["surf_bg"])

        # Left: title + desc
        left = tk.Frame(inner, bg=self.c["surf_bg"])
        left.pack(side="left", anchor="w")
        self._add_tw(left, "bg", THEMES["dark"]["surf_bg"], THEMES["light"]["surf_bg"])

        title_lbl = tk.Label(left, text=self.T(title_key),
                             font=("Microsoft YaHei UI", 11, "bold"))
        self.t(title_lbl, "fg", "text_fg")
        self.t(title_lbl, "bg", "surf_bg")
        self._bind_text(title_lbl, title_key)
        title_lbl.pack(anchor="w")

        desc_lbl = tk.Label(left, text=self.T(desc_key),
                            font=("Microsoft YaHei UI", 8), justify="left")
        self.t(desc_lbl, "fg", "dim")
        self.t(desc_lbl, "bg", "surf_bg")
        self._bind_text(desc_lbl, desc_key)
        desc_lbl.pack(anchor="w", pady=(4, 0))

        # Right: buttons
        btnf = tk.Frame(inner, bg=self.c["surf_bg"])
        btnf.pack(side="right")
        self._add_tw(btnf, "bg", THEMES["dark"]["surf_bg"], THEMES["light"]["surf_bg"])

        tk.Button(btnf, text=self.T("btn_disable"), font=("Segoe UI", 10, "bold"),
                  bg="#f38ba8", fg="#1e1e2e", activebackground="#e06c7f",
                  relief="flat", padx=16, pady=5, cursor="hand2",
                  command=lambda: self.run_op(disable_fn, self.T(title_key), "disable")).pack(
                  side="left", padx=(0, 6))

        tk.Button(btnf, text=self.T("btn_enable"), font=("Segoe UI", 10, "bold"),
                  bg="#a6e3a1", fg="#1e1e2e", activebackground="#7ec97c",
                  relief="flat", padx=16, pady=5, cursor="hand2",
                  command=lambda: self.run_op(enable_fn, self.T(title_key), "enable")).pack(
                  side="left")

    # ── Operation runner ─────────────────────────────────
    def run_op(self, fn, title, action):
        global RUNNING
        with _RUNNING_LOCK:
            if RUNNING:
                self.set_status(self.T("status_running"), "#f9e2af")
                return
            RUNNING = True
        label = f"{title}: {self.T(action + '_suffix')}"
        self.set_status(label, "#f9e2af")
        threading.Thread(target=self._run, args=(fn, title, action), daemon=True).start()

    def _run(self, fn, title, action):
        global RUNNING
        try:
            ok = fn()
            self.set_status(f"{title}  {self.T('done_suffix')}" if ok
                            else f"{title}  {self.T('fail_suffix')}",
                            "#a6e3a1" if ok else "#f38ba8")
        except Exception as e:
            self.set_status(str(e)[:80], "#f38ba8")
        finally:
            with _RUNNING_LOCK:
                RUNNING = False

    def set_status(self, text, color=None):
        self.root.after(0, lambda: self.status_label.config(
            text=text, fg=color or self.c["ovl_bg"]))

    # ── Language switch ──────────────────────────────────
    def _switch_zh(self):
        self._set_lang("zh")

    def _switch_en(self):
        self._set_lang("en")

    def _set_lang(self, lang):
        self.lang = lang
        self.root.title(self.T("title"))
        # 更新所有注册的文本控件
        for widget, key in self._text_widgets:
            try:
                widget.config(text=self.T(key))
            except Exception:
                pass
        # 高亮当前语言按钮
        self.btn_zh.configure(bg="#a6e3a1" if lang == "zh" else "#d9d9d9")
        self.btn_en.configure(bg="#89b4fa" if lang == "en" else "#d9d9d9")

# ── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TweakerApp(root)
    # 窗口图标（兼容 PyInstaller）
    if getattr(sys, 'frozen', False):
        ico = os.path.join(sys._MEIPASS, 'chino.ico')
    else:
        ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chino.ico')
    if os.path.exists(ico):
        root.iconbitmap(ico)
    root.mainloop()
