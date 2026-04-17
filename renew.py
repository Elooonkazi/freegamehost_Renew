import os
import json
import time
import requests
from seleniumbase import SB
from selenium.webdriver.common.action_chains import ActionChains

# ================= 🚨 配置区 🚨 =================

# 1. 浏览器指纹与 Cookie (建议定期更新)
MY_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"

MY_COOKIES = [
    {"name": "cf_clearance", "value": "TdelI2Xb5bYWDes4luF8ajPwgqaeqBAtUfjnlayhWu4-1776387100-1.2.1.1-IhdIFAqBhimcYPFbG570a65t1f77aq8MN1OPtzWLkos9JAL8vzYlDIpLMu9bW6OEwOOz6S5WEw4GL5bq2358GEHANBynJIZ.QeAw0ZooKuIl9kcasJnzxd_bwvKkWjd948LERW90aFZu3fmNie9AiN67tn6LX4UPDiuOrknM1CbPaJOvlMReCeazYpbVQTkvrXdAnhC8VKJk5hsZ5UzNtrL6_p.M6NGIHcFHRJGdVmKjp51ht6okWHhzPslQC4pKvH3Q.vz8o7c.Y1z9TvON1xJN47QVeLMwTqNp7xYLav0UebnjWqqnE7cQ7NDL2h6vD15Hyf7GtsawWjBo_vkvDw"},
    {"name": "pterodactyl_session", "value": "eyJpdiI6InZjR3k5YXc0VllNcmhDOWROUk44R0E9PSIsInZhbHVlIjoiaE1ab1Z3V2NaZlFMN2JzMlhkUjRMRjBIMnozNmVOR3piMUorYW9JU2dVUDZvY1NtZExqT01qOGJUZ2Uzc0d4Q3RHRGY5YVJ6aVRsYkNrS0VuajVuUFhteHcwVDZPUjV4UDk4MHp5WUJCdUFrbThnbWY1SlFNQkZTcDZVa3d3clAiLCJtYWMiOiIzNDgyNjJhOTJlNmFmMjgzMjEzNTFiNDA2ZTFjMWNhNThmY2UxMzcwN2FkOTg2ODFjZjc5MmQ2MDc4MmJkNzgwIiwidGFnIjoiIn0%3D"},
    {"name": "XSRF-TOKEN", "value": "eyJpdiI6IjdFWUpIdW01dU9YdUJjd2JuLzhCMnc9PSIsInZhbHVlIjoiMUNUWG1zeFNQTzJmT0xnd1ZPSkVmbXJJL2dVMEpnMmxzMzgvZ3BxNEh5RVZpK3JTamdRL3NZVXZjOGxCRk8vNU5uNWJjOG8xeUxNekRNZnAzRXVrbGYwYnBtZzN0c1FSTStIUkVrUHByMTRFUVBDNGxmTDdNVTNRVWtzbkkrelEiLCJtYWMiOiJjNmVkZjY1NjA4ZjA2NjExNzlkMDc5YmNmMWMwOGU1ZGFlODVmYmE5NTBjMDBjNDBjYTg4ZDU2ODk4YWFkMzYxIiwidGFnIjoiIn0%3D"},
    {"name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", "value": "eyJpdiI6IlFsaVROSllyc0d4UGtXZlN3b1BWNVE9PSIsInZhbHVlIjoiMlNuNHd5UVJGdFdYYjFaMnZxYWZZcklOVi81ai9nNTNmQTlPdFlUTSsrODRlQkFGVzlRMGg3aE9mcTU3T0djNWhnWjhOOHdQVDVTOXB0LzFhK0E5S3RLTDNIbzN2WTlFU1VnZmJSMWQzSGU3dHhyNVJmczBWQUtxQnQ5bjU1Y3dBRlF5R3Q1eWpiUGVmK0dWZytPeUR1d2VtZk9aTFNmVGQwZVRjNFhiTVB5T29MOWpOR2h4dzRncHZwVS9oazJVanZjUld1cllscjVwMThJSm92YnV1a2VOTllpSU10amdhWW1BbVgwVkY3WT0iLCJtYWMiOiJjOTliNTYwYjE1MmI0NDFhYmRiMTIyZWJiMjYzYzVjYTVjNTdkNzMyNDk1NzViMmRjMWE4ZDUxZDhhNTA2ZjkxIiwidGFnIjoiIn0%3D"}
]

# 2. 基础配置
FGH_ACCOUNT_ENV = os.environ.get('FGH_ACCOUNT', '[]')
TG_BOT_ENV = os.environ.get('TG_BOT', '')
TARGET_SERVER_URL = "https://panel.freegamehost.xyz/server/41ed8b6e"

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
    except: pass

def inject_cookies(sb):
    print("🚀 正在注入身份 Cookie...")
    for c in MY_COOKIES:
        try:
            sb.driver.execute_cdp_cmd('Network.setCookie', {
                'name': c['name'], 'value': c['value'],
                'domain': 'panel.freegamehost.xyz', 'path': '/', 'secure': True
            })
        except Exception as e:
            print(f"⚠️ Cookie 注入失败: {c['name']} -> {e}")

def execute_renewal(sb, email):
    # 强制修正账号显示为 My renqi
    display_name = email if email and email != 'unknown' else 'My renqi'
    print(f"✈️ 正在空降目标服务器 (账号: {display_name})...")
    
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 15)
    sb.sleep(8)

    if "login" in sb.get_current_url().lower():
        print("❌ 身份失效，未能进入管理面板")
        return False

    # 1. 核弹级清场（保留这个成功经验）
    print("🧹 正在清理页面广告与遮挡物...")
    sb.execute_script("""
        document.querySelectorAll('iframe').forEach(f => {
            if(f.src && !f.src.includes('cloudflare')) f.remove(); 
        });
        document.querySelectorAll('div, a, span').forEach(el => { 
            let txt = (el.innerText || '').toUpperCase();
            if(txt.includes('DOWNLOAD EXTENSION') || txt.includes('2 EASY STEPS') || txt.includes('ADVERTISEMENT')) {
                el.remove(); 
            }
        });
    """)

    # 2. 锁定续期按钮
    print("🎯 锁定续期按钮...")
    button_clicked = sb.execute_script("""
        var els = document.querySelectorAll('button, a, div[role="button"]');
        for (var i = 0; i < els.length; i++) {
            var txt = els[i].innerText.toUpperCase();
            if ((txt.includes('HOURS') || txt.includes('RENEW')) && !txt.includes('DELETE')) {
                els[i].scrollIntoView({block: "center"});
                els[i].click();
                return true;
            }
        }
        return false;
    """)

    if button_clicked:
        print("✅ 按钮已点击，等待 CF 验证框展开...")
        sb.sleep(6)
        
        # 3. 终极穿甲弹：基于内部坐标的精准打击
        print("🛡️ 正在执行内部坐标精准打击...")
        try:
            cf_iframe = None
            # 放弃正则匹配，直接全屏扫描所有 iframe
            iframes = sb.driver.find_elements("tag name", "iframe")
            
            # 找出那个可见的、且有一定体积的正牌验证框（因为广告全被清了，剩下的必定是它）
            for f in iframes:
                if f.is_displayed() and f.size.get('width', 0) > 150:
                    cf_iframe = f
                    break
            
            if cf_iframe:
                print("🎯 成功锁定验证框实体！准备击发...")
                # 强制居中
                sb.execute_script("arguments[0].scrollIntoView({block: 'center'});", cf_iframe)
                sb.sleep(2)
                
                # 获取尺寸并计算往左侧偏移的量（复选框通常在左侧 35% 的位置）
                w = cf_iframe.size.get('width', 300)
                offset_x = -int(w * 0.35)
                
                # 唤醒内部坐标打击模块
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(sb.driver)
                actions.move_to_element(cf_iframe).move_by_offset(offset_x, 0).click().perform()
                
                print(f"💥 坐标穿甲弹已击发 (偏移量 {offset_x})，静候 10 秒等待绿勾...")
                sb.sleep(10)
            else:
                print("❌ 未能在页面中找到任何可见的验证框。")
        except Exception as e:
            print(f"❌ 坐标打击发生异常: {e}")
            
    else:
        print("⚠️ 未发现续期按钮，可能已在冷却中。")

    # 截图撤退
    final_img = f"{display_name}_status.png"
    print(f"📸 任务流程结束，正在截图保存为 {final_img}")
    sb.save_screenshot(final_img)
    send_tg_photo(f"✅ 账号执行完毕: {display_name}", final_img)
    
    return True

def main():
    try:
        accounts = json.loads(FGH_ACCOUNT_ENV)
    except:
        print("❌ 账户数据解析失败")
        return

    for acc in accounts:
        email = acc.get('email', 'unknown')
        print(f"\n--- 处理账号: {email} ---")
        with SB(uc=True, headless=False, agent=MY_USER_AGENT) as sb:
            # 强制最大化窗口，确保 PyAutoGUI 的绝对坐标计算不会因为窗口缩放而打偏
            sb.driver.maximize_window()
            sb.uc_open_with_tab("about:blank") 
            inject_cookies(sb)
            execute_renewal(sb, email)
            time.sleep(5)

if __name__ == "__main__":
    main()
