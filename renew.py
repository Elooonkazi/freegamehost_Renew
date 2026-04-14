import os
import json
import time
import requests
from seleniumbase import SB

# ================= 🚨 本地克隆配置区 🚨 =================

# 1. 你本地的真实浏览器指纹
MY_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

# 2. 你本地的真实 Cookie 组合
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

# ================= 基础配置 =================

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
    except Exception:
        pass

def inject_vip_cookies_via_cdp(sb):
    print("正在通过 CDP 强注克隆 Cookie...")
    for c in MY_COOKIES:
        if c["value"] and "在此填入" not in c["value"]:
            try:
                sb.driver.execute_cdp_cmd('Network.setCookie', {
                    'name': c['name'], 'value': c['value'],
                    'domain': 'panel.freegamehost.xyz', 'path': '/', 'secure': True
                })
            except Exception:
                pass

def execute_renewal(sb, email):
    """终极通关版：滑到中间 -> 点续期 -> 宽频雷达捕捉验证码 -> 死磕点击 -> 监控时间变化"""
    print(f"✈️ 正在空降目标服务器: {TARGET_SERVER_URL}")
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
    sb.sleep(8) 

    page_text = sb.get_text('body').upper()
    if "RENEWAL COOLDOWN" in page_text and "HOURS" not in page_text:
        print("⏳ 确认当前已处于冷却期。")
        cd_img = f"{email}_cooldown.png"
        sb.save_screenshot(cd_img)
        send_tg_photo(f"⏳ FGH 服务器 41ed8b6e 续期冷却中。", cd_img)
        return True 

    print("往下滚动并点击续期按钮...")
    sb.execute_script("""
        var btns = document.querySelectorAll('button, div[class*="btn"], div[class*="rounded"]');
        for (var i = 0; i < btns.length; i++) {
            if (btns[i].innerText && btns[i].innerText.includes('HOURS')) {
                btns[i].scrollIntoView({block: "center"});
                btns[i].click();
                break;
            }
        }
    """)
    print("✅ 成功点击续期按钮！静静等待 5 秒让验证码弹出来...")
    sb.sleep(5) 

    # ================= 🚨 最终 Boss 战：全频段雷达猎杀 CF 🚨 =================
    print("启动 CF 猎杀雷达...")
    
    # 🌟 致命修复：极其宽泛的匹配规则！只要涉及安全验证的框，一个不留！
    BROAD_CF_SELECTOR = 'iframe[src*="cdn-cgi"], iframe[src*="challenge"], iframe[title*="Cloudflare"], iframe[title*="challenge"]'
    
    if sb.is_element_present(BROAD_CF_SELECTOR):
        print("🛡️ 雷达锁定白色的验证画框！开始处决...")
        
        # 防止错位，强行把验证码也滚到屏幕中间
        sb.execute_script(f"""
            var cf = document.querySelector('{BROAD_CF_SELECTOR}');
            if(cf) cf.scrollIntoView({{block: "center"}});
        """)
        sb.sleep(1)

        # 🗡️ 杀招 A：原生 UC 鼠标物理模拟点击（最强破解机制）
        print("-> 释放杀招 A: 原生真人物理点击...")
        try:
            sb.uc_gui_click_captcha()
        except:
            pass
            
        sb.sleep(3)

        # 🗡️ 杀招 B：如果杀招 A 被闪避，直接切入画框贴脸开大！
        print("-> 释放杀招 B: 深入画框内部强制点击...")
        if sb.is_element_present(BROAD_CF_SELECTOR):
            try:
                sb.switch_to_frame(BROAD_CF_SELECTOR)
                sb.click("body") # 直接猛击验证码框的身体
                sb.switch_to_default_content()
            except Exception as e:
                sb.switch_to_default_content()
    else:
        print("⚠️ 雷达未扫描到验证框，可能被隐身、或者你的 IP 太干净直接被秒过了。")

    # ================= ⏳ 监控时间变化（你要求的功能） ⏳ =================
    print("死盯 TIME REMAINING，等待时间重置/增加...")
    success = False
    
    # 轮询检查 6 次，每次 3 秒（最多等 18 秒）
    for i in range(6): 
        sb.sleep(3)
        try:
            current_text = sb.get_text('body').upper()
            # 核心逻辑：如果成功加上了 8 小时，那个 "+ 8 HOURS" 的紫色按钮就会消失！
            if "HOURS" not in current_text or "SUCCESS" in current_text:
                print(f"✅ 监控到面板状态已刷新！+8 HOURS 按钮已消失，时间已成功增加！(第 {i+1} 次检查)")
                success = True
                break
            else:
                print(f"⌛ 时间尚未刷新，继续等待 CF 后台确认... ({i+1}/6)")
                # 顺手点掉可能弹出的 Confirm 确认按钮
                sb.execute_script("""
                    var btns = document.querySelectorAll('button');
                    for (var j = 0; j < btns.length; j++) {
                        var txt = btns[j].innerText || btns[j].textContent;
                        if (txt && (txt.includes('确认') || txt.includes('Confirm') || txt.includes('Yes'))) {
                            btns[j].click();
                        }
                    }
                """)
        except:
            pass

    if success:
        print("🎉 续期彻底成功！")
    else:
        print("⚠️ 监控超时，时间似乎没有增加，可能是 CF 验证失败了。")

    # 拍下最终的案发现场发到你的 TG 上
    final_img = f"{email}_final_result.png"
    sb.save_screenshot(final_img)
    send_tg_photo(f"📸 续期流程结束，这是最终的现场快照。", final_img)
    return success

# ================= 主流程 =================
def process_account(account):
    email = account.get('email', '')
    password = account.get('password', '')
    
    print(f"==========================================")
    print(f"👤 开始处理账号: {email}")
    print("==========================================")

    # ---------------- 隔离区 A：尝试克隆 Cookie 秒进 ----------------
    print("▶️ 策略 A: 尝试 CDP 注入 Cookie 免密登录...")
    with SB(uc=True, headless=False, agent=MY_USER_AGENT) as sb:
        sb.driver.set_window_size(1920, 1080)
        
        sb.uc_open_with_tab("about:blank") 
        inject_vip_cookies_via_cdp(sb)
        
        sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/", 10)
        sb.sleep(6)

        if sb.is_element_visible('a[href="/account"]') or sb.is_element_visible('.fa-sign-out-alt'):
            print("✅ 策略 A 成功！克隆身份完美通过验证！")
            return execute_renewal(sb, email)
        else:
            print("⚠️ 策略 A (Cookie) 失效！销毁当前污染的浏览器进程...")
    
    # ---------------- 隔离区 B：开启全新纯净浏览器，硬刚账号密码 ----------------
    print("🔄 启动策略 B: 开启全新纯净浏览器，执行物理登录...")
    with SB(uc=True, headless=False, agent=MY_USER_AGENT) as sb:
        try:
            sb.driver.set_window_size(1920, 1080)
            sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/auth/login", 10)
            sb.sleep(6)
            
            if sb.is_element_present('iframe[src*="cloudflare"]'):
                print("🛡️ 检测到 Cloudflare 盾，执行纯净破解...")
                sb.uc_gui_click_captcha()
                sb.sleep(6) 
            
            USERNAME_SELECTOR = 'input[name="user"], input[name="username"], input[type="email"], input[type="text"]'
            PASSWORD_SELECTOR = 'input[name="password"], input[type="password"]'

            print("等待登录表单渲染...")
            sb.wait_for_element(USERNAME_SELECTOR, timeout=15)
            
            print("填写账号密码...")
            sb.type(USERNAME_SELECTOR, email)
            sb.type(PASSWORD_SELECTOR, password)
            sb.sleep(1)
            sb.click('button[type="submit"], button:contains("Login"), button:contains("LOGIN")')
            print("提交成功，等待后台加载...")
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
    print("✅ 任务处理完毕")

if __name__ == "__main__":
    main()
