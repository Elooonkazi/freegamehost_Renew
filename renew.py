import os
import json
import time
import requests
from seleniumbase import SB

# ================= 🚨 终极克隆配置区 🚨 =================

# 1. 你本地的真实浏览器指纹
MY_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

# 2. 你本地的最新真实 Cookie 组合
MY_COOKIES = [
    {
        "name": "cf_clearance", 
        "value": "o7tH8YbzuVDqzu3IuSi42d3U9.dOFlUsmQa.ixpcD0I-1776168022-1.2.1.1-ak8KC4txaydnj6dl287_JdV_EjP5yj6TZCf7dCjfSe3vKKYZPllYx5HtySb7dxluydiUYaBBybh.oTAFS9VO86ADi0zOhO7GdXa9yb39QD8vBBZ.gca3o4h3gxHE1vbXIVq6Ia.5os3NdgtzuAJxvSg7PYEkiAph2_.Z7iFQ0CDd87irFK3XMJUJLBrMyXLqd3ALylKmrWQLw8GXsGTmVAnkYcTo_BACHA2JcT4SQEvf9V1tqSAez8z6BkscHEp9xzGKjP8KxzeXCW3TGv2He2X5f3F7gRwz5r7NTmRto7Em8Gm_PM_EKtT3D9jdV5YMYdmGSyWGjRSQcr5NCtURbA"
    },
    {
        "name": "pterodactyl_session", 
        "value": "eyJpdiI6IjY2ZDVYd3llYi9WbmZqeGxHZFYyUVE9PSIsInZhbHVlIjoiVTd2WndFdHF2b042VExqMG5qdXI0bDZUUEJ2UDduOFdQRURBQmdsMEZLSjRrbjBRSE9NZEFvV1R5bzFKVTNhaUVlcXAyK0FBYVRKTStmdUpKYnFjcFlzaFpWRnp3ZWVsa0ZaVW9mMzVEU1ZIZjEwWE5GNE9hVVNtNnBwUTRQU0YiLCJtYWMiOiIwMTUyYmM2ZGJhYjcxZDdkM2ViNzZlNzMzM2Y3YTZiMTY2NDJlYmY0N2JjOTI4OTRjNjVkNzgwODI5YTg3NmM3IiwidGFnIjoiIn0%3D"
    },
    {
        "name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", 
        "value": "eyJpdiI6IkIxUEVjRmhJUGdaZ2RzbjdPU083OUE9PSIsInZhbHVlIjoiZ3VFR0tMTGx4OG1FRUNSWFdYNFhLd0xTLzBRQkRJLzkzNmg2WHowN3czTWpRdUxPUjQ2ZDlGQm1rbDYwYWZpajl1WWtTM2oweEdFNkNiQ2Uxc2hRUXlYMi9ya3BjRm5Ib2NCQ0x1RXdPVUEwa3VINU02RVkyS255eUoxbnNQakI3eS9BbTNSTzBOM1J0WGJkWlBCRlVBWTNsRm1zczVzcGplK2NkUEVTL0pyNDZQclVtTXd1SWo1Ti9xUFUyRHo1cERJYnFIVU83N2RNM3NOaHJGY2xoTWI4cWptYnp0WEgzcWVSNnV3bHQ1TT0iLCJtYWMiOiJmOTFhYjk2ODEwZGMzYzU5ZjdmNWQ5ZDFhMGE0MTBlMzZlMWY2MDdkYTAzODRkMzViY2M5NmZlNTA5NTY2ODZjIiwidGFnIjoiIn0%3D"
    }
]

# ==============================================================================

FGH_ACCOUNT_ENV = os.environ.get('FGH_ACCOUNT', '[]')
TG_BOT_ENV = os.environ.get('TG_BOT', '')
TARGET_SERVER_URL = "https://panel.freegamehost.xyz/server/41ed8b6e"

try:
    ACCOUNTS = json.loads(FGH_ACCOUNT_ENV)
except Exception as e:
    print(f"❌ 环境变量解析失败，请检查 JSON 格式: {e}")
    exit(1)

def send_tg_photo(msg, photo_path=None):
    if not TG_BOT_ENV:
        return
    try:
        chat_id, bot_token = TG_BOT_ENV.split(':', 1)
        if photo_path and os.path.exists(photo_path):
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            with open(photo_path, 'rb') as f:
                requests.post(url, data={"chat_id": chat_id, "caption": msg}, files={"photo": f})
        else:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": msg})
    except Exception as e:
        print(f"⚠️ TG 通知发送失败: {e}")

def inject_vip_cookies_via_cdp(sb):
    print("正在通过 Chrome 开发者协议 (CDP) 强制写入本地克隆 Cookie...")
    for c in MY_COOKIES:
        try:
            sb.driver.execute_cdp_cmd('Network.setCookie', {
                'name': c['name'], 'value': c['value'],
                'domain': 'panel.freegamehost.xyz', 'path': '/', 'secure': True
            })
            print(f"✅ CDP 强注成功: {c['name']}")
        except Exception as e:
            print(f"⚠️ CDP 写入失败: {e}")

def execute_renewal(sb, email):
    """单独封装的续期动作"""
    print(f"✈️ 正在空降目标服务器: {TARGET_SERVER_URL}")
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
    sb.sleep(8) 

    page_text = sb.get_text('body').upper()
    if "RENEWAL COOLDOWN" in page_text:
        print("⏳ 目标服务器处于冷却期。")
        cd_img = f"{email}_cooldown.png"
        sb.save_screenshot(cd_img)
        send_tg_photo(f"⏳ FGH 服务器续期冷却中，时间未到。", cd_img)
        return True 

    print("尝试寻找并点击续期按钮...")
    if sb.is_element_visible('button:contains("续期")') or sb.is_element_visible('button:contains("Renew")'):
        sb.click('button:contains("续期"), button:contains("Renew")')
    else:
        try:
            sb.click('a:contains("续期"), a:contains("Renew"), a:contains("Billing")')
            sb.sleep(2)
            sb.click('button:contains("续期"), button:contains("Renew")')
        except:
            err_img = f"{email}_no_button.png"
            sb.save_screenshot(err_img)
            send_tg_photo(f"⚠️ 续期失败：未找到按钮。", err_img)
            return False

    sb.sleep(5)
    if sb.is_element_present('iframe[src*="cloudflare"]'):
        sb.uc_gui_click_captcha()
        sb.sleep(3)

    sb.click('button:contains("确认"), button:contains("Confirm"), button[class*="success"]')
    sb.sleep(4)
    
    success_img = f"{email}_success.png"
    sb.save_screenshot(success_img)
    send_tg_photo(f"🎉 恭喜！FGH 服务器续期操作成功！", success_img)
    return True

# ================= 主流程 =================
def process_account(account):
    email = account.get('email', '')
    password = account.get('password', '')
    
    print(f"==========================================")
    print(f"👤 开始处理账号: {email}")
    print(f"==========================================")

    # ---------------- 隔离区 A：尝试 Cookie (携入克隆 UA) ----------------
    print("▶️ 策略 A: 尝试 CDP 注入 Cookie 免密登录...")
    with SB(uc=True, headless=False, proxy="fgh:renew@127.0.0.1:10808", agent=MY_USER_AGENT) as sb:
        sb.driver.set_window_size(1920, 1080)
        
        # 使用 uc_open_with_tab 规避一些针对首个空白标签页的检测
        sb.uc_open_with_tab("about:blank") 
        inject_vip_cookies_via_cdp(sb)
        
        sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/", 10)
        sb.sleep(6)

        if sb.is_element_visible('a[href="/account"]') or sb.is_element_visible('.fa-sign-out-alt'):
            print("✅ 策略 A 成功！完美通过身份验证！")
            return execute_renewal(sb, email)
        else:
            print("⚠️ 策略 A (Cookie) 失效或被 CF 拦截！准备关闭受污染的浏览器...")
    # 受污染的浏览器销毁完毕

    # ---------------- 隔离区 B：纯净浏览器尝试物理登录 (携入克隆 UA) ----------------
    print("🔄 启动策略 B: 开启全新纯净浏览器，执行物理登录...")
    with SB(uc=True, headless=False, proxy="fgh:renew@127.0.0.1:10808", agent=MY_USER_AGENT) as sb:
        try:
            sb.driver.set_window_size(1920, 1080)
            sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/auth/login", 10)
            
            sb.sleep(6) 
            if sb.is_element_present('iframe[src*="cloudflare"]'):
                print("🛡️ 检测到 Cloudflare 盾，尝试破解...")
                sb.uc_gui_click_captcha()
                sb.sleep(8) 
            
            print("等待登录表单渲染...")
            sb.wait_for_element('input[type="email"], input[name="email"]', timeout=20)
            
            sb.type('input[type="email"], input[name="email"]', email)
            sb.type('input[type="password"], input[name="password"]', password)
            sb.sleep(2)
            sb.click('button[type="submit"], button:contains("Login")')
            sb.sleep(8) 
            
            if sb.is_element_visible('a[href="/account"]') or sb.is_element_visible('.fa-sign-out-alt'):
                print("✅ 策略 B 物理登录成功！")
                return execute_renewal(sb, email)
            else:
                fatal_img = f"{email}_login_fatal.png"
                sb.save_screenshot(fatal_img)
                send_tg_photo(f"❌ 账号 {email} 所有登录策略均失败，请看截图。", fatal_img)
                return False
                
        except Exception as e:
            print(f"❌ 物理登录异常: {e}")
            error_img = f"{email}_error.png"
            sb.save_screenshot(error_img)
            send_tg_photo(f"❌ 脚本异常终止，截图已保存。", error_img)
            return False

def main():
    if not ACCOUNTS:
        print("没有账号需要处理。")
        return
    for account in ACCOUNTS:
        process_account(account)
        time.sleep(5)
    print("✅ 所有任务处理完毕")

if __name__ == "__main__":
    main()
