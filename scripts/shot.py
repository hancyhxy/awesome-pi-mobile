"""Store a small screenshot of a project for the README: media/<id>.jpg.
Takes the project's own public image (App Store, README or site), crops it to a phone
screen (9:19.5) from the top, and keeps it at 360 px wide.
    pyx scripts/shot.py <id> <image URL or path> [--wide] [--box x0,y0,x1,y1] [--pad]
--wide   keeps a 16:9 crop for web apps (640 px wide).
--box    first cuts this pixel box out of the source, e.g. the phone in a desktop + phone mockup.
--pad    fills up to the full ratio with the edge colour instead of cutting, for short images.
GIFs use their first frame. Then set "shot" and "shotFrom" in data/projects.json.
"""
import io, sys, pathlib, urllib.request
from PIL import Image
root = pathlib.Path(__file__).resolve().parent.parent
pid, src = sys.argv[1], sys.argv[2]
args = sys.argv[3:]
wide, pad = "--wide" in args, "--pad" in args
box = tuple(int(v) for v in args[args.index("--box") + 1].split(",")) if "--box" in args else None
src = src.replace("320x480bb", "600x1300bb")  # App Store: ask for a larger size
raw = urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})).read() if src.startswith("http") else pathlib.Path(src).read_bytes()
im = Image.open(io.BytesIO(raw)).convert("RGB")
if box: im = im.crop(box)
ratio = 9 / 16 if wide else 19.5 / 9
W = 640 if wide else 360
im = im.resize((W, round(W * im.height / im.width)), Image.LANCZOS)
H = round(W * ratio)
if im.height > H: im = im.crop((0, 0, W, H))
elif pad and im.height < H:
    canvas = Image.new("RGB", (W, H), im.getpixel((W // 2, im.height - 1)))
    canvas.paste(im, (0, (H - im.height) // 2)); im = canvas
out = root / "media" / f"{pid}.jpg"; im.save(out, quality=78, optimize=True)
print(out, im.size, out.stat().st_size // 1024, "KB")
