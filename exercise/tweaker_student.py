"""
System Tweaker v4.2 — 学生练习版
 四层防线：策略 + 服务 + 驱动 + 计划任务
 双语切换 · 二次元壁纸 · 暗色/亮色主题
 需管理员权限 | Python 3.12+
"""
import os, sys, subprocess, ctypes, threading, time

# ═══════════════════════════════════════════════════════════
# 任务 0：自动提权 (Admin Elevation)
# 提示: ctypes.windll.shell32.IsUserAnAdmin() 检测权限
#       不是管理员 → ShellExecuteW("runas") 重启自己 → sys.exit()
# ═══════════════════════════════════════════════════════════

# TODO: 写 is_admin() 函数（~3行）
#   def is_admin():
#       try: return ctypes.windll.shell32.IsUserAnAdmin()
#       except: return False


# TODO: 如果不是管理员 → 提权重启（~5行）
#   if not is_admin():
#       ctypes.windll.shell32.ShellExecuteW(
#           None, "runas", sys.executable,
#           f'"{os.path.abspath(__file__)}"',
#           os.path.dirname(os.path.abspath(__file__)),
#           1)
#       sys.exit()


import tkinter as tk
from tkinter import ttk, messagebox

RUNNING = False

# ═══════════════════════════════════════════════════════════
# 任务 1：_run() 静默执行命令行
# 提示: subprocess.run(cmd, shell=True, stdout=DEVNULL, stderr=DEVNULL)
# ═══════════════════════════════════════════════════════════

# TODO: 实现 _run(cmd, silent=True)
#   def _run(cmd, silent=True):
#       dev = subprocess.DEVNULL if silent else None
#       return subprocess.run(cmd, shell=True, stdout=dev, stderr=dev)


# ═══════════════════════════════════════════════════════════
# 任务 2：注册表操作 reg_set / reg_del
# 提示: f'reg add "{path}" /v {name} /t REG_{reg_type.upper()} /d {value} /f'
# ═══════════════════════════════════════════════════════════

# TODO: 实现 reg_set(path, name, value, reg_type="dword")
#   def reg_set(path, name, value, reg_type="dword"):
#       _run(f'reg add "{path}" /v {name} /t REG_{reg_type.upper()} /d {value} /f')


# TODO: 实现 reg_del(path, name="")
#   def reg_del(path, name=""):
#       flag = f'/v {name}' if name else '/ve'
#       _run(f'reg delete "{path}" {flag} /f')


# ═══════════════════════════════════════════════════════════
# 任务 3：服务管理 svc_set / svc_stop
# 提示: sc config {name} start= {action}（注意等号后面有空格！）
# ═══════════════════════════════════════════════════════════

# TODO: 实现 svc_set(name, action) — auto / demand / disabled
#   def svc_set(name, action):
#       _run(f'sc config {name} start= {action}')


# TODO: 实现 svc_stop(name)
#   def svc_stop(name):
#       _run(f'sc stop {name}')


# ═══════════════════════════════════════════════════════════
# 任务 4：计划任务管理 task_set
# 提示: schtasks /change /tn "任务名" /enable 或 /disable
# ═══════════════════════════════════════════════════════════

# TODO: 实现 task_set(name, action) — enable / disable
#   def task_set(name, action):
#       _run(f'schtasks /change /tn "{name}" /{action}')


# ═══════════════════════════════════════════════════════════
# 任务 5：Windows Update 绕路策略
# 提示: Win11 24H2 锁定 reg_del 操作 → 用 reg_set 改写值代替删除
#       pause_days=35 恢复默认 | pause_days=25000 延长至约 27 年
# ═══════════════════════════════════════════════════════════

UPDATE_PAUSE_PATH = r"HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"

# TODO: 实现 disable_update() — 恢复默认（设回 35 天）
#   def disable_update():
#       reg_set(UPDATE_PAUSE_PATH, "FlightSettingsMaxPauseDays", 35)
#       return True


# TODO: 实现 enable_update() — 延长暂停（设 25000 天）
#   def enable_update():
#       reg_set(UPDATE_PAUSE_PATH, "FlightSettingsMaxPauseDays", 25000)
#       return True


# ═══════════════════════════════════════════════════════════
# 任务 6：Windows Defender — 四层防线  (★ 多步任务)
# 提示: 策略键 → 服务停止+Start=4 → 驱动Start=4 → 任务禁用
#       DisableAntiSpyware / DisableAntiVirus / Real-Time Protection 子键
#       驱动: WdBoot / WdFilter / WdNisDrv
#       服务: WinDefend / WdNisSvc / SecurityHealthService / wscsvc
#             WdFilter / SgrmBroker / MpKslDrv / MDCoreSvc
#       恢复: reg delete 清策略 → reg del Start 键 → svc_set auto → task_set enable
# ═══════════════════════════════════════════════════════════

DEF_BASE = r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender"
DEF_SERVICES = ["WinDefend", "WdNisSvc", "SecurityHealthService",
                "wscsvc", "WdFilter", "SgrmBroker", "MpKslDrv", "MDCoreSvc"]
DEF_DRIVERS = ["WdBoot", "WdFilter", "WdNisDrv"]
DEF_TASKS = [
    r"Microsoft\Windows\Windows Defender\Windows Defender Cache Maintenance",
    r"Microsoft\Windows\Windows Defender\Windows Defender Cleanup",
    r"Microsoft\Windows\Windows Defender\Windows Defender Scheduled Scan",
    r"Microsoft\Windows\Windows Defender\Windows Defender Verification",
]

# TODO: 实现 disable_defender()
#   1. 关 Tamper Protection: reg_set Features/TamperProtection=0
#   2. 注册表策略: DisableAntiSpyware=1, DisableAntiVirus=1
#      实时防护子键: DisableRealtimeMonitoring=1, DisableBehaviorMonitoring=1 等
#      云防护: DisableBlockAtFirstSeen=1, SpynetReporting=0
#      通知: DisableNotifications=1
#   3. for svc in DEF_SERVICES: svc_stop(svc); svc_set(svc, "disabled")
#      reg_set Services/{svc} Start=4 (24H2关键!)
#   4. for drv in DEF_DRIVERS: reg_set Services/{drv} Start=4
#   5. for task in DEF_TASKS: task_set(task, "disable")
#   Returns True


# TODO: 实现 enable_defender()
#   1. reg delete "{DEF_BASE}" /f (+ Security Center 策略树)
#   2. 恢复 Tamper: reg_set Features/TamperProtection=5
#   3. for svc in DEF_SERVICES: reg del Start; svc_set(svc, "auto")
#   4. for drv in DEF_DRIVERS: reg del Start
#   5. for task in DEF_TASKS: task_set(task, "enable")
#   6. gpupdate /force
#   Returns True


# ═══════════════════════════════════════════════════════════
# 任务 7：Win11 右键菜单 + 防火墙 (★ 综合题)
# 提示: CLSID {86ca1aa0-34aa-4e8b-a509-50c905bae2a2} 的 InprocServer32
#       防火墙: 三配置文件 DomainProfile/PrivateProfile/PublicProfile
#       netsh advfirewall 即时生效
# ═══════════════════════════════════════════════════════════

CTX_KEY = r"HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
CTX_SUB = f"{CTX_KEY}\\InprocServer32"

# TODO: 实现 restart_explorer()
#   def restart_explorer():
#       _run('taskkill /f /im explorer.exe')
#       time.sleep(1)
#       _run('explorer.exe')


# TODO: 实现 disable_win11_context() — 恢复经典菜单
#   reg_set(CTX_SUB, "", "", "sz") 再 threading.Thread 启动 restart_explorer


# TODO: 实现 enable_win11_context() — 恢复 Win11 简洁菜单
#   reg_del(CTX_KEY) 再重启 explorer


FW_BASE = r"HKLM\SOFTWARE\Policies\Microsoft\WindowsFirewall"
FW_PROFILES = ["DomainProfile", "PrivateProfile", "PublicProfile"]

# TODO: 实现 disable_firewall() — 策略 + netsh 即时关闭
#   for profile in FW_PROFILES:
#       reg_set(FW_BASE/{profile}, EnableFirewall=0)
#       netsh advfirewall set {short}profile state off


# TODO: 实现 enable_firewall() — 删策略键 + 设回 1 + netsh on
#   for profile in FW_PROFILES:
#       先 reg del EnableFirewall
#       再 reg_set EnableFirewall=1
#       netsh advfirewall set {short}profile state on


# ═══════════════════════════════════════════════════════════
# 任务 8：GUI 界面 —— 中英双语 + 暗色/亮色主题 + 二次元壁纸 (★★ 综合)
# 提示: make_card 工厂方法、语言字典、主题切换、壁纸 cover 铺满
# ═══════════════════════════════════════════════════════════

L = {
    "zh": {
        "title": "系统调教工具  v4.2",
        "subtitle": "每个模块独立开关 · ENBALE即恢复 · 需管理员权限",
        "status_ready": "就绪",
        "status_running": "操作进行中，请稍候...",
        "bottom_hint": "操作完成后建议重启系统以完全生效",
        "btn_disable": "DISABLE", "btn_enable": "ENABLE",
        "card1_title": "Windows 更新",
        "card1_desc": "暂停延长至27年·仅一条注册表绕路\nENABLE即恢复",
        "card2_title": "Windows 安全中心",
        "card2_desc": "四层防线：策略+服务+驱动+任务\nENABLE一键恢复",
        "card3_title": "Win11 右键菜单",
        "card3_desc": "DISABLE=经典菜单·ENABLE=简洁菜单",
        "card4_title": "Windows 防火墙",
        "card4_desc": "三配置文件·策略+netsh即时生效\nDISABLE=关  ENABLE=开",
        "card5_title": "程序主题 — 暗色/亮色",
        "card5_desc": "DISABLE=暗色·ENABLE=亮色\nCatppuccin 配色",
        "card6_title": "二次元友好模式",
        "card6_desc": "ENABLE=显示壁纸✨·DISABLE=隐藏",
    },
    "en": {
        "title": "System Tweaker  v4.2",
        "subtitle": "Independent modules · Admin required",
        "status_ready": "Ready",
        "status_running": "Operation in progress...",
        "bottom_hint": "A restart is recommended for full effect",
        "btn_disable": "DISABLE", "btn_enable": "ENABLE",
        "card1_title": "Windows Update",
        "card1_desc": "Extend pause to 27 years·Single registry\nENABLE to restore",
        "card2_title": "Windows Security Center",
        "card2_desc": "4 layers: Policies+Services+Drivers+Tasks\nENABLE to restore",
        "card3_title": "Win11 Right-Click Menu",
        "card3_desc": "DISABLE=Classic·ENABLE=Compact",
        "card4_title": "Windows Firewall",
        "card4_desc": "3 profiles: Domain/Private/Public\nDISABLE=Off  ENABLE=On",
        "card5_title": "App Theme — Dark/Light",
        "card5_desc": "DISABLE=Dark·ENABLE=Light\nCatppuccin palette",
        "card6_title": "Anime-Friendly Mode",
        "card6_desc": "ENABLE=Show wallpaper✨·DISABLE=Hide",
    },
}

# Catppuccin 颜色方案
THEMES = {
    "dark": {"bg":"#1e1e2e","surf_bg":"#313244","text_fg":"#cdd6f4","accent":"#cba6f7","dim":"#a6adc8"},
    "light":{"bg":"#eff1f5","surf_bg":"#ccd0da","text_fg":"#4c4f69","accent":"#8839ef","dim":"#5c5f77"},
}

class TweakerApp:
    def __init__(self, root):
        self.root = root
        self.lang = "zh"
        self.theme_name = "dark"
        root.title("System Tweaker v4.2")
        root.geometry("660x820")
        root.resizable(True, True)
        root.minsize(660, 700)
        root.configure(bg=THEMES["dark"]["bg"])

        # ── 标题 ──
        # TODO: 实现标题区（约8行）
        #   hdr = tk.Frame(root, bg=...)
        #   tk.Label(hdr, text=self.T("title"), font=...).pack()
        #   tk.Label(hdr, text=self.T("subtitle"), font=...).pack()

        # ── 6 张卡片 ──
        # TODO: 调用 self.make_card(title_key, desc_key, disable_fn, enable_fn)
        #   self.make_card("card1_title", "card1_desc", disable_update, enable_update)
        #   ... (共 6 张)

        # ── 状态栏 ──
        # TODO: 状态栏 "就绪" + 底部提示

        # ── 语言切换按钮 ──
        # TODO: 两个 Button: "中文" 和 "English"

    # ── 辅助方法 ──
    # TODO: 实现 T(key) — 返回 L[self.lang][key]
    # TODO: 实现 set_lang(lang) — 切换所有文字标签
    # TODO: 实现 apply_theme(name) — 切换暗色/亮色
    # TODO: 实现 make_card(title_key, desc_key, disable_fn, enable_fn)
    # TODO: 实现 run_op(fn, title) + _run(fn, title) + set_status(text, color)

# ── Main ──
if __name__ == "__main__":
    root = tk.Tk()
    app = TweakerApp(root)
    root.mainloop()
