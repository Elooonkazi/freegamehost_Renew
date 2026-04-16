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
    """🕊️ 温和清障版：停止乱杀 iframe，让 CF 自然生长后执行三连发"""
    print(f"✈️ 正在空降目标服务器: {TARGET_SERVER_URL}")
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
    sb.sleep(8) 

    # 🚀 温和清障术：绝不碰任何 iframe，避免误杀还在发育中的 CF 验证框
    safe_nuke_js = """
        // 1. 隐藏多余的文字弹窗
        document.querySelectorAll('a, button, span, div').forEach(el => {
            let txt = (el.innerText || '').trim().toUpperCase();
            if (txt === 'CLOSE' || txt === 'X' || txt.includes('DO NOT SELL') || txt.includes('PERSONAL INFORMATION') || txt.includes('2 EASY STEPS')) {
                el.style.display = 'none';
            }
        });

        // 2. 仅隐藏底部巨大且恶心的白色容器
        document.querySelectorAll('div').forEach(d => {
            let style = window.getComputedStyle(d);
            if ((style.position === 'fixed' || style.position === 'absolute') && style.bottom === '0px') {
                if (d.offsetWidth > window.innerWidth * 0.5 && (style.backgroundColor.includes('255, 255, 255') || parseInt(style.zIndex) > 10)) {
                    d.style.display = 'none';
                }
            }
        });
    """

    print("🔄 开始寻找并点击续期按钮...")
    success = False

    sb.execute_script(safe_nuke_js)
    sb.sleep(2)

    # 强行把页面卷到中间偏上，防止点击不到
    sb.execute_script("window.scrollTo(0, 300);")

    clicked = sb.execute_script("""
        var els = document.querySelectorAll('button, a, div[role="button"]');
        for (var i = 0; i < els.length; i++) {
            var txt = (els[i].innerText || "").toUpperCase().trim();
            if ((txt.includes('HOURS') || txt.includes('RENEW') || txt.includes('ADD TIME')) 
                && !txt.includes('UPGRADE') && !txt.includes('DELETE') && txt.length > 0 && txt.length < 30) {
                var target = els[i];
                target.scrollIntoView({block: "center", behavior: "instant"});
                target.click();
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
        print("⏳ 停止一切干扰，静静等待 CF 验证框自然生长 (8秒)...")
        sb.sleep(8) 

        print("🧹 战中清理：轻轻扫除弹出的白框...")
        sb.execute_script(safe_nuke_js)
        sb.sleep(2)

        # ================= 🚨 破解 Cloudflare Turnstile 🚨 =================
        print("🛡️ 锁定 CF 验证框！执行最稳妥的 ActionChains 内部坐标打击...")
        try:
            # 强行校准视角，寻找包含关键文本的区块
            sb.execute_script("""
                var divs = document.querySelectorAll('div');
                for(var i=0; i<divs.length; i++) {
                    var text = (divs[i].innerText || "").toUpperCase();
                    if(text.includes('SECURITY CHECK') || text.includes('VERIFY YOU ARE HUMAN') || text.includes('RENEW SERVER')) {
                        divs[i].scrollIntoView({block: 'center'});
                        break;
                    }
                }
                window.scrollBy(0, -150); // 稍微往上移一点点，防止被导航栏遮挡
            """)
            sb.sleep(2)

            iframes = sb.driver.find_elements("tag name", "iframe")
            target_frame = None
            
            print(f"👀 页面上目前共有 {len(iframes)} 个 iframe，正在筛选...")
            for idx, f in enumerate(iframes):
                w = f.size.get('width', 0)
                h = f.size.get('height', 0)
                # 宽容的尺寸匹配：既然我们没删其他 iframe，就靠尺寸严选 CF
                if 200 <= w <= 450 and 40 <= h <= 250:
                    target_frame = f
                    print(f"🎯 确认目标 iframe [{idx}] (尺寸 {w}x{h})")
                    break
                    
            if not target_frame:
                raise Exception("页面上没找到符合尺寸的 iframe。可能是按钮没点成功，或者网络卡顿没加载出来。")

            # 📸 [调试神器] 截取开枪前的纯净视野
            aim_img = f"{email}_aiming.png"
            sb.save_screenshot(aim_img)
            send_tg_photo(f"📸 狙击手已就位，防抖开枪前快照：", aim_img)

            # 🔪 像素级清障（仅移除挡在枪口上的那一层透明薄膜，绝不改动 iframe 自身导致崩溃）
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

            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(sb.driver)
            
            w = target_frame.size.get('width', 300)
            if w > 500: w = 300 
            
            offset_1 = -int(w * 0.40)
            offset_2 = -int(w * 0.35)
            offset_3 = -int(w * 0.30)
            
            print(f"💥 启动三连发霰弹扫射！偏移量: {offset_1}, {offset_2}, {offset_3}")
            actions.move_to_element(target_frame).move_by_offset(offset_1, 0).click().pause(0.5)\
                   .move_to_element(target_frame).move_by_offset(offset_2, 0).click().pause(0.5)\
                   .move_to_element(target_frame).move_by_offset(offset_3, 0).click().perform()
            
            print("⏳ 弹夹打空，等待 8 秒校验响应...")
            sb.sleep(8)
            
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
