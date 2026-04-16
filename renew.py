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
    """👑 隐秘暗杀版：CSS全局屏蔽广告，动态重锁目标规避 Stale Element"""
    print(f"✈️ 正在空降目标服务器: {TARGET_SERVER_URL}")
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
    sb.sleep(8) 

    # 🚀 优雅的全局屏蔽术：不再暴力 remove，而是用 CSS 让它们在视觉上蒸发
    stealth_nuke_js = """
        // 1. 注入全局 CSS：直接从根本上隐藏所有非 CF 的 iframe
        if (!document.getElementById('anti-ad-style')) {
            let style = document.createElement('style');
            style.id = 'anti-ad-style';
            style.innerHTML = `
                iframe:not([src*="cloudflare"]):not([src*="turnstile"]) { display: none !important; width: 0 !important; height: 0 !important; }
            `;
            document.head.appendChild(style);
        }

        // 2. 隐藏那些明显的弹窗和关闭按钮
        document.querySelectorAll('a, button, span, div').forEach(el => {
            let txt = (el.innerText || '').trim().toUpperCase();
            if (txt === 'CLOSE' || txt === 'X' || txt.includes('DO NOT SELL') || txt.includes('PERSONAL INFORMATION')) {
                el.style.display = 'none';
            }
        });
        
        // 3. 抹杀底部的“白色幽灵”（图1中的白色横幅）
        document.querySelectorAll('div').forEach(d => {
            let style = window.getComputedStyle(d);
            // 如果它是悬浮/绝对定位，且背景是白色的，直接隐形
            if (style.position === 'fixed' || style.position === 'absolute') {
                if (style.backgroundColor.includes('255, 255, 255') || style.zIndex > 100) {
                    d.style.display = 'none';
                }
            }
        });
    """

    print("🔄 开始寻找并点击续期按钮...")
    success = False

    sb.execute_script(stealth_nuke_js)
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

        print("🧹 战中清理：粉碎白色幽灵与隐私弹窗，确保屏幕绝对整洁...")
        sb.execute_script(stealth_nuke_js)
        sb.sleep(2)

        # ================= 🚨 破解 Cloudflare Turnstile 🚨 =================
        print("🛡️ 锁定 CF 验证框！执行防 Stale Element 战术...")
        try:
            # 👁️ 强制视角锁定：确保视野在网页中间
            sb.execute_script("""
                var divs = document.querySelectorAll('div');
                for(var i=0; i<divs.length; i++) {
                    var text = (divs[i].innerText || "").toUpperCase();
                    if(text.includes('SECURITY CHECK') || text.includes('VERIFY YOU ARE HUMAN')) {
                        divs[i].scrollIntoView({block: 'center'});
                        break;
                    }
                }
            """)
            sb.sleep(2)

            # 【重要修复】：废弃会引发重载的“强制显影术”，直接寻找并清障
            iframes = sb.driver.find_elements("tag name", "iframe")
            target_frame = None
            for f in iframes:
                w = f.size.get('width', 0)
                h = f.size.get('height', 0)
                if 200 <= w <= 400 and 50 <= h <= 200:
                    target_frame = f
                    break
                    
            if not target_frame:
                raise Exception("页面上未能找到符合 CF 尺寸的 iframe。")

            # 🔪 像素级清障（仅删除挡在前面的透明玻璃，绝不修改 iframe 本身）
            sb.execute_script("""
                var iframe = arguments[0];
                var rect = iframe.getBoundingClientRect();
                var x = rect.left + 30; 
                var y = rect.top + (rect.height / 2);
                var overEl = document.elementFromPoint(x, y);
                if (overEl && overEl !== iframe && overEl.tagName !== 'BODY' && overEl.tagName !== 'HTML') {
                    overEl.style.display = 'none';
                }
            """, target_frame)
            sb.sleep(1)

            # 📸 [调试神器] 截取开枪前的纯净视野
            aim_img = f"{email}_aiming.png"
            sb.save_screenshot(aim_img)
            send_tg_photo(f"📸 狙击手已就位，防抖开枪前快照：", aim_img)

            # 【核心修复】：为了防止上一秒的清障导致 DOM 刷新，我们在此刻**重新抓取一次 iframe**！
            iframes = sb.driver.find_elements("tag name", "iframe")
            fresh_target = None
            for f in iframes:
                w = f.size.get('width', 0)
                h = f.size.get('height', 0)
                if 200 <= w <= 400 and 50 <= h <= 200:
                    fresh_target = f
                    break

            if fresh_target:
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(sb.driver)
                
                w = fresh_target.size.get('width', 300)
                if w > 500: w = 300 
                
                offset_1 = -int(w * 0.40)
                offset_2 = -int(w * 0.35)
                offset_3 = -int(w * 0.30)
                
                print(f"💥 目标已重锁！启动三连发霰弹扫射！偏移量: {offset_1}, {offset_2}, {offset_3}")
                actions.move_to_element(fresh_target).move_by_offset(offset_1, 0).click().pause(0.5)\
                       .move_to_element(fresh_target).move_by_offset(offset_2, 0).click().pause(0.5)\
                       .move_to_element(fresh_target).move_by_offset(offset_3, 0).click().perform()
                
                print("⏳ 弹夹打空，等待 8 秒校验响应...")
                sb.sleep(8)
            else:
                print("⚠️ 重新抓取目标失败，目标已逃逸！")
            
        except Exception as e:
            print(f"⚠️ 坐标打击异常: {e}")

        success = True 

    print("✅ 尝试点击可能存在的最终确认(Confirm)按钮...")
    sb.execute_script("""
        var btns = document.querySelectorAll('button');
        for (var i = 0; i < btns.length; i++) {
            var txt = (btns[i].innerText || "").toUpperCase();
            if (txt.includes('确认') || txt.includes('CONFIRM') || txt.includes('YES') || txt.includes('RENEW')) {
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
