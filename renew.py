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
    """终极实战版本：提前装填弹药 + 抹除广告外层白框躯壳"""
    print(f"✈️ 正在空降目标服务器: {TARGET_SERVER_URL}")
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
    sb.sleep(8) 

    # 🚀 智能防空火炮 JS：增加对“底部固定容器(躯壳)”的连根拔起逻辑
    nuke_ads_js = """
        // 1. 常规清理：点击所有明确的 Close 按钮
        document.querySelectorAll('a, button, span, div').forEach(el => {
            let txt = (el.innerText || '').trim().toUpperCase();
            if (txt === 'CLOSE' || txt === 'X') { try { el.click(); } catch(e){} }
        });
        
        // 2. 核心：按尺寸识别 iframe (保护小尺寸 CF，杀大尺寸广告)
        document.querySelectorAll('iframe').forEach(f => {
            if (f.offsetWidth > 0 && f.offsetWidth <= 400 && f.offsetHeight > 0 && f.offsetHeight <= 120) {
                return; 
            }
            let src = (f.src || '').toLowerCase();
            if (!src.includes('cloudflare') && !src.includes('turnstile')) {
                try { f.remove(); } catch(e){}
            }
        });
        
        // 3. 抹除躯壳：强制剥离高层级蒙层，以及固定在底部的可疑白色容器
        document.querySelectorAll('div').forEach(d => {
            let style = window.getComputedStyle(d);
            // 如果它固定在底部 (通常是底部横幅广告的容器)
            if ((style.position === 'fixed' || style.position === 'absolute') && style.bottom === '0px') {
                if (!d.innerHTML.includes('cloudflare') && !d.innerHTML.includes('turnstile')) {
                    try { d.remove(); } catch(e){}
                }
            }
            // 如果层级特别高且面积巨大
            if (style.zIndex !== 'auto' && parseInt(style.zIndex) > 900) {
                if (d.offsetWidth > window.innerWidth * 0.5 && d.offsetHeight > window.innerHeight * 0.5) {
                    try { d.remove(); } catch(e){}
                }
            }
        });
    """

    print("🔄 开始寻找并点击续期按钮...")
    success = False

    sb.execute_script(nuke_ads_js)
    sb.sleep(2)

    # 🎯 锁定并点击目标按钮
    clicked = sb.execute_script("""
        var els = document.querySelectorAll('button, a, div[role="button"]');
        for (var i = 0; i < els.length; i++) {
            var txt = (els[i].innerText || "").toUpperCase().trim();
            if ((txt.includes('HOURS') || txt.includes('RENEW') || txt.includes('ADD TIME')) 
                && !txt.includes('UPGRADE') && !txt.includes('DELETE') && txt.length > 0 && txt.length < 30) {
                els[i].scrollIntoView({block: "center"});
                els[i].click();
                return true;
            }
        }
        return false;
    """)

    if not clicked:
        print("✅ 扫描完毕！当前无需续期，或处于 RENEWAL COOLDOWN 冷却中。")
        success = True
    else:
        print("🎯 续期按钮已点击！")
        print("⏳ 等待敌方阵列与 CF 验证框展开 (6秒)...")
        sb.sleep(6) 

        # 🛡️ 战中清理：保留小尺寸 CF，杀掉大尺寸广告及白框
        print("🧹 战中清理：启动尺寸鉴别级清场，确保视野绝对清晰...")
        sb.execute_script(nuke_ads_js)
        sb.sleep(2)

        # ================= 🚨 破解 Cloudflare Turnstile 🚨 =================
        print("🛡️ 呼叫原生穿甲弹 (由于已在 YAML 预装 pyautogui，此次将瞬间击发)...")
        try:
            sb.uc_gui_click_captcha()
            print("⏳ 穿甲弹已发射，等待 CF 服务器校验响应 (8秒)...")
            sb.sleep(8)
        except Exception as e:
            print(f"⚠️ 原生穿甲弹遇阻: {e}，启动物理坐标盲射...")
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                iframes = sb.find_elements('iframe')
                for f in iframes:
                    w = f.size.get('width', 0)
                    h = f.size.get('height', 0)
                    if 200 < w < 400 and 40 < h < 120:
                        sb.execute_script("arguments[0].scrollIntoView({block: 'center'});", f)
                        sb.sleep(1)
                        actions = ActionChains(sb.driver)
                        actions.move_to_element_with_offset(f, -int(w * 0.35), 0).click().perform()
                        print("🎯 物理盲射命中目标！等待 8 秒...")
                        sb.sleep(8)
                        break
            except Exception as e2:
                print(f"-> 物理盲射失败: {e2}")

        success = True 

    print("✅ 尝试点击可能存在的最终确认(Confirm)按钮...")
    sb.execute_script("""
        var btns = document.querySelectorAll('button');
        for (var i = 0; i < btns.length; i++) {
            var txt = (btns[i].innerText || "").toUpperCase();
            if (txt.includes('确认') || txt.includes('CONFIRM') || txt.includes('YES')) {
                btns[i].click();
            }
        }
    """)
    sb.sleep(3) 

    print("🎉 任务环节终结，请查收最终状态快照。")
    final_img = f"{email}_final_result.png"
    sb.save_screenshot(final_img)
    send_tg_photo(f"📸 账号 {email} 续期执行完毕，最终现场快照。", final_img)
    
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
