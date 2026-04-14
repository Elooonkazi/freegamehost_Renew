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

# ================= 🚀 核心魔法：使用底层 CDP 强制注入 Cookie =================
def inject_vip_cookies_via_cdp(sb):
    cookies = [
        {"name": "cf_clearance", "value": "wIHY.vDl2N0tC2qnLX14QcMrMHAQdayMSvLSvGhl_Vc-1776164928-1.2.1.1-21UV17ZNUPP5TE86JDcrOiFKpAn5Uf1H.PjuD9L9NNgEsaETQsKCkHomf71NHVCBVQd3C6OIlg1BQr6s8MdyQYCNHyx._SPTyLO1MDxAYiWk1ZGAa5DNEmY8S3Li_rdJsJ1xfvj2LxFYAgkkhWh00Jcc5R9SQykDkI2vInTP3mo.0Mbi0Yas4xTKckLI.LQRtdbT.oLwEZnUzOHCzam1GiFXYZ4I6Znn.r4WQq_LSCdheyPXEMEMawvJFGZEi1CyFfEOfHHrWviFBCrNAgHa56lKQf32mB_UY3GfJimNzZqHfWo9FqjvpMksn6BVybM1uBfnYXjcWtHvXkfXVKbPxw"},
        {"name": "pterodactyl_session", "value": "eyJpdiI6InBBdHlZRDA2cUFya1VxYVNkU2hwbmc9PSIsInZhbHVlIjoiaGM3M0t0Y0Z2Y0xNVnBBdkNpSGhiR3l1L2VqSXkrYWhhWnpzMlhDOExURWJwODlDOXNxUEd5eGhPaUh0L0lJUTJRMG9lNzA5cTdVNzR6am5STCtZZEJFZGVsdit3bmdjVU1zbm92b2VFOVhONDhzenRhUld0L1VFa2NPOWxmQWEiLCJtYWMiOiJkMjgyMWYwNTAzYWNjOTFkNWY0OTUyNDRjZmU3ZTRmNWZjMDFiZjgzMDY3ZjYwNWUwODcwNmI0OGI3YzkzODk0IiwidGFnIjoiIn0%3D"},
        {"name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", "value": "eyJpdiI6IkIxUEVjRmhJUGdaZ2RzbjdPU083OUE9PSIsInZhbHVlIjoiZ3VFR0tMTGx4OG1FRUNSWFdYNFhLd0xTLzBRQkRJLzkzNmg2WHowN3czTWpRdUxPUjQ2ZDlGQm1rbDYwYWZpajl1WWtTM2oweEdFNkNiQ2Uxc2hRUXlYMi9ya3BjRm5Ib2NCQ0x1RXdPVUEwa3VINU02RVkyS255eUoxbnNQakI3eS9BbTNSTzBOM1J0WGJkWlBCRlVBWTNsRm1zczVzcGplK2NkUEVTL0pyNDZQclVtTXd1SWo1Ti9xUFUyRHo1cERJYnFIVU83N2RNM3NOaHJGY2xoTWI4cWptYnp0WEgzcWVSNnV3bHQ1TT0iLCJtYWMiOiJmOTFhYjk2ODEwZGMzYzU5ZjdmNWQ5ZDFhMGE0MTBlMzZlMWY2MDdkYTAzODRkMzViY2M5NmZlNTA5NTY2ODZjIiwidGFnIjoiIn0%3D"}
    ]
    
    print("正在通过 Chrome 开发者协议 (CDP) 强制写入无视域名的 Cookie...")
    for c in cookies:
        try:
            # CDP 指令拥有最高权限，无论页面处于什么状态都能强行写入！
            sb.driver.execute_cdp_cmd('Network.setCookie', {
                'name': c['name'],
                'value': c['value'],
                'domain': 'panel.freegamehost.xyz',
                'path': '/',
                'secure': True
            })
            print(f"✅ CDP 强注成功: {c['name']}")
        except Exception as e:
            print(f"⚠️ CDP 写入失败: {e}")

# ================= 主流程 =================
def process_account(account):
    email = account.get('email', '')
    password = account.get('password', '')
    TARGET_SERVER_URL = "https://panel.freegamehost.xyz/server/41ed8b6e"
    
    print(f"==========================================")
    print(f"👤 开始处理账号: {email}")
    print(f"==========================================")

    with SB(uc=True, headless=False, proxy="fgh:renew@127.0.0.1:10808") as sb:
        try:
            sb.driver.set_window_size(1920, 1080)
            
            # 【策略 A】：无脑强注 Cookie 登录
            print("▶️ 策略 A: 尝试使用底层 CDP 注入 Cookie 免密登录...")
            # 随便打开个什么页面激活浏览器网络模块
            sb.uc_open_with_reconnect("about:blank", 5) 
            inject_vip_cookies_via_cdp(sb)
            
            # 直接带票闯关
            sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/", 10)
            sb.sleep(5)

            is_logged_in = sb.is_element_visible('a[href="/account"]') or sb.is_element_visible('.fa-sign-out-alt')

            # 【策略 B】：智能排队物理登录
            if not is_logged_in:
                print("⚠️ Cookie 已失效。启动策略 B: 智能物理登录...")
                sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/auth/login", 10)
                
                # 🌟 修复：先等 Cloudflare 盾出现并破解，再找密码框！
                print("等待并处理可能存在的 Cloudflare 5秒盾...")
                sb.sleep(5) 
                if sb.is_element_present('iframe[src*="cloudflare"]'):
                    print("🛡️ 检测到 5秒盾！尝试破解中...")
                    sb.uc_gui_click_captcha()
                    sb.sleep(8) # 破解后多等一会，让真实的登录页面渲染出来
                
                try:
                    # 现在页面加载好了，我们给它足足 20 秒去寻找邮箱框
                    print("等待登录表单渲染...")
                    sb.wait_for_element('input[type="email"], input[name="email"]', timeout=20)
                    
                    # 填写账号密码
                    sb.type('input[type="email"], input[name="email"]', email)
                    sb.type('input[type="password"], input[name="password"]', password)
                    sb.sleep(2)
                        
                    sb.click('button[type="submit"], button:contains("Login")')
                    print("提交登录，等待跳转...")
                    sb.sleep(8) 
                    
                    is_logged_in = sb.is_element_visible('a[href="/account"]') or sb.is_element_visible('.fa-sign-out-alt')
                except Exception as login_err:
                    print(f"密码登录过程发生异常 (找不到输入框或被拦截): {login_err}")

            if not is_logged_in:
                print("❌ 所有登录策略均失败！")
                fatal_img = f"{email}_login_fatal.png"
                sb.save_screenshot(fatal_img)
                send_tg_photo(f"❌ FGH 账号 {email} 登录彻底失败，请查看截图排查原因。", fatal_img)
                return False
                
            print("✅ 成功登录面板！")

            # ================= 空降并执行续期 =================
            print(f"✈️ 正在空降目标服务器...")
            sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
            sb.sleep(8) 

            # 1. 检查冷却状态
            page_text = sb.get_text('body').upper()
            if "RENEWAL COOLDOWN" in page_text:
                print("⏳ 目标服务器处于冷却期。")
                cd_img = f"{email}_cooldown.png"
                sb.save_screenshot(cd_img)
                send_tg_photo(f"⏳ FGH 服务器 41ed8b6e 续期冷却中，时间未到。", cd_img)
                return True 

            # 2. 点击续期
            print("尝试寻找并点击续期按钮...")
            if sb.is_element_visible('button:contains("续期")') or sb.is_element_visible('button:contains("Renew")'):
                sb.click('button:contains("续期"), button:contains("Renew")')
            else:
                try:
                    sb.click('a:contains("续期"), a:contains("Renew"), a:contains("Billing")')
                    sb.sleep(2)
                    sb.click('button:contains("续期"), button:contains("Renew")')
                except:
                    print("⚠️ 没找到续期按钮！")
                    err_img = f"{email}_no_button.png"
                    sb.save_screenshot(err_img)
                    send_tg_photo(f"⚠️ FGH 续期失败：未找到可点击的续期按钮。", err_img)
                    return False

            print("等待续期验证框加载...")
            sb.sleep(5)

            if sb.is_element_present('iframe[src*="cloudflare"]'):
                print("执行最终的 Cloudflare 验证...")
                sb.uc_gui_click_captcha()
                sb.sleep(3)

            print("点击确认...")
            sb.click('button:contains("确认"), button:contains("Confirm"), button[class*="success"]')
            sb.sleep(4)

            print("🎉 续期操作执行完毕!")
            success_img = f"{email}_success.png"
            sb.save_screenshot(success_img)
            send_tg_photo(f"🎉 恭喜！FGH 服务器 41ed8b6e 续期操作成功！", success_img)

        except Exception as e:
            print(f"❌ 运行中途发生异常: {e}")
            error_img = f"{email}_runtime_error.png"
            sb.save_screenshot(error_img)
            send_tg_photo(f"❌ FGH 脚本运行发生异常终止，请查看报错截图。", error_img)
            return False
            
    return True

def main():
    if not ACCOUNTS:
        print("没有账号需要处理。")
        return

    for account in ACCOUNTS:
        process_account(account)
        time.sleep(5)
        
    print("✅ 任务全部处理完毕")

if __name__ == "__main__":
    main()
