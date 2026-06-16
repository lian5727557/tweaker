from PIL import Image
import sys, os

png = sys.argv[1] if len(sys.argv) > 1 else None
if not png:
    # 自动检测常见图片格式作为输入
    candidates = [f for f in os.listdir(".") if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp"))]
    if not candidates:
        print("用法: python png2ico.py <图片文件>")
        print("当前目录无图片文件")
        sys.exit(1)
    png = candidates[0]
    print(f"自动选择: {png}")
name = os.path.splitext(png)[0]
img = Image.open(png).convert("RGBA")
img.save(f"{name}.ico", format="ICO",
    sizes=[(256,256), (64,64), (48,48), (32,32), (16,16)])
print(f"{name}.ico")
