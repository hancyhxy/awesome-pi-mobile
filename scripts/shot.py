"""Store a small screenshot of a project for the README: media/<id>.jpg.
Takes the project's own public image (App Store, README or site), crops it to a phone
screen (9:19.5) from the top, and keeps it at 360 px wide.
    pyx scripts/shot.py <id> <image URL or path> [--wide]
--wide keeps a 16:10 crop for web apps. Then set "shot" and "shotFrom" in data/projects.json.
"""
import io, sys, pathlib, urllib.request
from PIL import Image
root = pathlib.Path(__file__).resolve().parent.parent
pid, src = sys.argv[1], sys.argv[2]
wide = "--wide" in sys.argv
src = src.replace("320x480bb", "600x1300bb")  # App Store: ask for a larger size
raw = urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})).read() if src.startswith("http") else pathlib.Path(src).read_bytes()
im = Image.open(io.BytesIO(raw)).convert("RGB")
ratio = 10 / 16 if wide else 19.5 / 9
w = im.width; h = min(im.height, int(w * ratio))
im = im.crop((0, 0, w, h))
W = 640 if wide else 360
im = im.resize((W, int(W * h / w)), Image.LANCZOS)
out = root / "media" / f"{pid}.jpg"; im.save(out, quality=78, optimize=True)
print(out, im.size, out.stat().st_size // 1024, "KB")
