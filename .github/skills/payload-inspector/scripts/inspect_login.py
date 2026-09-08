import sys
import json
import re
from playwright.sync_api import sync_playwright
from payload_listener import PayloadSniffer

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def inspect_url(url, account="TestUser", password="WrongPassword123!"):
    print(f"\n🔍 [啟動 Payload 攔截器] 目標網址: {url}")
    
    sniffer = PayloadSniffer(target_keywords=["pwd", "password", "rangpwd", "account", "login", "user"])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. 綁定監聽器，開始監控所有網路流量
        sniffer.attach_to_page(page)

        try:
            page.goto(url, timeout=15000, wait_until="networkidle")
        except Exception:
            print("⚠️ 網頁載入緩慢或完成逾時，繼續執行填表動作...")

        # 2. 尋找輸入框並填寫
        try:
            acc_input = page.locator("input[name*='user'], input[id*='user'], input[name*='account'], input[name*='login'], input[type='text']").first
            if acc_input.is_visible(timeout=2000):
                acc_input.fill(account)
                print(f"✅ 填入帳號: {account}")

            pwd_input = page.locator("input[type='password']").first
            if pwd_input.is_visible(timeout=2000):
                pwd_input.fill(password)
                print(f"✅ 填入密碼")

            # 3. 點擊登入以發送請求
            btn = page.locator("button, input[type='submit']").filter(
                has_text=re.compile(r"登入|Login|Sign in|送出", re.IGNORECASE)
            ).first

            if not btn.is_visible(timeout=1000):
                btn = page.locator("button[type='submit'], input[type='submit'], button").first

            if btn.is_visible(timeout=2000):
                print("💥 點擊登入按鈕，觸發資料傳送...")
                btn.click()
                page.wait_for_timeout(3000) # 等待封包送出
            else:
                print("⚠️ 找不到明顯的登入按鈕，等待 3 秒確認是否有背景請求...")
                page.wait_for_timeout(3000)

        except Exception as e:
            print(f"⚠️ 互動過程中出現狀況: {e}")

        browser.close()

    # 4. 輸出結果報告
    sniffer.print_summary()
    return sniffer.get_records()

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://the-internet.herokuapp.com/login"
    inspect_url(target)
