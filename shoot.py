import sys, time
from playwright.sync_api import sync_playwright
mode = sys.argv[1]; ids = sys.argv[2:]
T = {"fisher": "Fisher", "elliott": "Elliott", "burgess": "Burgess"}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1500, "height": 1100})
    for cid in ids:
        pg.goto("http://localhost:8501"); pg.wait_for_selector("text=Check records", timeout=60000)
        pg.locator("[data-testid=stSelectbox]").click(); pg.get_by_role("option", name=T[cid], exact=False).click()
        pg.get_by_text("Live (Mubit" if mode == "live" else "Replay from cache").click(); time.sleep(1)
        pg.get_by_role("button", name="Check records").click()
        pg.wait_for_selector("text=Pharmacist worklist", timeout=240000); time.sleep(1.5)
        print(cid, mode, "|", pg.locator("h3:has-text('medicines checked')").inner_text())
        pg.screenshot(path=f"screenshots/{cid}_{mode}_top.png")
        pg.get_by_text("Pharmacist worklist").scroll_into_view_if_needed(); time.sleep(0.5)
        pg.screenshot(path=f"screenshots/{cid}_{mode}_worklist.png")
        pg.get_by_text("Conflict, pharmacist review").first.scroll_into_view_if_needed(); pg.mouse.wheel(0, 250); time.sleep(0.5)
        pg.screenshot(path=f"screenshots/{cid}_{mode}_rows.png")
    b.close()
