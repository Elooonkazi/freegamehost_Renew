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
    """真正的疯狗模式：无视一切前置条件，看见什么点什么！"""
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

    print("🔄 开启无限制火力覆盖循环 (最多尝试 8 波攻势)...")
    success = False

    for attempt in range(8):
        print(f"\n--- 🚀 第 {attempt + 1} 波攻势 ---")

        # 1. 检查是否已经彻底胜利 (加时成功后 HOURS 按钮会消失)
        current_text = sb.get_text('body').upper()
        if "HOURS" not in current_text or "SUCCESS" in current_text:
            print("✅ 监控到面板状态已刷新！+8 HOURS 按钮已消失，时间已成功增加！")
            success = True
            break

        # 2. 广告粉碎机 (无情连点器)
        print("🧹 清理战场广告与弹窗...")
        sb.execute_script("""
            var items = document.querySelectorAll('span, div, a, button');
            for(var i=0; i<items.length; i++) {
                var t = items[i].innerText || "";
                if(t.trim() === 'Close' || t.trim() === 'CLOSE' || t.includes('Not Sell')) {
                    try { items[i].click(); } catch(e){}
                }
            }
        """)
        sb.sleep(1)

        # 3. 寻找并点击续期按钮
        print("🎯 锁定并点击续期按钮 (+8 HOURS)...")
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
        sb.sleep(5) # 必须等够 5 秒，让 CF 完全渲染出来！

        # ================= 🚨 终极核弹 🚨 =================
        # 4. 盲放终极大招：CF 毁灭者 (绝不写 IF 语句判断，直接开大！)
        print("🛡️ 无差别释放 CF 毁灭者...")
        
        # 第一重火力：UC 官方外挂，全屏幕扫描验证码特征并模拟真人点击
        try:
            sb.uc_gui_click_captcha()
            print("💥 UC 真人鼠标物理外挂已触发！")
        except:
            pass
            
        sb.sleep(2)

        # 第二重火力：画框潜入刺杀！只进小尺寸画框，防大广告劫持
        try:
            iframes = sb.find_elements("iframe")
            for frame in iframes:
                try:
                    w = frame.size.get('width', 0)
                    h = frame.size.get('height', 0)
                    # CF 验证码通常是长条形，超过 500x500 的基本是纯广告遮罩，我们不进去
                    if 10 < w < 500 and 10 < h < 500:
                        sb.switch_to_frame(frame)
                        sb.click('body', timeout=1) # 对着白板就是一枪
                        sb.switch_to_default_content()
                except:
                    sb.switch_to_default_content()
        except Exception as e:
            pass

        print("⏳ 破甲弹已发射，等待 CF 服务器转圈圈响应 (5秒)...")
        sb.sleep(5)

        # 5. 点击所有确认按钮
        print("✅ 尝试确认最终授权弹窗...")
        sb.execute_script("""
            var btns = document.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
                var txt = btns[i].innerText || btns[i].textContent;
                if (txt && (txt.includes('确认') || txt.includes('Confirm') || txt.includes('Yes') || txt.includes('Renew'))) {
                    btns[i].click();
                }
            }
        """)
        sb.sleep(3) 

    if success:
        print("🎉 漫长战役终结，续期彻底成功！")
    else:
        print("⚠️ 8 波攻势结束，时间依然没有增加。可能面板 API 宕机或防弹盾过厚。")

    final_img = f"{email}_final_result.png"
    sb.save_screenshot(final_img)
    send_tg_photo(f"📸 续期流程结束，最终现场快照。", final_img)
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
