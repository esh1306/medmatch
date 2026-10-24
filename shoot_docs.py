import sys,time
from playwright.sync_api import sync_playwright
cases=sys.argv[1].split(","); W,H=int(sys.argv[2]),int(sys.argv[3])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg=b.new_page(viewport={"width":W,"height":H})
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(sys.argv[4] if len(sys.argv)>4 else "http://localhost:8765/")
    for c in cases:
        pg.click(f'[data-c="{c}"]')
        for s in range(7):
            pg.click(f'[data-s="{s}"]'); time.sleep({4:16,2:8}.get(s,5))
            pg.screenshot(path=f"docs/screenshots/{c}_{s+1}_{W}.png")
    print("errors:",errs)
    b.close()
