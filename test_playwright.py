import time
import json
from playwright.sync_api import sync_playwright

def test_module0():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("[1] Navigating to ComfyUI Login...")
        page.goto('http://194.93.49.14:20032/login')
        
        # Login
        print("[2] Authenticating...")
        page.fill('input[type="text"]', 'root')
        page.fill('input[type="password"]', 'rri_8OfJfM3gnJCBdMCZ')
        page.keyboard.press('Enter')
        page.wait_for_selector('canvas')
        print("[3] Logged in successfully. Waiting for App initialization...")
        time.sleep(3)
        
        # Read workflow
        with open('production/workflows/module0_preprocessing.json') as f:
            wf_data = f.read()
        
        # Load the graph data via the App object
        print("[4] Injecting workflow data...")
        page.evaluate(f"""
            window.app.loadGraphData({wf_data});
        """)
        time.sleep(2)
        
        # Trigger execution via the App object
        print("[5] Executing graph via API translation...")
        page.evaluate("""
            window.app.graphToPrompt().then(p => {
                window.app.api.queuePrompt(0, p);
            });
        """)
        
        print("[6] Execution queued. Waiting 20 seconds for processing...")
        time.sleep(20)
        
        browser.close()
        print("[7] Browser closed. Output should be on server.")

if __name__ == '__main__':
    test_module0()
