import os
import json
import time
import requests
from seleniumbase import SB

# ================= 🚨 本地克隆配置区 🚨 =================

# 1. 必须填入你提取 Cookie 时的真实浏览器指纹！(千万别用假版本号)
MY_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36" # 请替换为你的真实 UA

# 2. 你本地的真实 Cookie 组合 (新增了必不可少的 XSRF-TOKEN)
MY_COOKIES = [
    {
        "name": "cf_clearance", 
        "value": "TdelI2Xb5bYWDes4luF8ajPwgqaeqBAtUfjnlayhWu4-1776387100-1.2.1.1-IhdIFAqBhimcYPFbG570a65t1f77aq8MN1OPtzWLkos9JAL8vzYlDIpLMu9bW6OEwOOz6S5WEw4GL5bq2358GEHANBynJIZ.QeAw0ZooKuIl9kcasJnzxd_bwvKkWjd948LERW90aFZu3fmNie9AiN67tn6LX4UPDiuOrknM1CbPaJOvlMReCeazYpbVQTkvrXdAnhC8VKJk5hsZ5UzNtrL6_p.M6NGIHcFHRJGdVmKjp51ht6okWHhzPslQC4pKvH3Q.vz8o7c.Y1z9TvON1xJN47QVeLMwTqNp7xYLav0UebnjWqqnE7cQ7NDL2h6vD15Hyf7GtsawWjBo_vkvDw"
    },
    {
        "name": "pterodactyl_session", 
        "value": "eyJpdiI6InZjR3k5YXc0VllNcmhDOWROUk44R0E9PSIsInZhbHVlIjoiaE1ab1Z3V2NaZlFMN2JzMlhkUjRMRjBIMnozNmVOR3piMUorYW9JU2dVUDZvY1NtZExqT01qOGJUZ2Uzc0d4Q3RHRGY5YVJ6aVRsYkNrS0VuajVuUFhteHcwVDZPUjV4UDk4MHp5WUJCdUFrbThnbWY1SlFNQkZTcDZVa3d3clAiLCJtYWMiOiIzNDgyNjJhOTJlNmFmMjgzMjEzNTFiNDA2ZTFjMWNhNThmY2UxMzcwN2FkOTg2ODFjZjc5MmQ2MDc4MmJkNzgwIiwidGFnIjoiIn0%3D"
    },
    {
        "name": "XSRF-TOKEN", 
        "value": "eyJpdiI6IjdFWUpIdW01dU9YdUJjd2JuLzhCMnc9PSIsInZhbHVlIjoiMUNUWG1zeFNQTzJmT0xnd1ZPSkVmbXJJL2dVMEpnMmxzMzgvZ3BxNEh5RVZpK3JTamdRL3NZVXZjOGxCRk8vNU5uNWJjOG8xeUxNekRNZnAzRXVrbGYwYnBtZzN0c1FSTStIUkVrUHByMTRFUVBDNGxmTDdNVTNRVWtzbkkrelEiLCJtYWMiOiJjNmVkZjY1NjA4ZjA2NjExNzlkMDc5YmNmMWMwOGU1ZGFlODVmYmE5NTBjMDBjNDBjYTg4ZDU2ODk4YWFkMzYxIiwidGFnIjoiIn0%3D" # 🚨 必须新增这个！
    },
    {
        "name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", 
        "value": "eyJpdiI6IlFsaVROSllyc0d4UGtXZlN3b1BWNVE9PSIsInZhbHVlIjoiMlNuNHd5UVJGdFdYYjFaMnZxYWZZcklOVi81ai9nNTNmQTlPdFlUTSsrODRlQkFGVzlRMGg3aE9mcTU3T0djNWhnWjhOOHdQVDVTOXB0LzFhK0E5S3RLTDNIbzN2WTlFU1VnZmJSMWQzSGU3dHhyNVJmczBWQUtxQnQ5bjU1Y3dBRlF5R3Q1eWpiUGVmK0dWZytPeUR1d2VtZk9aTFNmVGQwZVRjNFhiTVB5T29MOWpOR2h4dzRncHZwVS9oazJVanZjUld1cllscjVwMThJSm92YnV1a2VOTllpSU10amdhWW1BbVgwVkY3WT0iLCJtYWMiOiJjOTliNTYwYjE1MmI0NDFhYmRiMTIyZWJiMjYzYzVjYTVjNTdkNzMyNDk1NzViMmRjMWE4ZDUxZDhhNTA2ZjkxIiwidGFnIjoiIn0%3D"
    }
]

# ================= 基础配置 =================

FGH_ACCOUNT_ENV = os.environ.get('FGH_ACCOUNT', '[]')
TG_BOT_ENV = os.environ.get('TG_BOT', '')
TARGET_SERVER_URL = "https://panel.freegamehost.xyz/server/41ed8b6e"

try:
    ACCOUNTS = json.loads(FGH_ACCOUNT_ENV)
except Exception as e:
    print(f"❌ 环境变量解析失败: {e}")
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
    except:
        pass

def inject_vip_cookies_via_cdp(sb):
    print("正在通过 CDP 强注克隆 Cookie...")
    for c in MY_COOKIES:
        if c.get("value") and "这里填" not in c.get("value"):
            try:
                sb.driver.execute_cdp_cmd('Network.setCookie', {
                    'name': c['name'], 'value': c['value'],
                    'domain': 'panel.freegamehost.xyz', 'path': '/', 'secure': True
                })
            except:
                pass

def execute_renewal(sb, email):
    """
    🎯 终极纯 Python 物理探雷版：
    弃用 JS DOM 传值，纯粹依靠 Python 原生 API 进行体积和坐标的高低位筛选。
    """
    print(f"✈️ 正在空降目标服务器: {TARGET_SERVER_URL}")
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
    sb.sleep(5)

    # 🚨 岗哨检查 1
    if "login" in sb.get_current_url().lower():
        print("❌ 灾难性拦截：您的身份已失效，被服务器强制踢回了登录页！")
        return False

    # 🚀 进场第一波清障：用 JS 隐藏掉所有的广告外壳，让它们的尺寸变成 0x0
    sb.execute_script("""
        document.querySelectorAll('div').forEach(el => {
            let txt = (el.innerText || '').toUpperCase();
            if (txt.includes('2 EASY STEPS') || txt.includes('DOWNLOAD EXTENSION') || txt.includes('TRUSTED SPOT')) {
                try { el.style.display = 'none'; } catch(e){}
            }
        });
        document.querySelectorAll('button, a, span, div[role="button"]').forEach(el => {
            let txt = (el.innerText || '').trim().toUpperCase();
            if (txt === 'CLOSE' || txt === 'X' || txt.includes('DISMISS')) {
                try { el.click(); } catch(e){}
            }
        });
    """)

    # 🚀 第一时间寻找并点击续期按钮
    print("🎯 第一时间锁定并点击续期按钮...")
    button_clicked = sb.execute_script("""
        var els = document.querySelectorAll('button, a, div[role="button"]');
        for (var i = 0; i < els.length; i++) {
            var txt = (els[i].innerText || "").toUpperCase().trim();
            if ((txt.includes('HOURS') || txt.includes('RENEW')) && !txt.includes('DELETE') && txt.length < 30) {
                els[i].scrollIntoView({block: "center"});
                els[i].click();
                return true;
            }
        }
        return false;
    """)

    if button_clicked:
        print("✅ 续期按钮已点击！等待 CF 验证框展开 (6秒)...")
        sb.sleep(6)
        
        # 🚨 岗哨检查 2
        if "login" in sb.get_current_url().lower():
            print("❌ 续期请求被拒：被踢回登录页！")
            return False

        # 🚀 纯 Python 物理探雷
        print("🛡️ 正在执行：全 Python 原生探雷器，按体型和高低位锁定目标...")
        try:
            iframes = sb.driver.find_elements("tag name", "iframe")
            target_frame = None
            min_y = float('inf')
            target_w = 0
            target_h = 0
            
            for idx, f in enumerate(iframes):
                # 拿取真实的物理数据
                w = f.size.get('width', 0)
                h = f.size.get('height', 0)
                y = f.location.get('y', 0)
                print(f"👀 探雷器测算: iframe[{idx}] Y坐标={y}, 尺寸={w}x{h}")
                
                # 铁律 1：拥有实体（剔除 0x0 幽灵探针和被我们隐藏的广告）
                if w >= 150 and h >= 40:
                    # 铁律 2：寻找位置最高的那一个（Y坐标最小，彻底避开底部漏网广告）
                    if y < min_y:
                        min_y = y
                        target_frame = f
                        target_w = w
                        target_h = h
            
            if target_frame:
                print(f"💥 探雷器成功锁定位置最高的正牌 CF (Y坐标: {min_y}，尺寸 {target_w}x{target_h})")
                
                # 强行把验证框居中
                sb.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_frame)
                sb.sleep(1)
                
                # 强制解除元素的禁止点击限制
                sb.execute_script("""
                    arguments[0].style.display = 'block';
                    arguments[0].style.visibility = 'visible';
                    arguments[0].style.opacity = '1';
                    arguments[0].style.pointerEvents = 'auto';
                """, target_frame)
                sb.sleep(1)
                
                # 启动内部坐标系精确点击
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(sb.driver)
                
                # 往左偏移宽度的 35%
                offset_x = -int(target_w * 0.35)
                actions.move_to_element(target_frame).move_by_offset(offset_x, 0).click().perform()
                
                print(f"🎯 穿甲弹已击发 (偏移量 {offset_x})，静候 8 秒等待绿勾...")
                sb.sleep(8)
            else:
                print("❓ 探雷器扫遍全网，未发现拥有实体的 CF 验证框。")
                
        except Exception as e:
            print(f"❌ CF 坐标打击发生异常: {e}")
    else:
        print("⚠️ 未发现续期按钮，可能已处于冷却中。")

    # 🚀 截图撤退
    print("📸 任务流程结束，正在截图并退出...")
    final_img = f"{email}_process.png"
    sb.save_screenshot(final_img)
    send_tg_photo(f"✅ 账号执行完毕，查看最终结果。账号: {email}", final_img)
    
    return True
# ================= 主流程 =================
def process_account(account):
    email = account.get('email', '')
    print(f"==========================================")
    print(f"👤 开始处理账号: {email}")
    print("==========================================")

    print("▶️ 策略 A: 尝试 CDP 注入 Cookie 免密登录...")
    with SB(uc=True, headless=False, agent=MY_USER_AGENT) as sb:
        sb.driver.set_window_size(1920, 1080)
        sb.uc_open_with_tab("about:blank") 
        inject_vip_cookies_via_cdp(sb)
        sb.uc_open_with_reconnect("https://panel.freegamehost.xyz/", 10)
        sb.sleep(6)

        if sb.is_element_visible('a[href="/account"]') or sb.is_element_visible('.fa-sign-out-alt'):
            print("✅ 策略 A 成功！克隆身份初步通过验证！")
            return execute_renewal(sb, email)
        else:
            print("❌ 策略 A 失败，面板未能识别您的 Cookie。")
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
