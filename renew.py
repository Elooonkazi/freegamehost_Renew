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

# ================= 📸 核心升级：支持发送带图的 TG 通知 =================
def send_tg_photo(msg, photo_path=None):
    if not TG_BOT_ENV:
        return
    try:
        chat_id, bot_token = TG_BOT_ENV.split(':', 1)
        # 如果有截图且文件存在，发送图片 + 文字说明
        if photo_path and os.path.exists(photo_path):
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            with open(photo_path, 'rb') as f:
                requests.post(url, data={"chat_id": chat_id, "caption": msg}, files={"photo": f})
        # 如果没有截图，退化为仅发送文字
        else:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": msg})
    except Exception as e:
        print(f"⚠️ TG 通知发送失败: {e}")

# ================= 核心魔法：注入你的 VIP 通行证 =================
def inject_vip_cookies(sb):
    cookies = [
        {"name": "cf_clearance", "value": "wIHY.vDl2N0tC2qnLX14QcMrMHAQdayMSvLSvGhl_Vc-1776164928-1.2.1.1-21UV17ZNUPP5TE86JDcrOiFKpAn5Uf1H.PjuD9L9NNgEsaETQsKCkHomf71NHVCBVQd3C6OIlg1BQr6s8MdyQYCNHyx._SPTyLO1MDxAYiWk1ZGAa5DNEmY8S3Li_rdJsJ1xfvj2LxFYAgkkhWh00Jcc5R9SQykDkI2vInTP3mo.0Mbi0Yas4xTKckLI.LQRtdbT.oLwEZnUzOHCzam1GiFXYZ4I6Znn.r4WQq_LSCdheyPXEMEMawvJFGZEi1CyFfEOfHHrWviFBCrNAgHa56lKQf32mB_UY3GfJimNzZqHfWo9FqjvpMksn6BVybM1uBfnYXjcWtHvXkfXVKbPxw"},
        {"name": "pterodactyl_session", "value": "eyJpdiI6InBBdHlZRDA2cUFya1VxYVNkU2hwbmc9PSIsInZhbHVlIjoiaGM3M0t0Y0Z2Y0xNVnBBdkNpSGhiR3l1L2VqSXkrYWhhWnpzMlhDOExURWJwODlDOXNxUEd5eGhPaUh0L0lJUTJRMG9lNzA5cTdVNzR6am5STCtZZEJFZGVsdit3bmdjVU1zbm92b2VFOVhONDhzenRhUld0L1VFa2NPOWxmQWEiLCJtYWMiOiJkMjgyMWYwNTAzYWNjOTFkNWY0OTUyNDRjZmU3ZTRmNWZjMDFiZjgzMDY3ZjYwNWUwODcwNmI0OGI3YzkzODk0IiwidGFnIjoiIn0%3D"},
        {"name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", "value": "eyJpdiI6IkIxUEVjRmhJUGdaZ2RzbjdPU083OUE9PSIsInZhbHVlIjoiZ3VFR0tMTGx4OG1FRUNSWFdYNFhLd0xTLzBRQkRJLzkzNmg2WHowN3czTWpRdUxPUjQ2ZDlGQm1rbDYwYWZpajl1WWtTM2oweEdFNkNiQ2Uxc2hRUXlYMi9ya3BjRm5Ib2NCQ0x1RXdPVUEwa3VINU02RVkyS255eUoxbnNQakI3eS9BbTNSTzBOM1J0WGJkWlBCRlVBWTNsRm1zczVzcGplK2NkUEVTL0pyNDZQclVtTXd1SWo1Ti9xUFUyRHo1cERJYnFIVU83N2RNM3NOaHJGY2xoTWI4cWptYnp0WEgzcWVSNnV3bHQ1TT0iLCJtYWMiOiJmOTFhYjk2ODEwZGMzYzU5ZjdmNWQ5ZDFhMGE0MTBlMzZlMWY2MDdkYTAzODRkMzViY2M5NmZlNTA5NTY2ODZjIiwidGFnIjoiIn0%3D"}
    ]
    for cookie in cookies:
        try:
            sb.driver.add_cookie(cookie)
        except:
            pass

# ================= 主流程 =================
def process_account(account):
    email = account.get('email', '')
    password = account.get('password', '')  # ⚠️ 确保你的 GitHub Secrets JSON 里有 password 字段
    
    TARGET_SERVER_URL = "https://panel.freegamehost.xyz/server/41ed8b6e"
    
    print(f"==========================================")
    print(f"👤 开始处理账号: {email}")
    print(f"==========================================")

    with SB(uc=True, headless=False, proxy="fgh:renew@127.0.0.1:10808") as sb:
        try:
            sb.driver.set_window_size(1920, 1080)
            
            # 【策略 A】：优先使用 Cookie 登录
            print("▶️ 策略 A: 尝试使用 Cookie 免密登录...")
            sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/auth/login", 10)
            sb.sleep(3)
            inject_vip_cookies(sb)
            sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/", 10)
            sb.sleep(5)

            is_logged_in = sb.is_element_visible('a[href="/account"]') or sb.is_element_visible('.fa-sign-out-alt')

            # 【策略 B】：Cookie 失效，回退到账号密码登录
            if not is_logged_in:
                print("⚠️ Cookie 已失效或未生效。启动策略 B: 使用账号密码进行物理登录...")
                sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/auth/login", 10)
                sb.sleep(5)
                
                try:
                    # 填写账号密码
                    sb.type('input[type="email"], input[name="email"]', email)
                    sb.type('input[type="password"], input[name="password"]', password)
                    sb.sleep(2)
                    
                    # 解决登录页可能出现的 5秒盾
                    if sb.is_element_present('iframe[src*="cloudflare"]'):
                        print("检测到登录页验证码，尝试破解...")
                        sb.uc_gui_click_captcha()
                        sb.sleep(3)
                        
                    # 点击登录
                    sb.click('button[type="submit"], button:contains("Login")')
                    sb.sleep(6) # 等待页面跳转
                    
                    # 再次判定是否成功
                    is_logged_in = sb.is_element_visible('a[href="/account"]') or sb.is_element_visible('.fa-sign-out-alt')
                except Exception as login_err:
                    print(f"密码登录过程发生异常: {login_err}")

            # 彻底登录失败，截图并发送告警
            if not is_logged_in:
                print("❌ 所有登录策略均失败！")
                fatal_img = f"{email}_login_fatal.png"
                sb.save_screenshot(fatal_img)
                send_tg_photo(f"❌ FGH 账号 {email} 登录彻底失败 (Cookie与密码均无效)，请检查账号状态或网络！", fatal_img)
                return False
                
            print("✅ 成功登录面板！")

            # ================= 空降目标服务器 =================
            print(f"✈️ 正在空降目标服务器: {TARGET_SERVER_URL}")
            sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
            sb.sleep(8) 

            # 1. 检查冷却状态 (带图 TG 通知)
            page_text = sb.get_text('body').upper()
            if "RENEWAL COOLDOWN" in page_text:
                print("⏳ 当前服务器处于【续期冷却中 (RENEWAL COOLDOWN)】")
                cd_img = f"{email}_cooldown.png"
                sb.save_screenshot(cd_img)
                send_tg_photo(f"⏳ FGH 服务器 41ed8b6e 续期冷却中，时间未到。", cd_img)
                return True 

            # 2. 原汁原味的点击续期逻辑
            print("尝试寻找并点击续期按钮...")
            if sb.is_element_visible('button:contains("续期")') or sb.is_element_visible('button:contains("Renew")'):
                sb.click('button:contains("续期"), button:contains("Renew")')
            else:
                try:
                    sb.click('a:contains("续期"), a:contains("Renew"), a:contains("Billing")')
                    sb.sleep(2)
                    sb.click('button:contains("续期"), button:contains("Renew")')
                except:
                    print("⚠️ 没找到续期按钮！可能是 UI 变了。")
                    err_img = f"{email}_no_button.png"
                    sb.save_screenshot(err_img)
                    send_tg_photo(f"⚠️ FGH 续期失败：未找到续期按钮，页面 UI 可能发生了改变。", err_img)
                    return False

            print("等待 Turnstile 验证组件加载...")
            sb.sleep(5)

            if sb.is_element_present('iframe[src*="cloudflare"]'):
                print("执行动作验证...")
                sb.uc_gui_click_captcha()
                print("✅ Cloudflare Turnstile 验证通过!")
                sb.sleep(3)

            print("点击确认续期按钮...")
            sb.click('button:contains("确认"), button:contains("Confirm"), button[class*="success"]')
            sb.sleep(4)

            # 3. 成功续期 (带图 TG 通知)
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
