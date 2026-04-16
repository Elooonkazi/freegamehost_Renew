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
        "value": "BCLS1VRs2XdNcW121YxY5k6rjmskDZXawJDTsdF8k5c-1776328981-1.2.1.1-riFPNqFniObElrMpsivZquGGZDH0fDefCm._dCWBLJ63RYDn7rUhJVowj25pMn0iW_3bLeZHL1msJghRWlArpL11ELdhn_6E1epeia9V.ohjUSmSODMUrn2F5C6aiuwsBJTkrhOFKgQ3zporxVPC4Z5_orcQHYdOHe6w5u1EZj7Un8F1XmLKHVA68L7sQgbr0HrcRTzXHwO.WYJgy1M5hr_fQEiDMSByjvPZZINcipq6tMxN3KDkGUsgr9nUKnO8AooofvyZJfP8hBo5bQHze.Zl9hmNJxHFBG3OnV_K7UimdVR93_nYx71n.OsMPXyeqETBzhq4g.of1Uh9XiI2bA"
    },
    {
        "name": "pterodactyl_session", 
        "value": "eyJpdiI6ImJnZHZpaGxKU1VLRWczbXJReUZWM3c9PSIsInZhbHVlIjoidVA5c29vaVkxN0Z6VmlZK2JOa2U0eE9sR01OczJVSlAwM3BZZTVKUjNIVnZJYmFxVXVudFdpL01xaDRPVnBObC82dkNuZlNMcXNCTGVJbFRHb1BtQSthTWpqeWtjcm5adDF3MDRqRmdhaWlhaHBLU3EzdGVSeGpYS3RwZVVtQkkiLCJtYWMiOiJkNDU4Zjc4YmFkYWQ5OGRlM2EyNjNjMWUxY2I3NDRiYTNjYTBkYzZlYjdhZjZhYWJmNDI4MjE3MjBkOWFkMjY1IiwidGFnIjoiIn0%3D"
    },
    {
        "name": "XSRF-TOKEN", 
        "value": "eyJpdiI6InVJMVYrdkxWK2xkWlNreDJSVUJnREE9PSIsInZhbHVlIjoiaStRKzljRG1yLytxUXNEWjNUVnJVT00xYU1uTkxoazdUTjBjdDk5NDMzQzZZOWthdVFoZTByYnUzOEZMZmRhZ3BlY0dRQ0ZEalN5di9tSHE2UHk3Z1JMN0RabjhtSUZoSy9kY2dSNFRlU2JmSU56bU9CUno2VnN6TFY1d21nL2ciLCJtYWMiOiJjYTkxMWFlMTAzNzIzNzY0MjNhYjY4NzA5YjZjMGNiYmY0MDc4MDQ4NzA5NDA5NDg1NjQ0YmE5ZTljN2M3YzgyIiwidGFnIjoiIn0%3D" # 🚨 必须新增这个！
    },
    {
        "name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", 
        "value": "eyJpdiI6Imo1OGFBOXRhdGxFOWRLUVFZcldjbUE9PSIsInZhbHVlIjoiVEE3MFY3SUNHT2UvVktaWmkzMDVzampORUhQb3ZubzczU1RBVnpGbGlxSUZJSFVqZHRzRkZrdnlVdTlDL2pMRU9objJKTXppL0RLYVlSbkpSeE9NVUN0LzU2dWVYZTlkNnZPUldqKzVUN2VpQ1NVbzdwcXdXTzhoOTBZbk1GRUcwRkUveHowUzNWMWVSQzd4T1d2R0dGRFFZTmdVWTI4WWRETTF6K3AxT2REclErYlN1QllRSVZSOE1JOWo2alFzOWM4K0RrR1lKT1ZnQmFFQU1jcGJ2c1oxVWNmYTdiR2g0SjJTQy9VMC8rMD0iLCJtYWMiOiI5NmYwZTY3NzQxNGY0ZGZlOGJlMGFlNzcyNTU3MjNmNjQwZDc0MjM5MmJkY2RjNjA0OTNiNWQwZWViZWQ0M2U3IiwidGFnIjoiIn0%3D"
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
    🎯 北斗制导版：
    秒点续期 -> 锁定周围带有"Security Check"字眼的真实 CF 框 -> 坐标爆破 -> 截图撤退
    """
    print(f"✈️ 正在空降目标服务器: {TARGET_SERVER_URL}")
    sb.uc_open_with_reconnect(TARGET_SERVER_URL, 10)
    sb.sleep(5)

    # 🚀 进场直接核爆底部的虚假广告框，防止干扰
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

        # 🚀 精准制导锁定 CF 验证框
        print("🛡️ 正在执行：通过周围环境文本，顺藤摸瓜寻找真实 CF 验证框...")
        try:
            # 💡 核心修复：通过查找 "SECURITY CHECK" 等文字，精准提取它身边的 iframe！
            target_frame = sb.execute_script("""
                let frames = document.querySelectorAll('iframe');
                
                // 战术 1：顺藤摸瓜 (看它爸爸的文字里有没有验证提示)
                for (let f of frames) {
                    let parentText = (f.parentElement ? f.parentElement.innerText : '').toUpperCase();
                    if (parentText.includes('SECURITY CHECK') || parentText.includes('VERIFY YOU ARE HUMAN')) {
                        return f;
                    }
                }
                
                // 战术 2：看它自身的 title 属性
                for (let f of frames) {
                    let title = (f.title || '').toUpperCase();
                    if (title.includes('CLOUDFLARE') || title.includes('WIDGET CONTAINING')) {
                        return f;
                    }
                }
                
                return null;
            """)
            
            if target_frame:
                w = target_frame.size['width']
                h = target_frame.size['height']
                print(f"💥 成功锁定正牌 CF 验证框 (尺寸 {w}x{h})")
                
                # 强行把真实的验证框滚动到屏幕正中间！
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
                offset_x = -int(w * 0.35)
                actions.move_to_element(target_frame).move_by_offset(offset_x, 0).click().perform()
                
                print(f"🎯 鼠标已精准点击复选框 (偏移量 {offset_x})，静候 8 秒等待绿勾...")
                sb.sleep(8)
            else:
                print("❓ 扫描完毕，页面中部并未生成 CF 验证框。")
                
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
