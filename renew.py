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
    """真理说服版：彻底放弃 JS 点击，启用纯物理光标霰弹枪火力覆盖！"""
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

    print("🔄 开启最终物理强袭循环 (最多尝试 8 波)...")
    success = False

    # 之前表现完美的战场净化程序（保持不变）
    cleansing_js = """
        document.querySelectorAll('iframe').forEach(f => {
            if (f.offsetWidth > 380 || f.offsetHeight > 380) f.remove();
        });
        document.querySelectorAll('*').forEach(e => {
            let t = (e.innerText || '').toUpperCase().replace(/\\s+/g, '');
            if(t.includes('DOWNLOADEXTENSION') || t.includes('STARTNOW') || t.includes('TRUSTEDSPOT') || t.includes('2EASYSTEPS')) {
                try { e.style.display = 'none'; } catch(err){}
                try { if(e.parentElement) e.parentElement.style.display = 'none'; } catch(err){}
                try { if(e.parentElement.parentElement) e.parentElement.parentElement.style.display = 'none'; } catch(err){}
            }
            if(t === 'CLOSE') {
                try{ e.click(); e.style.display = 'none'; }catch(err){}
            }
        });
        document.querySelectorAll('div').forEach(d => {
            let z = window.getComputedStyle(d).zIndex;
            if (z !== 'auto' && parseInt(z) > 1000) {
                if (d.offsetWidth > window.innerWidth * 0.7 && d.offsetHeight > window.innerHeight * 0.7) {
                    d.style.display = 'none';
                }
            }
        });
    """

    for attempt in range(8):
        print(f"\n--- 🚀 第 {attempt + 1} 波攻势 ---")

        current_text = sb.get_text('body').upper()
        if "HOURS" not in current_text or "SUCCESS" in current_text:
            print("✅ 监控到面板状态已刷新！+8 HOURS 按钮已消失，时间已成功增加！")
            success = True
            break

        print("🧹 战前清理：粉碎一切视觉遮挡...")
        sb.execute_script(cleansing_js)
        sb.sleep(1)

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
        
        print("⏳ 等待 4 秒，诱导敌方弹窗...")
        sb.sleep(4) 

        print("🧹 战间清理：秒杀反击护盾...")
        sb.execute_script(cleansing_js)
        sb.sleep(1)

        # ================= 🚨 物理坐标霰弹枪系统 🚨 =================
        print("🛡️ 确认护盾清除！提取 CF 验证码执行物理枪决...")
        
        try:
            # 引入操作系统级别的物理鼠标控制器
            from selenium.webdriver.common.action_chains import ActionChains
            
            iframes = sb.find_elements("iframe")
            cf_found = False
            for frame in iframes:
                try:
                    w = frame.size.get('width', 0)
                    h = frame.size.get('height', 0)
                    # 经历过清场后，剩下的小画框必然是 CF
                    if 10 < w < 380 and 10 < h < 380:
                        cf_found = True
                        print(f"💥 锁定目标！画框尺寸 {w}x{h}，启动【物理霰弹枪】盲射...")
                        sb.execute_script("arguments[0].scrollIntoView({block: 'center'});", frame)
                        sb.sleep(1)
                        
                        # 第一重火力：官方物理外挂扫射
                        try: sb.uc_gui_click_captcha()
                        except: pass
                        sb.sleep(1)

                        # 🔥 致命武器：纯鼠标坐标偏移连发 (专门击碎 CF 的 JS 免疫装甲)
                        try:
                            actions = ActionChains(sb.driver)
                            # 动态计算左半部分坐标，不管复选框藏在左边哪个像素，通通覆盖！
                            offset_1 = -int(w * 0.4)  # 偏左边缘
                            offset_2 = -int(w * 0.3)  # 偏左四分之一
                            offset_3 = -int(w * 0.2)  # 偏左三分之一
                            
                            actions.move_to_element_with_offset(frame, offset_1, 0).click().pause(0.5)
                            actions.move_to_element_with_offset(frame, offset_2, 0).click().pause(0.5)
                            actions.move_to_element_with_offset(frame, offset_3, 0).click().perform()
                            print("-> 物理霰弹枪横向扫射完毕，完美覆盖复选框区域！")
                        except Exception as e:
                            print(f"霰弹枪卡壳: {e}")
                            
                        # 第三重火力：内部暴力开火兜底
                        try:
                            sb.switch_to_frame(frame)
                            body = sb.driver.find_element("css selector", "body")
                            ActionChains(sb.driver).move_to_element(body).click().perform()
                            sb.switch_to_default_content()
                        except:
                            sb.switch_to_default_content()

                        break # 击毙当前目标即收队
                except Exception as inner_e:
                    pass
        except Exception as e:
            print(f"搜寻画框异常: {e}")

        print("⏳ 弹夹已清空，等待 CF 服务器响应 (6秒)...")
        sb.sleep(6)

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
