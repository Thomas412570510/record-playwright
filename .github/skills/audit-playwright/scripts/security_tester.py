import re
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

def test_login_reset(page, url):
    print(f"\n🚀 [開始檢測] 前往網址: {url}")
    
    test_account = "ErrorUser"
    test_password = "WrongPassword123!"
    test_captcha = "0000"
    finding = "正常 (未發現明顯輸入框或已通過)"
    
    try:
        page.goto(url, timeout=15000, wait_until="networkidle")
    except PlaywrightTimeoutError:
        print("⚠️ 網頁載入緩慢，繼續執行...")
    except Exception as e:
        return f"連線失敗: {str(e)[:20]}"

    acc_locator = None
    pwd_locator = None
    cap_locator = None

    try:
        # 找帳號
        acc_locator = page.locator("input[name*='user'], input[id*='user'], input[name*='account'], input[name*='login'], input[type='email']").first
        if not acc_locator.is_visible(timeout=2000):
            acc_locator = page.get_by_placeholder(re.compile(r"帳號|信箱|Email|User|ID", re.IGNORECASE)).first
        if acc_locator.is_visible():
            acc_locator.fill(test_account)

        # 找密碼
        pwd_locator = page.locator("input[type='password']").first
        if pwd_locator.is_visible():
            pwd_locator.fill(test_password)

        # 找驗證碼
        cap_locator = page.get_by_placeholder(re.compile(r"驗證碼|Captcha|認證碼", re.IGNORECASE)).first
        if cap_locator.is_visible(timeout=1500):
            cap_locator.fill(test_captcha)

        # 找登入按鈕並點擊
        login_btn = page.locator("button, input[type='submit'], input[type='button']").filter(
            has_text=re.compile(r"登入|Login|Sign in|送出", re.IGNORECASE)
        ).first
        
        if login_btn.is_visible():
            login_btn.click()
        else:
            return "找不到登入按鈕"

        page.wait_for_timeout(3000) 
        
        # 資安檢測
        issues = []
        if pwd_locator and pwd_locator.is_visible():
            if pwd_locator.input_value() != "":
                issues.append("密碼無清空")
                
        if cap_locator and cap_locator.is_visible():
            if cap_locator.input_value() != "":
                issues.append("驗證碼無清空")
                
        if issues:
            finding = "、".join(issues)
        else:
            if pwd_locator.is_visible() == False and acc_locator.is_visible() == False:
                 finding = "正常 (報錯後跳轉或隱藏表單)"
            else:
                 finding = "正常 (欄位已清空)"
            
    except Exception as e:
        finding = f"執行異常"

    return finding
