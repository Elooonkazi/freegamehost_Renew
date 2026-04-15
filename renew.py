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
    """上帝模式：强行抓取 CF 验证码并置顶居中，纯物理处决！"""
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

    print("🔄 开启上帝模式循环 (最多尝试 8 波)...")
    success = False

    for attempt in range(8):
        print(f"\n--- 🚀 第 {attempt + 1} 波攻势 ---")

        current_text = sb.get_text('body').upper()
        if "HOURS" not in current_text or "SUCCESS" in current_text:
            print("✅ 监控到面板状态已刷新！+8 HOURS 按钮已消失，时间已成功增加！")
            success = True
            break

        # 1. 寻找并点击续期按钮
        print("🎯 寻找并点击续期按钮 (+8 HOURS)...")
        sb.execute_script("""
            // 顺手隐藏一下烦人的大广告，免得挡住我们的视线
            var divs = document.querySelectorAll('div');
            for(var i=0; i<divs.length; i++) {
                if(divs[i].innerText.includes('DOWNLOAD') || divs[i].innerText.includes('START NOW')) {
                    try { divs[i].style.display = 'none'; } catch(e){}
                }
            }
            
            var btns = document.querySelectorAll('button, div[class*="btn"], div[class*="rounded"]');
            for (var i = 0; i < btns.length; i++) {
                if (btns[i].innerText && btns[i].innerText.includes('HOURS')) {
                    btns[i].scrollIntoView({block: "center"});
                    btns[i].click();
                    break;
                }
            }
        """)
        sb.sleep(5) # 必须等够时间，让 CF 验证码从网络加载出来

        # ================= 🚨 上帝之手：强行提取 CF 并置顶居中 🚨 =================
        print("🛡️ 启动上帝之手：提取 CF 验证码并强行置于屏幕正中央！")
        
        sb.execute_script("""
            var frames = document.querySelectorAll('iframe');
            for(var i=0; i<frames.length; i++) {
                var rect = frames[i].getBoundingClientRect();
                // 只要尺寸是 300x65 附近的，绝对是 CF 验证码 (排除所有的巨型广告和隐藏探针)
                if (rect.width > 250 && rect.width < 350 && rect.height > 50 && rect.height < 100) {
                    frames[i].id = "god_mode_cf"; // 打上专属标记
                    frames[i].style.position = 'fixed';
                    frames[i].style.top = '50%';
                    frames[i].style.left = '50%';
                    frames[i].style.transform = 'translate(-50%, -50%)';
                    frames[i].style.zIndex = '2147483647'; // 最高层级，突破天际，没有任何东西能挡住它
                    frames[i].style.boxShadow = '0 0 0 9999px rgba(0,0,0,0.8)'; // 给周围全部打上黑色遮罩，凸显验证码
                    frames[i].style.border = '3px solid #00FF00'; // 加上绿色瞄准框
                    frames[i].style.display = 'block';
                } else {
                    // 其他所有 iframe 全部物理隐藏，防止任何干扰
                    frames[i].style.display = 'none';
                }
            }
        """)
        sb.sleep(2) # 缓冲一下动画渲染

        # 检查验证码是否成功被我们抓到了屏幕中央
        cf_exists = sb.is_element_present("#god_mode_cf")
        if cf_exists:
            print("🎯 CF 验证码已被强行拖至屏幕中央！执行真人物理处决...")
            
            # 杀招 A：纯正物理鼠标点击（引入 ActionChains）
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                cf_el = sb.driver.find_element("css selector", "#god_mode_cf")
                # 真实的鼠标移动到元素正中心，然后按下左键！这完全模拟了真人的操作。
                ActionChains(sb.driver).move_to_element(cf_el).click().perform()
                print("-> 物理鼠标左键精准狙击完毕！")
            except Exception as e:
                print(f"物理鼠标狙击发生偏差: {e}")

            sb.sleep(2)

            # 杀招 B：内置工具扫尾
            try: sb.uc_gui_click_captcha()
            except: pass

            # 杀招 C：钻入画框盲点
            try:
                sb.switch_to_frame("#god_mode_cf")
                sb.click('body', timeout=1)
                sb.switch_to_default_content()
            except:
                sb.switch_to_default_content()
        else:
            print("⚠️ 本轮未扫描到尺寸匹配的 CF 画框，可能在加载或已被秒过。")

        print("⏳ 破甲弹已倾泻，等待面板后台转圈验证 (5秒)...")
        sb.sleep(5)

        # 5. 点击可能出现的最终确认
        print("✅ 尝试确认可能弹出的最终授权框...")
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
        print("⚠️ 8 波攻势结束，时间依然没有增加。")

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
