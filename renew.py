import os
import json
import time
import requests
from seleniumbase import SB

# ================= 配置读取 =================
FGH_ACCOUNT_ENV = os.environ.get('FGH_ACCOUNT', '[]')
TG_BOT_ENV = os.environ.get('TG_BOT', '')

try:
    ACCOUNTS = json.loads(FGH_ACCOUNT_ENV)
except Exception as e:
    print(f"❌ 环境变量解析失败，请检查 JSON 格式: {e}")
    exit(1)

def send_tg_msg(msg):
    if not TG_BOT_ENV:
        return
    try:
        chat_id, bot_token = TG_BOT_ENV.split(':', 1)
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": msg})
    except Exception as e:
        print(f"⚠️ TG 通知发送失败: {e}")

# ================= 核心魔法：注入你的 VIP 通行证 =================
def inject_vip_cookies(sb):
    # 🌟 关键修复：域名后缀改为 .xyz
    domain = ".freegamehost.xyz" 
    
    cookies = [
        {
            "name": "cf_clearance",
            "value": "wIHY.vDl2N0tC2qnLX14QcMrMHAQdayMSvLSvGhl_Vc-1776164928-1.2.1.1-21UV17ZNUPP5TE86JDcrOiFKpAn5Uf1H.PjuD9L9NNgEsaETQsKCkHomf71NHVCBVQd3C6OIlg1BQr6s8MdyQYCNHyx._SPTyLO1MDxAYiWk1ZGAa5DNEmY8S3Li_rdJsJ1xfvj2LxFYAgkkhWh00Jcc5R9SQykDkI2vInTP3mo.0Mbi0Yas4xTKckLI.LQRtdbT.oLwEZnUzOHCzam1GiFXYZ4I6Znn.r4WQq_LSCdheyPXEMEMawvJFGZEi1CyFfEOfHHrWviFBCrNAgHa56lKQf32mB_UY3GfJimNzZqHfWo9FqjvpMksn6BVybM1uBfnYXjcWtHvXkfXVKbPxw",
            "domain": domain
        },
        {
            "name": "pterodactyl_session",
            "value": "eyJpdiI6InBBdHlZRDA2cUFya1VxYVNkU2hwbmc9PSIsInZhbHVlIjoiaGM3M0t0Y0Z2Y0xNVnBBdkNpSGhiR3l1L2VqSXkrYWhhWnpzMlhDOExURWJwODlDOXNxUEd5eGhPaUh0L0lJUTJRMG9lNzA5cTdVNzR6am5STCtZZEJFZGVsdit3bmdjVU1zbm92b2VFOVhONDhzenRhUld0L1VFa2NPOWxmQWEiLCJtYWMiOiJkMjgyMWYwNTAzYWNjOTFkNWY0OTUyNDRjZmU3ZTRmNWZjMDFiZjgzMDY3ZjYwNWUwODcwNmI0OGI3YzkzODk0IiwidGFnIjoiIn0%3D",
            "domain": domain
        },
        {
            "name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d",
            "value": "eyJpdiI6IkIxUEVjRmhJUGdaZ2RzbjdPU083OUE9PSIsInZhbHVlIjoiZ3VFR0tMTGx4OG1FRUNSWFdYNFhLd0xTLzBRQkRJLzkzNmg2WHowN3czTWpRdUxPUjQ2ZDlGQm1rbDYwYWZpajl1WWtTM2oweEdFNkNiQ2Uxc2hRUXlYMi9ya3BjRm5Ib2NCQ0x1RXdPVUEwa3VINU02RVkyS255eUoxbnNQakI3eS9BbTNSTzBOM1J0WGJkWlBCRlVBWTNsRm1zczVzcGplK2NkUEVTL0pyNDZQclVtTXd1SWo1Ti9xUFUyRHo1cERJYnFIVU83N2RNM3NOaHJGY2xoTWI4cWptYnp0WEgzcWVSNnV3bHQ1TT0iLCJtYWMiOiJmOTFhYjk2ODEwZGMzYzU5ZjdmNWQ5ZDFhMGE0MTBlMzZlMWY2MDdkYTAzODRkMzViY2M5NmZlNTA5NTY2ODZjIiwidGFnIjoiIn0%3D",
            "domain": domain
        }
    ]
    
    # 注入 Cookie
    for cookie in cookies:
        sb.driver.add_cookie(cookie)
    print("✅ VIP Cookie 注入完毕！")

# ================= 主流程 =================
def process_account(account):
    email = account.get('email')
    
    print(f"==========================================")
    print(f"👤 开始处理账号: {email}")
    print(f"==========================================")
    print("🌐 启动浏览器...")

    # 我们依然带着你的 HTTP 代理插件，以防万一
    with SB(uc=True, headless=False, proxy="fgh:renew@127.0.0.1:10808") as sb:
        try:
            sb.driver.set_window_size(1920, 1080)
            
            # 第一步：先打开一个目标网站的 404 页面，获得 .xyz 的域名环境
            print("正在获取域名许可...")
            sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/robots.txt", 10) # 🌟 修复为 .xyz
            sb.sleep(2)
            
            # 第二步：强行塞入登录凭证
            print("正在注入登录状态...")
            inject_vip_cookies(sb)
            
            # 第三步：拿着通行证，直接空降到面板主页
            print("VIP 免密直达服务器面板...")
            sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/", 10) # 🌟 修复为 .xyz
            sb.sleep(5)

            # 检查是否成功骗过了网站
            if sb.is_element_visible('a[href="/admin"]') or "panel" in sb.get_current_url():
                print("✅ 免密登录成功! https://panel.freegamehost.xyz/")
            else:
                print("❌ Cookie 可能已失效，被踢回登录页。")
                sb.save_screenshot(f"{email}_login_failed.png")
                return False

            print(f"准备续期，当前页面: {sb.get_current_url()}")
            
            # ==============================================================
            # 以下部分完全保留你最初的续期逻辑，一字未改！
            # ==============================================================
            server_links = sb.find_visible_elements('a[href^="/server/"]')
            if not server_links:
                print("⚠️ 未找到任何服务器列表。")
                return True
                
            server_urls = [el.get_attribute('href') for el in server_links]

            for srv_url in server_urls:
                print(f"导航到服务器页面: {srv_url}")
                sb.uc_open_with_reconnect(srv_url, 5)
                sb.sleep(3)
                
                try:
                    srv_name = sb.get_text('h1')
                    print(f"服务器名称: {srv_name}")
                except:
                    pass

                print("开始执行续期操作...")
                if sb.is_element_visible('button:contains("续期")') or sb.is_element_visible('button:contains("Renew")'):
                    sb.click('button:contains("续期"), button:contains("Renew")')
                else:
                    sb.click('a:contains("续期"), a:contains("Renew"), a:contains("Billing")')
                    sb.sleep(2)
                    sb.click('button:contains("续期"), button:contains("Renew")')

                print("等待 Turnstile 验证组件加载(最多20s)...")
                sb.sleep(3)

                if sb.is_element_present('iframe[src*="cloudflare"]'):
                    print("执行动作验证...")
                    sb.uc_gui_click_captcha()
                    print("✅ Cloudflare Turnstile 验证通过!")
                    sb.sleep(2)

                print("点击确认续期按钮...")
                sb.click('button:contains("确认"), button:contains("Confirm"), button[class*="success"]')
                sb.sleep(3)

                print("🎉 续期成功!")

        except Exception as e:
            print(f"❌ 运行发生异常: {e}")
            sb.save_screenshot(f"{email}_error.png")
            return False
            
    return True

def main():
    if not ACCOUNTS:
        print("没有账号需要处理。")
        return

    for account in ACCOUNTS:
        success = process_account(account)
        if success:
            send_tg_msg(f"✅ FGH 账号 {account.get('email')} 续期成功！")
        else:
            send_tg_msg(f"❌ FGH 账号 {account.get('email')} 续期失败，请查看截图。")
        time.sleep(5)
        
    print("✅ 任务全部处理完毕")

if __name__ == "__main__":
    main()
