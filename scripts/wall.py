"""Build media/wall.png: a wall of the projects' own screenshots for the top of the README.
Phone screenshots of every app and phone web UI in rows of nine, each labelled with its name.
Wide web screenshots stay in their README sections.
    pyx scripts/wall.py
"""
import json, pathlib, base64
from playwright.sync_api import sync_playwright
root = pathlib.Path(__file__).resolve().parent.parent
db = json.loads((root / "data/projects.json").read_text())
uri = lambda p: "data:image/jpeg;base64," + base64.b64encode((root / p).read_bytes()).decode()
phones = [p for p in db["projects"] if p.get("shot") and not p.get("shotWide")]
def tag(p): return f'<span>{p["name"]}{" · sample" if p.get("ours") else ""}</span>'
ph = "".join(f'<figure class="ph"><img src="{uri(p["shot"])}">{tag(p)}</figure>' for p in phones)
html = f"""<html><head><style>
body{{margin:0;background:#101114;font-family:-apple-system,system-ui,sans-serif}}
.wrap{{width:1760px;padding:36px 40px 30px;box-sizing:border-box}}
h1{{margin:0 0 4px;color:#f3f1ec;font-size:40px;letter-spacing:-.02em}} p{{margin:0 0 26px;color:#9b988f;font-size:18px}}
.row{{display:flex;flex-wrap:wrap;gap:22px 22px;align-items:flex-end;margin-bottom:22px}}
figure{{margin:0;display:flex;flex-direction:column;align-items:center;gap:10px}}
.ph img{{width:166px;border-radius:22px;border:5px solid #2a2b30;display:block}}
span{{color:#d8d5ce;font-size:13px;font-weight:600;white-space:nowrap}}
</style></head><body><div class="wrap"><h1>Pi, from your phone</h1><p>{len(db["projects"])} apps, web UIs and setups for the Pi coding agent · screenshots from each project</p>
<div class="row">{ph}</div></div></body></html>"""
out = root / "media/wall.png"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1760, "height": 600}, device_scale_factor=1)
    pg.set_content(html); pg.wait_for_timeout(300)
    pg.locator(".wrap").screenshot(path=str(out)); b.close()
print(out)
