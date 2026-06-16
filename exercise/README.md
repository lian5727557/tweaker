# System Tweaker v4.2 — 教学练习包

## 文件说明

| 文件 | 用途 |
|------|------|
| `tweaker_student.py` | 📝 学生练习版 — 8 个 TODO 任务，需填充代码 |
| `tweaker_answer.py`  | 🔒 参考答案 — 精简版，可运行 |
| `png2ico.py`         | 🖼️  ICO 图标生成工具 |

## 教学任务分布（8 个任务）

| 任务 | 内容 | 知识点 | 难度 |
|------|------|--------|------|
| 0 | 自动提权 | `ctypes.IsUserAnAdmin` / `ShellExecuteW` / `sys.exit` | ⭐⭐ |
| 1 | `_run()` 静默执行 | `subprocess.run` / `DEVNULL` | ⭐ |
| 2 | 注册表操作 | `reg.exe` / 类型转换 / f-string | ⭐⭐ |
| 3 | 服务管理 | `sc.exe` / `start=` 语法 | ⭐ |
| 4 | 计划任务 | `schtasks.exe` | ⭐ |
| 5 | Windows Update | 绕路策略—`reg_set` 改写值代替 `reg_del` | ⭐⭐ |
| 6 | Defender 四层防线 | 策略+服务+驱动+任务 / `Start=4` / 完整恢复 | ⭐⭐⭐ |
| 7 | 右键菜单+防火墙 | CLSID / `netsh advfirewall` / `threading` | ⭐⭐ |
| 8 | GUI 双语界面 | `make_card` 工厂 / 语言字典 / 主题切换 | ⭐⭐⭐ |

## v4.2 新增
- 四层 Defender 防线（驱动级 `WdBoot`/`WdFilter`）
- 防火墙 `netsh` 即时生效 + ENABLE 正确恢复
- 中英双语切换按钮
- 二次元壁纸 + 暗色/亮色主题

## 使用方式

1. 学生打开 `tweaker_student.py`
2. 按 TODO 注释和提示完成每个任务
3. 运行 `python tweaker_student.py` 验证（需管理员权限）
4. 对照 `tweaker_answer.py` 检查答案

## 配套课件

`../System_Tweaker_课件.docx` — 完整代码解析与打包教程
