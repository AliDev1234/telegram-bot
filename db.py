import json
import os
import shutil

DB_FILE = "database.json"
BACKUP_FILE = "database_backup.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    try:
        # نسخ احتياطي قبل الحفظ النهائي
        if os.path.exists(DB_FILE):
            shutil.copy(DB_FILE, BACKUP_FILE)

        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        # إذا فشل الحفظ الرئيسي، نحاول استرجاع النسخة الاحتياطية
        if os.path.exists(BACKUP_FILE):
            shutil.copy(BACKUP_FILE, DB_FILE)
        raise e

def save_button(button_id, type_, content, caption):
    data = load_data()

    old_data = data.get(button_id, {})
    data[button_id] = {
        "type": type_,
        "file_id": content if type_ != "text" else None,
        "text": content if type_ == "text" else None,
        "caption": caption if caption is not None else old_data.get("caption"),
        "clicks": old_data.get("clicks", 0)
    }

    save_data(data)

def get_button(button_id):
    data = load_data()
    return data.get(button_id)

def add_click(button_id):
    data = load_data()
    if button_id in data:
        data[button_id]["clicks"] = data[button_id].get("clicks", 0) + 1
    save_data(data)

def get_stats():
    data = load_data()
    total_buttons = len(data)
    total_clicks = sum(btn.get("clicks", 0) for btn in data.values())
    return total_buttons, total_clicks

def delete_button(button_id):
    data = load_data()
    if button_id in data:
        del data[button_id]
        save_data(data)