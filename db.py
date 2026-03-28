import json
import os

DB_FILE = "Buttons.json"

# تحميل البيانات
def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# حفظ البيانات
def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# حفظ زر
def save_button(button_id, type_, content, caption=None):
    data = load_data()
    old_clicks = data.get(button_id, {}).get("clicks", 0)
    data[button_id] = {
        "type": type_,
        "file_id": content if type_ != "text" else None,
        "text": content if type_ == "text" else None,
        "caption": caption,
        "clicks": old_clicks
    }
    save_data(data)

# جلب زر
def get_button(button_id):
    data = load_data()
    return data.get(button_id)

# إضافة ضغطة
def add_click(button_id):
    data = load_data()
    if button_id in data:
        data[button_id]["clicks"] = data[button_id].get("clicks", 0) + 1
        save_data(data)

# إحصائيات
def get_stats():
    data = load_data()
    total_buttons = len(data)
    total_clicks = sum(btn.get("clicks", 0) for btn in data.values())
    return total_buttons, total_clicks

# حذف زر
def delete_button(button_id):
    data = load_data()
    if button_id in data:
        del data[button_id]
        save_data(data)