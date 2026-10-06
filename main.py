import requests
import json
import os
from datetime import datetime

# تنظیمات
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SEEN_FILE = "seen_tokens.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def search_divar():
    url = "https://api.divar.ir/v8/postlist/w/search"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {
        "city_ids": [],
        "source_view": "SEARCH",
        "search_data": {
            "form_data": {
                "data": {
                    "category": {"str": {"value": "pets-animals"}},
                    "query": {"str": {"value": "عروس هلندی"}}
                }
            },
            "server_payload": {
                "@type": "type.googleapis.com/widgets.SearchData.ServerPayload",
                "legacy": {
                    "query": "عروس هلندی",
                    "category": "pets-animals"
                }
            }
        }
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        data = r.json()
        return data
    except:
        return None

def main():
    seen = load_seen()
    data = search_divar()
    if not data:
        return

    widgets = data.get("list_widgets", [])
    new_count = 0

    for widget in widgets:
        if widget.get("widget_type") != "POST_ROW":
            continue

        post = widget.get("data", {})
        token = post.get("token")
        if not token or token in seen:
            continue

        title = post.get("title", "بدون عنوان")
        price = post.get("middle_description_text", "قیمت نامشخص")
        city = post.get("action", {}).get("payload", {}).get("web_info", {}).get("city_persian", "")
        link = f"https://divar.ir/v/{token}"

        message = f"""🦜 <b>آگهی جدید عروس هلندی</b>

📌 <b>{title}</b>
💰 {price}
📍 {city}

🔗 <a href="{link}">مشاهده آگهی</a>
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        send_telegram(message)
        seen.add(token)
        new_count += 1

    save_seen(seen)
    print(f"Found {new_count} new ads")

if __name__ == "__main__":
    main()
