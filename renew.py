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
    """👑 最终破幻版：无视系统可见性伪装，强制显影并精准打击"""
    print(f"✈️ 正在空降目标服务器: {TARGET_SERVER_URL}")
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
    sb.sleep(8) 

    # 🚀 智能防空火炮 JS：清理弹窗、广告、外壳
    nuke_ads_js = """
        document.querySelectorAll('a, button, span, div').forEach(el => {
            let txt = (el.innerText || '').trim().toUpperCase();
            if (txt === 'CLOSE' || txt === 'X' || txt.includes('DO NOT SELL') || txt.includes('PERSONAL INFORMATION') || txt.includes('2 EASY STEPS')) {
                try { el.click(); } catch(e){}
                try { el.remove(); } catch(e){}
            }
        });
        
        document.querySelectorAll('iframe').forEach(f => {
            if (f.offsetWidth > 400 || f.offsetHeight > 200) {
                let src = (f.src || '').toLowerCase();
                if (!src.includes('cloudflare') && !src.includes('turnstile')) {
                    try { f.remove(); } catch(e){}
                }
            }
        });
        
        document.querySelectorAll('div').forEach(d => {
            let rect = d.getBoundingClientRect();
            if (rect.width > window.innerWidth * 0.7 && rect.height > 50 && rect.top > window.innerHeight * 0.5) {
                if (!d.innerHTML.includes('cloudflare') && !d.innerHTML.includes('turnstile') && !d.innerHTML.includes('RENEW')) {
                    try { d.remove(); } catch(e){}
                }
            }
        });
    """

    print("🔄 开始寻找并点击续期按钮...")
    success = False

    sb.execute_script(nuke_ads_js)
    sb.sleep(2)

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

        print("🧹 战中清理：粉碎遗留躯壳与隐私弹窗，确保屏幕整洁...")
        sb.execute_script(nuke_ads_js)
        sb.sleep(2)

        # ================= 🚨 破解 Cloudflare Turnstile 🚨 =================
        print("🛡️ 锁定 CF 验证框！无视 is_displayed 伪装，只认尺寸！")
        try:
            iframes = sb.driver.find_elements("tag name", "iframe")
            target_frame = None
            
            for idx, f in enumerate(iframes):
                w = f.size.get('width', 0)
                h = f.size.get('height', 0)
                # 🔪 致命改动：移除了 visible 检查。只要不是 0x0 的隐藏像素，就是它！
                if w > 10 and h > 10:
                    target_frame = f
                    print(f"🎯 破除伪装！强行锁定 iframe [{idx}] (尺寸 {w}x{h}) 作为打击对象！")
                    break
                    
            if not target_frame:
                raise Exception("活见鬼，页面上连一个有实体的 iframe 都没有了。")

            # 🔪 强制显影术：如果 Selenium 认为它不可见，ActionChains 可能会拒绝点击。
            # 我们用 JS 强行把它和它的父节点属性全部改写为绝对可见！
            sb.execute_script("""
                var iframe = arguments[0];
                iframe.style.display = 'block';
                iframe.style.visibility = 'visible';
                iframe.style.opacity = '1';
                if(iframe.parentElement) {
                    iframe.parentElement.style.display = 'block';
                    iframe.parentElement.style.visibility = 'visible';
                    iframe.parentElement.style.overflow = 'visible';
                }
                iframe.scrollIntoView({block: 'center'});
            """, target_frame)
            sb.sleep(2)
            
            # 🔪 像素级清障
            sb.execute_script("""
                var iframe = arguments[0];
                var rect = iframe.getBoundingClientRect();
                var x = rect.left + 30; 
                var y = rect.top + (rect.height / 2);
                var overEl = document.elementFromPoint(x, y);
                if (overEl && overEl !== iframe && overEl.tagName !== 'BODY' && overEl.tagName !== 'HTML') {
                    overEl.remove();
                }
            """, target_frame)
            sb.sleep(1)

            # 🎯 发动内部坐标点击
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(sb.driver)
            
            w = target_frame.size.get('width', 300)
            if w > 500: w = 300 
            
            offset_x = -int(w * 0.35)
            actions.move_to_element(target_frame).move_by_offset(offset_x, 0).click().perform()
            
            print(f"🎯 内部坐标穿甲弹发射 (横向偏移 {offset_x})！等待 8 秒校验...")
            sb.sleep(8)
            
        except Exception as e:
            print(f"⚠️ 坐标打击异常: {e}")

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
