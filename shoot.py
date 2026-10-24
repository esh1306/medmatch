"""Playwright: run each case in a mode and screenshot. usage: shoot.py <mode: live|cache> [case_ids...]"""
import sys, time
from playwright.sync_api import sync_playwright
mode = sys.argv[1]; ids = sys.argv[2:]
TITLES = {"fisher_gp_vs_community":"Fisher (step 1)","fisher_community_vs_agency":"Fisher (step 2)","elliott":"Elliott","burgess":"Burgess"}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width":1500,"height":1000})
    for cid in ids:
        pg.goto("http://localhost:8501"); pg.wait_for_selector("text=Check records", timeout=60000)
        pg.locator("[data-testid=stSelectbox]").click(); pg.get_by_text(TITLES[cid], exact=False).last.click()
        pg.get_by_text("Live (Mubit" if mode=="live" else "Replay from cache").click()
        time.sleep(1); pg.get_by_role("button", name="Check records").click()
        pg.wait_for_selector("text=Pharmacist worklist", timeout=180000); time.sleep(1.5)
        txt = pg.locator("h3:has-text('medicines checked')").inner_text()
        info = pg.locator("[data-testid=stAlert]").first.inner_text()
        print(cid, mode, "|", txt, "|", info.replace("\n"," "))
        pg.screenshot(path=f"screenshots/{cid}_{mode}_full.png", full_page=True)
        pg.get_by_text("Pharmacist worklist").scroll_into_view_if_needed()
        pg.screenshot(path=f"screenshots/{cid}_{mode}_worklist.png")
    b.close()
