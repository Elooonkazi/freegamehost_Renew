import os
import json
import time
import requests
from seleniumbase import SB

# ================= 配置读取 =================
FGH_ACCOUNT_ENV = os.environ.get('FGH_ACCOUNT', '[]')
TG_BOT_ENV = os.environ.get('TG_BOT', '')

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

# ================= 主流程 =================
def process_account(account):
    email = account.get('email', '')
    password = account.get('password', '')
    TARGET_SERVER_URL = "https://panel.freegamehost.xyz/server/41ed8b6e"
    
    print(f"==========================================")
    print(f"👤 开始处理账号: {email}")
    print("==========================================")

    # 🌟 核心魔法：完全不传代理参数！使用系统底层虚拟网卡！
    print("▶️ 启动 100% 纯净无痕浏览器进行物理硬闯...")
    with SB(uc=True, headless=False) as sb:
        try:
            sb.driver.set_window_size(1920, 1080)
            
            print("前往登录页...")
            sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/auth/login", 10)
            sb.sleep(6)
            
            # 对付可能存在的 5秒盾
            if sb.is_element_present('iframe[src*="cloudflare"]'):
                print("🛡️ 检测到 Cloudflare 盾，执行纯净破解...")
                sb.uc_gui_click_captcha()
                sb.sleep(8) 
            
            print("等待登录表单渲染...")
            sb.wait_for_element('input[type="email"], input[name="email"]', timeout=15)
            
            print("填写账号密码...")
            sb.type('input[type="email"], input[name="email"]', email)
            sb.type('input[type="password"], input[name="password"]', password)
            sb.sleep(1)
            sb.click('button[type="submit"], button:contains("Login")')
            print("提交成功，等待后台加载...")
            sb.sleep(8) 
            
            # ================= 检查登录结果 =================
            if sb.is_element_visible('a[href="/account"]') or sb.is_element_visible('.fa-sign-out-alt'):
                print("✅ 纯净环境验证通过，成功登录！")
            else:
                fatal_img = f"{email}_login_fatal.png"
                sb.save_screenshot(fatal_img)
                send_tg_photo(f"❌ 账号 {email} 登录失败，请看截图。", fatal_img)
                return False

            # ================= 执行续期 =================
            print(f"✈️ 正在空降目标服务器...")
            sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
            sb.sleep(8) 

            page_text = sb.get_text('body').upper()
            if "RENEWAL COOLDOWN" in page_text:
                print("⏳ 目标服务器处于冷却期。")
                cd_img = f"{email}_cooldown.png"
                sb.save_screenshot(cd_img)
                send_tg_photo(f"⏳ FGH 服务器 41ed8b6e 续期冷却中，时间未到。", cd_img)
                return True 

            print("寻找续期按钮...")
            if sb.is_element_visible('button:contains("续期")') or sb.is_element_visible('button:contains("Renew")'):
                sb.click('button:contains("续期"), button:contains("Renew")')
            else:
                try:
                    sb.click('a:contains("续期"), a:contains("Renew"), a:contains("Billing")')
                    sb.sleep(2)
                    sb.click('button:contains("续期"), button:contains("Renew")')
                except:
                    err_img = f"{email}_no_button.png"
                    sb.save_screenshot(err_img)
                    send_tg_photo(f"⚠️ 续期失败：未找到续期按钮。", err_img)
                    return False

            sb.sleep(5)
            if sb.is_element_present('iframe[src*="cloudflare"]'):
                sb.uc_gui_click_captcha()
                sb.sleep(3)

            sb.click('button:contains("确认"), button:contains("Confirm"), button[class*="success"]')
            sb.sleep(4)

            print("🎉 续期操作执行完毕!")
            success_img = f"{email}_success.png"
            sb.save_screenshot(success_img)
            send_tg_photo(f"🎉 恭喜！FGH 服务器 41ed8b6e 续期操作成功！", success_img)
            return True

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
