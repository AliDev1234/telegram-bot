import requests

TOKEN = "ضع توكن البوت هنا"

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
resp = requests.get(url).json()

if resp.get("result"):
    last_update_id = max(update["update_id"] for update in resp["result"])
    # مسح كل التحديثات المعلقة
    requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}")
    print("✅ تم مسح التحديثات المعلقة")
else:
    print("لا توجد تحديثات معلقة")