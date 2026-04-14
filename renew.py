import os
import json
import time
import requests
from seleniumbase import SB

# ================= 配置读取 =================
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

# ================= 核心组件 =================
def inject_vip_cookies_via_cdp(sb):
    cookies = [
        {"name": "cf_clearance", "value": "wIHY.vDl2N0tC2qnLX14QcMrMHAQdayMSvLSvGhl_Vc-1776164928-1.2.1.1-21UV17ZNUPP5TE86JDcrOiFKpAn5Uf1H.PjuD9L9NNgEsaETQsKCkHomf71NHVCBVQd3C6OIlg1BQr6s8MdyQYCNHyx._SPTyLO1MDxAYiWk1ZGAa5DNEmY8S3Li_rdJsJ1xfvj2LxFYAgkkhWh00Jcc5R9SQykDkI2vInTP3mo.0Mbi0Yas4xTKckLI.LQRtdbT.oLwEZnUzOHCzam1GiFXYZ4I6Znn.r4WQq_LSCdheyPXEMEMawvJFGZEi1CyFfEOfHHrWviFBCrNAgHa56lKQf32mB_UY3GfJimNzZqHfWo9FqjvpMksn6BVybM1uBfnYXjcWtHvXkfXVKbPxw"},
        {"name": "pterodactyl_session", "value": "eyJpdiI6InBBdHlZRDA2cUFya1VxYVNkU2hwbmc9PSIsInZhbHVlIjoiaGM3M0t0Y0Z2Y0xNVnBBdkNpSGhiR3l1L2VqSXkrYWhhWnpzMlhDOExURWJwODlDOXNxUEd5eGhPaUh0L0lJUTJRMG9lNzA5cTdVNzR6am5STCtZZEJFZGVsdit3bmdjVU1zbm92b2VFOVhONDhzenRhUld0L1VFa2NPOWxmQWEiLCJtYWMiOiJkMjgyMWYwNTAzYWNjOTFkNWY0OTUyNDRjZmU3ZTRmNWZjMDFiZjgzMDY3ZjYwNWUwODcwNmI0OGI3YzkzODk0IiwidGFnIjoiIn0%3D"},
        {"name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", "value": "eyJpdiI6IkIxUEVjRmhJUGdaZ2RzbjdPU083OUE9PSIsInZhbHVlIjoiZ3VFR0tMTGx4OG1FRUNSWFdYNFhLd0xTLzBRQkRJLzkzNmg2WHowN3czTWpRdUxPUjQ2ZDlGQm1rbDYwYWZpajl1WWtTM2oweEdFNkNiQ2Uxc2hRUXlYMi9ya3BjRm5Ib2NCQ0x1RXdPVUEwa3VINU02RVkyS255eUoxbnNQakI3eS9BbTNSTzBOM1J0WGJkWlBCRlVBWTNsRm1zczVzcGplK2NkUEVTL0pyNDZQclVtTXd1SWo1Ti9xUFUyRHo1cERJYnFIVU83N2RNM3NOaHJGY2xoTWI4cWptYnp0WEgzcWVSNnV3bHQ1TT0iLCJtYWMiOiJmOTFhYjk2ODEwZGMzYzU5ZjdmNWQ5ZDFhMGE0MTBlMzZlMWY2MDdkYTAzODRkMzViY2M5NmZlNTA5NTY2ODZjIiwidGFnIjoiIn0%3D"}
    ]
    for c in cookies:
        try:
            sb.driver.execute_cdp_cmd('Network.setCookie', {
                'name': c['name'], 'value': c['value'],
                'domain': 'panel.freegamehost.xyz', 'path': '/', 'secure': True
            })
        except:
            pass

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

    # ---------------- 隔离区 A：尝试 Cookie ----------------
    print("▶️ 策略 A: 尝试 CDP 注入 Cookie 免密登录...")
    with SB(uc=True, headless=False, proxy="fgh:renew@127.0.0.1:10808") as sb:
        sb.driver.set_window_size(1920, 1080)
        sb.uc_open_with_reconnect("about:blank", 5) 
        inject_vip_cookies_via_cdp(sb)
        sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/", 10)
        sb.sleep(6)

        if sb.is_element_visible('a[href="/account"]') or sb.is_element_visible('.fa-sign-out-alt'):
            print("✅ 策略 A 成功！直接执行续期...")
            return execute_renewal(sb, email)
        else:
            print("⚠️ 策略 A (Cookie) 失效或被 CF 拦截！准备关闭受污染的浏览器...")
    # 这里 with 代码块结束，受污染的浏览器会被彻底销毁！

    # ---------------- 隔离区 B：纯净浏览器尝试物理登录 ----------------
    print("🔄 启动策略 B: 开启全新纯净浏览器，执行物理登录...")
    with SB(uc=True, headless=False, proxy="fgh:renew@127.0.0.1:10808") as sb:
        try:
            sb.driver.set_window_size(1920, 1080)
            sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/auth/login", 10)
            
            # 对付可能存在的 5秒盾
            sb.sleep(6) 
            if sb.is_element_present('iframe[src*="cloudflare"]'):
                print("🛡️ 检测到 Cloudflare 盾，尝试破解...")
                sb.uc_gui_click_captcha()
                sb.sleep(8) 
            
            print("等待登录表单渲染...")
            sb.wait_for_element('input[type="email"], input[name="email"]', timeout=20)
            
            # 填写并提交
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
