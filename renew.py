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
        "value": "CnlHqFiqP3e1HFJ8xvuxaowIxZHOK_ubmdSi.9MUJPE-1776326730-1.2.1.1-UsMtnC.oO4IZZuTJ7sFqOrekwMeSYlPte2s4SSCZiwwPOWVmyRsufSX.yQIWj3W.a2QqDsd2fMzFgtBs05DrwRVsEusfNfRUwV2gTDX_qEUc9NNaphCJME99otOCj3XS23epAm1oZRU4FLMZHEHqsO3vwBCqbgbjhALNAzwS_qqgCt6.uq8VJNRN5FuBNk7BeCW3ei80CutoOtItGU8CSMjKuVyprIVenrlAsaou.qnR668s4aqm.LPCqIUTzI0ZISXJDfMWPSa5HUmO0nVb1l1DosljIgz7NCpj8jZsfhKYGMEP2ZWvpW3E24Pe6e1rBIEoxbgOh2MsR9pzNe_kDA"
    },
    {
        "name": "pterodactyl_session", 
        "value": "eyJpdiI6IlFWcWRrQWFOd0l6TEQyUFpCTHRsUlE9PSIsInZhbHVlIjoiVlg5TmVET1FxdnVJQ1BPeGFyWDZyRnpzV1FTV0JmYnpVNklodTRKbnM4TVA0czE2ZFlVajhGSGoxTFIxNTl3a2wyTmtadkllZi9BN0dRamk2MFdMV3dETlBPck1UV3hIUUdxei9YZ3ZGYzYydm16ZDZjck56eXo5Sk5oMk5FL1UiLCJtYWMiOiJkMzA4Nzg4MWE5YmQ3MTdjNWI5MzE0NWMyMDI3Yzg2MjE2YzgwZWUyMzEyZDA1NDBmYWU4M2JjY2FlMmI4MmU1IiwidGFnIjoiIn0%3D"
    },
    {
        "name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", 
        "value": "eyJpdiI6InFIUjJaTzM4N3hpQkRnaVlBQWhkUFE9PSIsInZhbHVlIjoiZllJVXdld1V1TXFyOTE1SjRDTExXNzgySFpnaG1vVHBlZzhTUzV6RVZpdkZxeDVrdzBlSTJPOWUvWVh6SnF5Ti9KMWI1WEJ0S29vQW14NmRsSWVKRVdBVnVRc0o3QVloMUx2L3B5RDRKU2lGRlZUcU12OHhuZTRlOEhpeWFCM0VwSWxYTUh5aXgvaWZnZkZ1MG9SVlVCZ1RvcGcwUzJzdElZNnRUR2Jhb1lueDg0SVBJWGMrYWdxRnltZFI0WE1mUzgrRkEzYllRd1ZPYldxc3RZQi9yOXVxdThEUGVDcktFWkF6cUQ3WlBuST0iLCJtYWMiOiJlZjZmOGYzNDQyZDhmNmEyOGIyNmQ4M2I1MDNlYTAxYTgwODRlNGU2ZTcwNjAzYWY1MjI5NzJmZTcyNDBlYzY1IiwidGFnIjoiIn0%3D"
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
    """
    极简主线版 (终极修正)：
    秒点续期 -> 废弃名字查找，纯靠体型抓出 CF -> 强制交互爆破 -> 截图退出
    """
    print(f"✈️ 正在空降目标服务器: {TARGET_SERVER_URL}")
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
    sb.sleep(5)

    # 🚀 附带广告扫描：顺手点掉明确挡路的 Close 按钮
    sb.execute_script("""
        document.querySelectorAll('button, a, span, div[role="button"]').forEach(el => {
            let txt = (el.innerText || '').trim().toUpperCase();
            if (txt === 'CLOSE' || txt === 'X' || txt.includes('DISMISS')) {
                try { el.click(); } catch(e){}
            }
        });
    """)

    # 🚀 步骤一：第一时间寻找并点击续期按钮
    print("🎯 第一时间锁定并点击续期按钮...")
    button_clicked = sb.execute_script("""
        var els = document.querySelectorAll('button, a, div[role="button"]');
        for (var i = 0; i < els.length; i++) {
            var txt = (els[i].innerText || "").toUpperCase().trim();
            if ((txt.includes('HOURS') || txt.includes('RENEW')) && !txt.includes('DELETE') && txt.length < 30) {
                els[i].scrollIntoView({block: "center"});
                els[i].click();
                return true;
            }
        }
        return false;
    """)

    if button_clicked:
        print("✅ 续期按钮已点击！等待 CF 验证框展开 (6秒)...")
        sb.sleep(6)

        # 🚀 步骤二：优先解决 CF 人机验证
        print("🛡️ 正在执行：精准寻找并破解 CF 验证框...")
        try:
            # 【核心修正】：废弃按名字查找！直接抓取页面所有 iframe，按尺寸抓人！
            iframes = sb.driver.find_elements("tag name", "iframe")
            target_frame = None
            
            for f in iframes:
                w = f.size.get('width', 0)
                h = f.size.get('height', 0)
                # CF 框的真实尺寸通常在这个范围 (宽度 250~380，高度 50~150)
                if 250 <= w <= 380 and 50 <= h <= 150:
                    target_frame = f
                    break
            
            if target_frame:
                w = target_frame.size['width']
                h = target_frame.size['height']
                print(f"💥 成功通过体型锁定 CF 真身 (尺寸 {w}x{h})")
                
                sb.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_frame)
                sb.sleep(1)
                
                # 🔪 强制交互术：强行解除底层限制，让隐形的替身也得显形接子弹
                sb.execute_script("""
                    arguments[0].style.display = 'block';
                    arguments[0].style.visibility = 'visible';
                    arguments[0].style.opacity = '1';
                    arguments[0].style.pointerEvents = 'auto';
                """, target_frame)
                sb.sleep(1)
                
                # 启动内部坐标系精确点击
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(sb.driver)
                
                offset_x = -int(w * 0.35)
                actions.move_to_element(target_frame).move_by_offset(offset_x, 0).click().perform()
                
                print(f"🎯 鼠标已精准点击复选框 (偏移量 {offset_x})，静候 8 秒等待绿勾...")
                sb.sleep(8)
            else:
                print("❓ 扫描完毕，页面上并未生成符合 CF 尺寸的 iframe。")
                
        except Exception as e:
            print(f"❌ CF 坐标打击发生异常: {e}")
    else:
        print("⚠️ 未发现续期按钮，可能已处于冷却中。")

    # 🚀 步骤三：截图撤退
    print("📸 任务流程结束，正在截图并退出...")
    final_img = f"{email}_process.png"
    sb.save_screenshot(final_img)
    send_tg_photo(f"✅ 账号执行完毕，查看最终结果。账号: {email}", final_img)
    
    return True
    
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
