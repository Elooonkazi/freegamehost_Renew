import os
import json
import time
import subprocess
import requests
from seleniumbase import SB

# ================= 配置读取 =================
# 从环境变量读取配置，格式要求为 JSON 字符串
FGH_ACCOUNT_ENV = os.environ.get('FGH_ACCOUNT', '[]')
GOST_PROXY_ENV = os.environ.get('GOST_PROXY', '[]')
TG_BOT_ENV = os.environ.get('TG_BOT', '')

try:
    ACCOUNTS = json.loads(FGH_ACCOUNT_ENV)
    PROXIES = json.loads(GOST_PROXY_ENV)
except Exception as e:
    print(f"❌ 环境变量解析失败，请检查 JSON 格式: {e}")
    exit(1)

# ================= 辅助函数 =================
def send_tg_msg(msg):
    """发送 Telegram 机器人通知"""
    if not TG_BOT_ENV:
        return
    try:
        # 假设 TG_BOT 格式为 "chat_id:bot_token"
        chat_id, bot_token = TG_BOT_ENV.split(':', 1)
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": msg})
    except Exception as e:
        print(f"⚠️ TG 通知发送失败: {e}")

def start_gost_proxy(proxy_url, local_port=1080):
    """启动 GOST 将复杂代理转换为本地 socks5"""
    # 先清理可能残留的 gost 进程
    os.system("pkill -f gost")
    time.sleep(1)
    
    cmd = f"./gost -L socks5://127.0.0.1:{local_port} -F {proxy_url}"
    print(f"▶️ 启动本地代理服务...")
    # 后台启动 gost
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3) # 等待代理启动
    return process

def test_proxy(port=1080):
    """测试本地代理是否连通并获取IP"""
    try:
        proxies = {
            "http": f"socks5://127.0.0.1:{port}",
            "https": f"socks5://127.0.0.1:{port}"
        }
        res = requests.get("https://api.ipify.org", proxies=proxies, timeout=10)
        print(f"✅ 测试代理IP... {res.text}")
        return True
    except Exception as e:
        print(f"❌ 代理连通性测试失败: {e}")
        return False

# ================= 主流程 =================
def process_account(account, proxy_url, node_index):
    email = account.get('email')
    password = account.get('password')
    
    print(f"==========================================")
    print(f"👤 开始处理账号: {email}")
    print(f"==========================================")
    print(f"🔄 尝试 节点[{node_index}]...")

    # 1. 启动并测试代理
    gost_process = start_gost_proxy(proxy_url)
    if not test_proxy():
        print("⚠️ 代理无效，跳过该节点")
        gost_process.kill()
        return False

    print("🌐 启动浏览器...")
    print(f"🚀 登录尝试 1/3 (节点[{node_index}])...")

    # 2. 启动 SeleniumBase UC 模式 (配合 xvfb 使用，headless=False 即可)
    # 截图中使用了 xvfb-run，所以浏览器认为自己是有界面的，这能极大提高通过率
    with SB(uc=True, headless=False, proxy="socks5://127.0.0.1:1080") as sb:
        try:
            # 缩放窗口，避免 CF 验证码超出视口
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

            # 检查是否登录成功 (寻找面板特征元素)
            if sb.is_element_visible('a[href="/admin"]') or "panel" in sb.get_current_url():
                print("✅ 登录成功! https://panel.freegamehost.com/")
            else:
                print("❌ 登录失败，请检查账号密码或是否被 CF 拦截拦截")
                sb.save_screenshot(f"{email}_login_failed.png")
                return False

            print(f"准备续期，当前页面: {sb.get_current_url()}")
            
            # 3. 寻找并进入服务器面板页面
            # 获取所有服务器链接
            server_links = sb.find_visible_elements('a[href^="/server/"]')
            if not server_links:
                print("⚠️ 未找到任何服务器列表。")
                return True
                
            server_urls = [el.get_attribute('href') for el in server_links]

            for srv_url in server_urls:
                print(f"导航到服务器页面: {srv_url}")
                sb.uc_open_with_reconnect(srv_url, 5)
                print("等待服务器页面加载...")
                sb.sleep(3)
                
                # 尝试提取服务器名称
                try:
                    srv_name = sb.get_text('h1') # 或者是具体的 class
                    print(f"服务器名称: {srv_name}")
                except:
                    pass

                print("开始执行续期操作...")
                print("点击 续期/重置密码 选项...")
                # 寻找并点击续期按钮或 Tab (请根据实际面板的按钮 class 或 text 调整)
                # Pterodactyl 面板一般会有特定按钮
                if sb.is_element_visible('button:contains("续期")') or sb.is_element_visible('button:contains("Renew")'):
                    sb.click('button:contains("续期"), button:contains("Renew")')
                else:
                    # 如果需要先点击 Tab
                    sb.click('a:contains("续期"), a:contains("Renew"), a:contains("Billing")')
                    sb.sleep(2)
                    sb.click('button:contains("续期"), button:contains("Renew")')

                print("等待 Turnstile 验证组件加载(最多20s)...")
                sb.sleep(3)

                # 4. 核心：处理 Cloudflare Turnstile 验证码
                # 查找是否存在 Turnstile 的 iframe
                if sb.is_element_present('iframe[src*="cloudflare"]'):
                    print("执行动作验证...")
                    print("等待 Verifying 状态更新...")
                    # 模拟真人点击 Turnstile 验证框
                    sb.uc_gui_click_captcha()
                    print("✅ Cloudflare Turnstile 验证通过!")
                    sb.sleep(2)

                print("点击确认续期按钮...")
                # 查找模态框/弹窗中的最终确认按钮
                sb.click('button:contains("确认"), button:contains("Confirm"), button[class*="success"]')
                sb.sleep(3)

                print("🎉 续期成功!")

        except Exception as e:
            print(f"❌ 运行发生异常: {e}")
            # 保存截图供 actions 存档
            sb.save_screenshot(f"{email}_error.png")
            
        finally:
            # 清理代理
            gost_process.kill()
            os.system("pkill -f gost")

def main():
    print(f"解析账号... 获取到 {len(ACCOUNTS)} 个账号。")
    print(f"解析代理... 获取到 {len(PROXIES)} 个节点。")

    if not ACCOUNTS:
        print("没有账号需要处理。")
        return

    # 默认使用第一个代理，如果有多个可以做轮询
    proxy_url = PROXIES[0] if PROXIES else ""

    for idx, account in enumerate(ACCOUNTS):
        success = process_account(account, proxy_url, idx)
        if success:
            send_tg_msg(f"✅ FGH 账号 {account.get('email')} 续期成功！")
        else:
            send_tg_msg(f"❌ FGH 账号 {account.get('email')} 续期失败，请查看 Github Actions 截图。")
        
        time.sleep(5) # 账号之间间隔防封
        
    print("✅ 任务全部处理完毕")

if __name__ == "__main__":
    main()
