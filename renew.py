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

def send_tg_msg(msg):
    if not TG_BOT_ENV:
        return
    try:
        chat_id, bot_token = TG_BOT_ENV.split(':', 1)
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": msg})
    except Exception as e:
        print(f"⚠️ TG 通知发送失败: {e}")

# ================= 主流程 =================
def process_account(account):
    email = account.get('email')
    password = account.get('password')
    
    print(f"==========================================")
    print(f"👤 开始处理账号: {email}")
    print(f"==========================================")
    print("🌐 启动浏览器 (GitHub 直连模式)...")

    # 注意这里去掉了 proxy 参数
    with SB(uc=True, headless=False, proxy="socks5://127.0.0.1:10808") as sb:
        try:
            sb.driver.set_window_size(1920, 1080)
            
            print("打开登录页面...")
            sb.uc_open_with_reconnect("https://panel.freegamehost.com/login", 10)
            sb.sleep(2)

            print("填写账号密码...")
            sb.type('input[type="email"], input[name="email"], input[name="username"]', email)
            sb.type('input[type="password"], input[name="password"]', password)
            
            print("提交登录表单...")
            sb.click('button[type="submit"]')
            sb.sleep(5)

            if sb.is_element_visible('a[href="/admin"]') or "panel" in sb.get_current_url():
                print("✅ 登录成功! https://panel.freegamehost.com/")
            else:
                print("❌ 登录失败，可能是被 CF 拦截或账号错误")
                sb.save_screenshot(f"{email}_login_failed.png")
                return False

            print(f"准备续期，当前页面: {sb.get_current_url()}")
            
            server_links = sb.find_visible_elements('a[href^="/server/"]')
            if not server_links:
                print("⚠️ 未找到任何服务器列表。")
                return True
                
            server_urls = [el.get_attribute('href') for el in server_links]

            for srv_url in server_urls:
                print(f"导航到服务器页面: {srv_url}")
                sb.uc_open_with_reconnect(srv_url, 5)
                sb.sleep(3)
                
                try:
                    srv_name = sb.get_text('h1')
                    print(f"服务器名称: {srv_name}")
                except:
                    pass

                print("开始执行续期操作...")
                if sb.is_element_visible('button:contains("续期")') or sb.is_element_visible('button:contains("Renew")'):
                    sb.click('button:contains("续期"), button:contains("Renew")')
                else:
                    sb.click('a:contains("续期"), a:contains("Renew"), a:contains("Billing")')
                    sb.sleep(2)
                    sb.click('button:contains("续期"), button:contains("Renew")')

                print("等待 Turnstile 验证组件加载(最多20s)...")
                sb.sleep(3)

                if sb.is_element_present('iframe[src*="cloudflare"]'):
                    print("执行动作验证...")
                    sb.uc_gui_click_captcha()
                    print("✅ Cloudflare Turnstile 验证通过!")
                    sb.sleep(2)

                print("点击确认续期按钮...")
                sb.click('button:contains("确认"), button:contains("Confirm"), button[class*="success"]')
                sb.sleep(3)

                print("🎉 续期成功!")

        except Exception as e:
            print(f"❌ 运行发生异常: {e}")
            sb.save_screenshot(f"{email}_error.png")
            return False
            
    return True

def main():
    if not ACCOUNTS:
        print("没有账号需要处理。")
        return

    for account in ACCOUNTS:
        success = process_account(account)
        if success:
            send_tg_msg(f"✅ FGH 账号 {account.get('email')} 续期成功！")
        else:
            send_tg_msg(f"❌ FGH 账号 {account.get('email')} 续期失败，请查看截图。")
        time.sleep(5)
        
    print("✅ 任务全部处理完毕")

if __name__ == "__main__":
    main()
