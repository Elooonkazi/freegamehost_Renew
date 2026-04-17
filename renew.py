import os
import json
import time
import re
import requests
from seleniumbase import SB

# ================= 🚨 配置区 🚨 =================

MY_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"

MY_COOKIES = [
    {"name": "cf_clearance", "value": "TdelI2Xb5bYWDes4luF8ajPwgqaeqBAtUfjnlayhWu4-1776387100-1.2.1.1-IhdIFAqBhimcYPFbG570a65t1f77aq8MN1OPtzWLkos9JAL8vzYlDIpLMu9bW6OEwOOz6S5WEw4GL5bq2358GEHANBynJIZ.QeAw0ZooKuIl9kcasJnzxd_bwvKkWjd948LERW90aFZu3fmNie9AiN67tn6LX4UPDiuOrknM1CbPaJOvlMReCeazYpbVQTkvrXdAnhC8VKJk5hsZ5UzNtrL6_p.M6NGIHcFHRJGdVmKjp51ht6okWHhzPslQC4pKvH3Q.vz8o7c.Y1z9TvON1xJN47QVeLMwTqNp7xYLav0UebnjWqqnE7cQ7NDL2h6vD15Hyf7GtsawWjBo_vkvDw"},
    {"name": "pterodactyl_session", "value": "eyJpdiI6InZjR3k5YXc0VllNcmhDOWROUk44R0E9PSIsInZhbHVlIjoiaE1ab1Z3V2NaZlFMN2JzMlhkUjRMRjBIMnozNmVOR3piMUorYW9JU2dVUDZvY1NtZExqT01qOGJUZ2Uzc0d4Q3RHRGY5YVJ6aVRsYkNrS0VuajVuUFhteHcwVDZPUjV4UDk4MHp5WUJCdUFrbThnbWY1SlFNQkZTcDZVa3d3clAiLCJtYWMiOiIzNDgyNjJhOTJlNmFmMjgzMjEzNTFiNDA2ZTFjMWNhNThmY2UxMzcwN2FkOTg2ODFjZjc5MmQ2MDc4MmJkNzgwIiwidGFnIjoiIn0%3D"},
    {"name": "XSRF-TOKEN", "value": "eyJpdiI6IjdFWUpIdW01dU9YdUJjd2JuLzhCMnc9PSIsInZhbHVlIjoiMUNUWG1zeFNQTzJmT0xnd1ZPSkVmbXJJL2dVMEpnMmxzMzgvZ3BxNEh5RVZpK3JTamdRL3NZVXZjOGxCRk8vNU5uNWJjOG8xeUxNekRNZnAzRXVrbGYwYnBtZzN0c1FSTStIUkVrUHByMTRFUVBDNGxmTDdNVTNRVWtzbkkrelEiLCJtYWMiOiJjNmVkZjY1NjA4ZjA2NjExNzlkMDc5YmNmMWMwOGU1ZGFlODVmYmE5NTBjMDBjNDBjYTg4ZDU2ODk4YWFkMzYxIiwidGFnIjoiIn0%3D"},
    {"name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", "value": "eyJpdiI6IlFsaVROSllyc0d4UGtXZlN3b1BWNVE9PSIsInZhbHVlIjoiMlNuNHd5UVJGdFdYYjFaMnZxYWZZcklOVi81ai9nNTNmQTlPdFlUTSsrODRlQkFGVzlRMGg3aE9mcTU3T0djNWhnWjhOOHdQVDVTOXB0LzFhK0E5S3RLTDNIbzN2WTlFU1VnZmJSMWQzSGU3dHhyNVJmczBWQUtxQnQ5bjU1Y3dBRlF5R3Q1eWpiUGVmK0dWZytPeUR1d2VtZk9aTFNmVGQwZVRjNFhiTVB5T29MOWpOR2h4dzRncHZwVS9oazJVanZjUld1cllscjVwMThJSm92YnV1a2VOTllpSU10amdhWW1BbVgwVkY3WT0iLCJtYWMiOiJjOTliNTYwYjE1MmI0NDFhYmRiMTIyZWJiMjYzYzVjYTVjNTdkNzMyNDk1NzViMmRjMWE4ZDUxZDhhNTA2ZjkxIiwidGFnIjoiIn0%3D"}
]

FGH_ACCOUNT_ENV = os.environ.get('FGH_ACCOUNT', '[]')
TG_BOT_ENV = os.environ.get('TG_BOT', '')
TARGET_SERVER_URL = "https://panel.freegamehost.xyz/server/41ed8b6e"

# 设定告警阈值：低于此时间（分钟）将发送 TG 截图告警（目前设为 3 小时 = 180 分钟）
ALERT_THRESHOLD_MINUTES = 180  

def send_tg_photo(msg, photo_path=None):
    if not TG_BOT_ENV: return
    try:
        chat_id, bot_token = TG_BOT_ENV.split(':', 1)
        if photo_path and os.path.exists(photo_path):
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            with open(photo_path, 'rb') as f:
                requests.post(url, data={"chat_id": chat_id, "caption": msg}, files={"photo": f})
        else:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": msg})
    except Exception as e:
        print(f"Telegram 推送失败: {e}")

def inject_cookies(sb):
    print("🚀 正在注入身份 Cookie...")
    for c in MY_COOKIES:
        try:
            sb.driver.execute_cdp_cmd('Network.setCookie', {
                'name': c['name'], 'value': c['value'],
                'domain': 'panel.freegamehost.xyz', 'path': '/', 'secure': True
            })
        except:
            pass

def check_server_status(sb, username):
    print(f"✈️ 正在空降目标服务器 (账号: {username})...")
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 15)
    sb.sleep(8)

    if "login" in sb.get_current_url().lower():
        error_msg = f"❌ [监控告警] 账号 {username} 身份已失效，请更新 Cookie！"
        print(error_msg)
        send_tg_photo(error_msg)
        return False

    print("🔍 正在扫描剩余时间...")
    # 获取页面上纯文本内容，避免被隐藏的 HTML 标签干扰
    page_text = sb.get_text("body")
    
    # 终极防误伤正则：必须是 00:00:00 格式，且后面紧跟着 HH : MM : SS 或其变体
    time_match = re.search(r'(\d{2}):(\d{2}):(\d{2})\s*(?i)HH\s*:\s*MM\s*:\s*SS', page_text)
    
    # 如果上面的没匹配到，试试找 "TIME REMAINING" 后面的时间
    if not time_match:
        time_match = re.search(r'(?i)TIME REMAINING\s*(\d{2}):(\d{2}):(\d{2})', page_text)

    if time_match:
        h, m, s = map(int, time_match.groups())
        total_minutes = h * 60 + m
        print(f"✅ 当前真实剩余时间: {h}小时 {m}分钟")
        
        if total_minutes < ALERT_THRESHOLD_MINUTES:
            # 触发告警：截图并发送
            screenshot_path = f"{username}_alert.png"
            sb.save_screenshot(screenshot_path)
            
            alert_msg = (
                f"🚨 你的免费服务器快到期了！\n\n"
                f"👤 账号：{username}\n"
                f"⏳ 真实剩余：{h}小时 {m}分钟\n\n"
                f"👉 立即点击下方链接手动续期：\n"
                f"{TARGET_SERVER_URL}"
            )
            send_tg_photo(alert_msg, screenshot_path)
            print("📸 阈值触发，已截图并发送 TG 告警！")
        else:
            print("🟢 剩余时间充足，继续潜水。")
    else:
        print("⚠️ 未能在页面中精准匹配到倒计时面板，可能布局已更新。")
        # 如果找不到时间，也发个截图告警，方便排查
        fail_path = f"{username}_fail.png"
        sb.save_screenshot(fail_path)
        send_tg_photo(f"⚠️ [监控异常] 账号 {username} 未找到倒计时，请查看截图确认状态。", fail_path)
        
    return True

def main():
    try:
        accounts = json.loads(FGH_ACCOUNT_ENV)
    except:
        print("❌ 账户数据解析失败，请检查 Secrets")
        return

    for acc in accounts:
        username = acc.get('username', 'My renqi')
        print(f"\n--- 监控进程启动: {username} ---")
        
        # 监控脚本推荐使用 headless=True（无头模式），因为不需要真实鼠标点击，跑得更快且节省 GitHub 资源
        with SB(uc=True, headless=True, agent=MY_USER_AGENT) as sb:
            # 设置一个标准的 1080p 窗口，保证截图清晰好看
            sb.driver.set_window_size(1920, 1080)
            sb.uc_open_with_tab("about:blank") 
            inject_cookies(sb)
            check_server_status(sb, username)

if __name__ == "__main__":
    main()
