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
        "value": "sd8ZcnPYOky1A2nTEgPoxCVBCXePjMCPOoirmuS2FeM-1776304100-1.2.1.1-gx7fa0twi6moUg_VtGGgDcZYvoghfYVNt96AQhQZTM3nDyR2L8SjUXHyb8GK1Bec3ASur.Dq.TuJ0x9JsAolQA6b_fyjHqZbZTkKCGfzp_V20.JlqhiMEvzwHh0EPoRDD_RnWn1CV6jey0ymtdEjku_G7gNQuiROWILMURmjY6RnD..hHMArUovlU3bYgH0K2jZD2oBjzRi2Ob.4CCvubqrKVSb0Pv3s3GbZTVYSBZA.lkFBAJykeqJwDDzRbndXwIxlZfXn.toQkEsAxs_EzwUjNyx5KmT9UjGfz10ErwOtdgIn6PrgJI4sEb4rkIJwVA1l82hH_ATQqrmvKKalhA"
    },
    {
        "name": "pterodactyl_session", 
        "value": "eyJpdiI6IkdydGtRK2s0TVNvSytqT0h1T2ZUWEE9PSIsInZhbHVlIjoiRW9kOFlKVXU5OTJyanIzcUdHR0NPQ0QreEhDdEhMOFhtR0hDMVNlYkhMa09QV0J0NXlDd0wyZjl3R0pFNlg3NEVRYkcvcWNzU1FROHNxdlBVQ082NWtzdlNCTEs5RVpoRk1JRHBiTGtxTEg5Y282b01oLzlJdEFHaExHY1JVb2kiLCJtYWMiOiI3ZjQ2OTRhMTM4MTE0NmZiNjUyYjNhZDljYmM1M2Y5OTI1ZGEwYmM1NjJkZWVjODA2ZWFlMDk3ZDc3Y2EwZTY1IiwidGFnIjoiIn0%3D"
    },
    {
        "name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", 
        "value": "eyJpdiI6IlhSUkwxYit2L1dmcDFZTEtVOFVPUWc9PSIsInZhbHVlIjoidzNBVC9CYnJYZXFUM3VtUGVqK2dJMnBnSDJCVnd5Nkt0S3pkUDlHWFFsNzNTckZLam1xT0NvQlE1ZnVLZHU0cGlkaXcvZDVkS01TOTJ1NjhaUStyNjB5NHFabmdUVzRoZ1d1UzdRZnJQNG9HOEVBWnNibnNZUjhSOUtxVnZMMUQvdzVmVHNpbE52RW11bXBBcmJseEZTeXNzZlpvL2xIM1JHbXM5a1ZVSHVUaHVyVDkzQm5XWE5MMUdTeXowVzdtbndsS0ZXRHg5TWFzVTFIaDhqVjJYb1VvUGo0OWJIaEV0MVA2L2RTOGd5WT0iLCJtYWMiOiIzMWI1NzFmZGNlZTM0YjMwY2ViOWYyZDg2NGNkYmUwNzc3YmQzMzdhZjM3MDczZjIyNWY3NmYxNzk1NGJkNGNhIiwidGFnIjoiIn0%3D"
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
    逻辑更正版：
    1. 第一时间清理现场广告。
    2. 第一时间寻找并点击续期按钮。
    3. 诱导 CF 弹出并执行精准打击。
    4. 截图并立即退出。
    """
    print(f"✈️ 正在空降目标服务器: {TARGET_SERVER_URL}")
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
    
    # 给页面基础加载一点时间
    sb.sleep(5)

    # 🚀 广告“侦测与处决”脚本：点击 Close 并清理蒙层
    nuke_ads_js = """
        // 1. 寻找所有的 "Close" 或 "X" 按钮并点击
        document.querySelectorAll('button, a, span, div[role="button"]').forEach(el => {
            let txt = (el.innerText || '').trim().toUpperCase();
            if (txt === 'CLOSE' || txt === 'X' || txt.includes('DISMISS')) {
                try { el.click(); console.log('已点击广告关闭按钮'); } catch(e){}
            }
        });
        // 2. 物理移除大面积的固定蒙层 (防止拦截点击)
        document.querySelectorAll('div').forEach(d => {
            let s = window.getComputedStyle(d);
            if (s.position === 'fixed' && parseInt(s.zIndex) > 100 && d.offsetWidth > window.innerWidth * 0.5) {
                // 排除 CF 自身的容器
                if (!d.innerHTML.includes('cloudflare') && !d.innerHTML.includes('turnstile')) {
                    try { d.remove(); } catch(e){}
                }
            }
        });
    """

    print("🧹 正在进行进场清障（广告扫描）...")
    sb.execute_script(nuke_ads_js)

    # 🚀 第一时间点击续期按钮
    print("🎯 正在执行：第一时间锁定并点击续期按钮...")
    button_clicked = sb.execute_script("""
        var els = document.querySelectorAll('button, a, div[role="button"]');
        for (var i = 0; i < els.length; i++) {
            var txt = (els[i].innerText || "").toUpperCase().trim();
            // 匹配 RENEW 或 HOURS，排除无关按钮
            if ((txt.includes('HOURS') || txt.includes('RENEW')) && !txt.includes('DELETE') && txt.length < 30) {
                els[i].scrollIntoView({block: "center"});
                els[i].click();
                return true;
            }
        }
        return false;
    """)

    if not button_clicked:
        print("⚠️ 未发现续期按钮，可能已处于冷却中。")
    else:
        print("✅ 续期按钮已点击！诱导 CF 验证框弹出...")
        sb.sleep(6) # 给 CF 加载时间

    # 🚀 解决 CF 人机验证（最高优先级）
    print("🛡️ 正在执行：解决 CF 人机验证...")
    # 再次清理可能在点击后弹出的广告
    sb.execute_script(nuke_ads_js)
    sb.sleep(2)

    try:
        # 寻找符合尺寸的 CF iframe (通常为 300x65 或宽 300 左右)
        iframes = sb.driver.find_elements("tag name", "iframe")
        target_frame = None
        for f in iframes:
            w = f.size.get('width', 0)
            h = f.size.get('height', 0)
            if 280 <= w <= 320 and 60 <= h <= 150:
                target_frame = f
                break
        
        if target_frame:
            print(f"💥 发现 CF 验证框 ({target_frame.size['width']}x{target_frame.size['height']})")
            sb.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_frame)
            sb.sleep(2)
            
            # 使用 ActionChains 执行相对坐标点击 (向左偏移以击中复选框)
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(sb.driver)
            offset_x = -int(target_frame.size['width'] * 0.35)
            actions.move_to_element(target_frame).move_by_offset(offset_x, 0).click().perform()
            print(f"🎯 坐标打击已完成 (偏移量 {offset_x})，等待服务器响应...")
            sb.sleep(8) # 等待校验通过
        else:
            print("❓ 视野内未发现符合尺寸的 CF 验证框，可能已自动通过。")
    except Exception as e:
        print(f"❌ CF 处理异常: {e}")

    # 🚀 截图撤退
    print("📸 正在保存执行现场并准备退出...")
    final_img = f"{email}_process.png"
    sb.save_screenshot(final_img)
    send_tg_photo(f"✅ 续期流程已走完。账号: {email}", final_img)
    
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
