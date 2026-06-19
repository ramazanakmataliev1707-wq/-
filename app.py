import re
import sqlite3
import os
import numpy as np
import csv
import json
import shutil
import threading
import time
from datetime import datetime, timedelta
import phonenumbers
from phonenumbers import NumberParseException
import asyncio
from cryptography.fernet import Fernet
from collections import deque
import urllib.request

try:
    import tensorflow.lite as tflite
    ML_AVAILABLE = True
except:
    ML_AVAILABLE = False

# ===== 0. ТИЛДЕР СИСТЕМАСЫ =====
LANGUAGES = {
    "ky": "Кыргызча", "ru": "Русский", "en": "English", "tr": "Türkçe", "kz": "Қазақша",
    "uz": "O'zbekcha", "zh": "中文", "ar": "العربية", "de": "Deutsch", "fr": "Français"
}

TRANSLATIONS = {
    "ky": {
        "app_title": "🛡️ Scam Shield PRO Brain",
        "select_lang": "Тил тандаңыз",
        "welcome": "Кош келиңиз! Тил тандаңыз",
        "continue": "Улантуу",
        "sms_label": "SMS текст бул жерге чаптаңыз",
        "number_label": "Номер: +996555123456",
        "paste": "📋 SMSти чаптоо",
        "check": "🔍 ТЕКШЕРҮ + BRAIN",
        "block": "📵 БЛОКТОО",
        "report": "🚩 Шектүү деп билдирүү",
        "settings": "⚙️ Орнотуулар",
        "history": "📜 Тарых",
        "sensitivity": "Сезгичтик",
        "auto_scan": "⏰ Авто сканер",
        "ml_ai": "🤖 ЖИ Мээ",
        "save": "Сактоо",
        "safe": "✅ Коопсуз",
        "caution": "🟡 Шектенүү",
        "warning": "⚠️ Кооптуу",
        "danger": "🚨 МОШЕННИК!",
        "tip": "💡 Банк код сурабайт!",
        "export_csv": "📊 CSV экспорт",
        "clear_history": "🗑️ Тазалоо",
        "dark_mode": "🌙 Караңгы режим",
        "backup_db": "💾 Backup",
        "restore_db": "🔄 Restore",
        "copy": "📋 Көчүрүү",
        "reasons": "Себептер:",
        "blocked_msg": "Номер блоктолду",
        "reported_msg": "Шектүү катары белгиленди",
        "home": "Башкы",
        "stats": "📊 Статистика",
        "whitelist": "⭐ Whitelist",
        "dynamic_db": "🧠 Dynamic DB",
        "last_update": "Акыркы жаңыртуу:",
        "total_scammers": "Базадагы мошейник:",
        "auto_update": "Авто жаңыртуу",
        "update_now": "Азыр жаңыртуу",
        "rate_limit": "Тез-тез текшерүүгө болбойт. {} сек күт",
        "add_whitelist": "⭐ Whitelist кошуу",
        "added_whitelist": "Whitelistке кошулду"
    },
    "ru": {
        "app_title": "🛡️ Scam Shield PRO Brain",
        "select_lang": "Выберите язык",
        "welcome": "Добро пожаловать! Выберите язык",
        "continue": "Продолжить",
        "sms_label": "Вставьте текст SMS",
        "number_label": "Номер: +79991234567",
        "paste": "📋 Вставить SMS",
        "check": "🔍 ПРОВЕРИТЬ + МОЗГ",
        "block": "📵 ЗАБЛОКИРОВАТЬ",
        "report": "🚩 Сообщить как спам",
        "settings": "⚙️ Настройки",
        "history": "📜 История",
        "sensitivity": "Чувствительность",
        "auto_scan": "⏰ Авто сканер",
        "ml_ai": "🤖 ИИ Мозг",
        "save": "Сохранить",
        "safe": "✅ Безопасно",
        "caution": "🟡 Подозрительно",
        "warning": "⚠️ Опасно",
        "danger": "🚨 МОШЕННИК!",
        "tip": "💡 Банк код не просит!",
        "export_csv": "📊 Экспорт CSV",
        "clear_history": "🗑️ Очистить",
        "dark_mode": "🌙 Темная тема",
        "backup_db": "💾 Бэкап",
        "restore_db": "🔄 Восстановить",
        "copy": "📋 Копировать",
        "reasons": "Причины:",
        "blocked_msg": "Номер заблокирован",
        "reported_msg": "Помечен как спам",
        "home": "Главная",
        "stats": "📊 Статистика",
        "whitelist": "⭐ Белый список",
        "dynamic_db": "🧠 Dynamic DB",
        "last_update": "Последнее обновление:",
        "total_scammers": "Мошенников в базе:",
        "auto_update": "Авто обновление",
        "update_now": "Обновить сейчас",
        "rate_limit": "Слишком часто. Подождите {} сек",
        "add_whitelist": "⭐ В белый список",
        "added_whitelist": "Добавлен в whitelist"
    },
    "en": {
        "app_title": "🛡️ Scam Shield PRO Brain",
        "select_lang": "Select Language",
        "welcome": "Welcome! Select language",
        "continue": "Continue",
        "sms_label": "Paste SMS text here",
        "number_label": "Number: +1234567890",
        "paste": "📋 Paste SMS",
        "check": "🔍 SCAN + BRAIN",
        "block": "📵 BLOCK",
        "report": "🚩 Report Scam",
        "settings": "⚙️ Settings",
        "history": "📜 History",
        "sensitivity": "Sensitivity",
        "auto_scan": "⏰ Auto Scanner",
        "ml_ai": "🤖 AI Brain",
        "save": "Save",
        "safe": "✅ Safe",
        "caution": "🟡 Suspicious",
        "warning": "⚠️ Dangerous",
        "danger": "🚨 SCAMMER!",
        "tip": "💡 Banks never ask code via SMS!",
        "export_csv": "📊 Export CSV",
        "clear_history": "🗑️ Clear History",
        "dark_mode": "🌙 Dark Mode",
        "backup_db": "💾 Backup",
        "restore_db": "🔄 Restore",
        "copy": "📋 Copy",
        "reasons": "Reasons:",
        "blocked_msg": "Number blocked",
        "reported_msg": "Marked as suspicious",
        "home": "Home",
        "stats": "📊 Stats",
        "whitelist": "⭐ Whitelist",
        "dynamic_db": "🧠 Dynamic DB",
        "last_update": "Last update:",
        "total_scammers": "Scammers in DB:",
        "auto_update": "Auto Update",
        "update_now": "Update Now",
        "rate_limit": "Too many checks. Wait {} sec",
        "add_whitelist": "⭐ Add to Whitelist",
        "added_whitelist": "Added to whitelist"
    }
}

def t(key, lang="en"):
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# ===== 1. 2 БАЗА СИСТЕМАСЫ =====
KEY_FILE = "key.key"
DB_NAME = "scam_shield_encrypted.db"
DYNAMIC_DB = "dynamic_scammers.db"
BACKUP_DIR = "backups"
ML_MODEL_FILE = "scam_model.tflite"

LINK_REGEX = re.compile(r'http|bit\.ly|tinyurl|t\.me|wa\.me|clck\.ru|short\.link', re.IGNORECASE)
URGENCY_REGEX = re.compile(r'5 минут|5 мүнөт|срочно|urgent|şimdi|now|立即|فوري', re.IGNORECASE)
BANK_REGEX = re.compile(r'банк|bank|карта|card|visa|mastercard|счет|account|эсеп', re.IGNORECASE)
VIRTUAL_REGEX = re.compile(r'\+7999|\+7800|\+496|\+4470|\+1234|\+1[0-9]{9}')

rate_limiter = deque(maxlen=10)

def get_or_create_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key.decode()

def init_main_db(key):
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scam_numbers
                 (number TEXT PRIMARY KEY, source TEXT, date_added TEXT, reports INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS checked_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, text_snippet TEXT, score INTEGER,
                  ml_score REAL, verdict TEXT, date_checked TEXT, auto_scanned INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS whitelist
                 (number TEXT PRIMARY KEY, name TEXT, date_added TEXT)''')

    c.execute("INSERT OR IGNORE INTO settings VALUES ('language', 'en')")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('sensitivity', 'high')")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('auto_scan_enabled', '1')")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('auto_update_enabled', '1')")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('theme_mode', 'system')")

    conn.commit()
    return conn

def init_dynamic_db():
    conn = sqlite3.connect(DYNAMIC_DB, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dynamic_scammers
                 (number TEXT PRIMARY KEY, source TEXT, first_seen TEXT, last_seen TEXT,
                  confidence REAL, report_count INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS update_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, update_time TEXT, new_numbers INTEGER, total_numbers INTEGER)''')
    conn.commit()
    return conn

def add_to_dynamic_db(conn, numbers_list, source):
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    added = 0

    for num, conf in numbers_list:
        clean_num = clean_number_format(num)
        if not clean_num:
            continue
        c.execute("SELECT confidence, report_count FROM dynamic_scammers WHERE number=?", (clean_num,))
        res = c.fetchone()
        if res:
            new_conf = min(res[0] + conf*0.1, 1.0)
            c.execute("UPDATE dynamic_scammers SET last_seen=?, confidence=?, report_count=? WHERE number=?",
                     (now, new_conf, res[1]+1, clean_num))
        else:
            c.execute("INSERT INTO dynamic_scammers VALUES (?,?,?,?,?,?)",
                     (clean_num, source, now, now, conf, 1))
            added += 1

    c.execute("INSERT INTO update_log VALUES (NULL,?,?,?)", (now, added, get_dynamic_count(conn)))
    conn.commit()
    return added

def get_dynamic_count(conn):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM dynamic_scammers")
    return c.fetchone()[0]

def cleanup_dynamic_db(conn):
    c = conn.cursor()
    cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute("DELETE FROM dynamic_scammers WHERE last_seen<? AND confidence<0.3", (cutoff,))
    c.execute("VACUUM")
    conn.commit()

def get_setting(conn, key, default='en'):
    try:
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key=?", (key,))
        res = c.fetchone()
        return res[0] if res else default
    except:
        return default

def set_setting(conn, key, value):
    try:
        c = conn.cursor()
        c.execute("UPDATE settings SET value=? WHERE key=?", (value, key))
        conn.commit()
    except:
        pass

def check_rate_limit():
    now = datetime.now()
    while rate_limiter and (now - rate_limiter[0]).total_seconds() > 60:
        rate_limiter.popleft()
    if len(rate_limiter) >= 10:
        wait_time = 60 - int((now - rate_limiter[0]).total_seconds())
        return False, max(0, wait_time)
    rate_limiter.append(now)
    return True, 0

def clean_number_format(number):
    if not number:
        return ""
    number = number.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not number.startswith("+"):
        number = "+" + number
    try:
        parsed = phonenumbers.parse(number, None)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException:
        pass
    return number

def is_whitelisted(conn, number):
    try:
        c = conn.cursor()
        c.execute("SELECT 1 FROM whitelist WHERE number=?", (clean_number_format(number),))
        return c.fetchone() is not None
    except:
        return False

def add_to_whitelist(conn, number, name="User"):
    try:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO whitelist VALUES (?,?,?)",
                  (clean_number_format(number), name, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        return True
    except:
        return False

# ===== 2. BRAIN - АР ТАРАПТАН ИЗДӨ =====
def fetch_from_open_sources():
    numbers = []
    try:
        url = "https://open.spamdb.org/api/v1/spam_numbers?limit=100"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            for item in data.get("numbers", []):
                numbers.append((item["number"], 0.8))
    except:
        pass

    numbers.extend([
        ("+79991111111", 0.9),
        ("+78002222222", 0.85),
        ("+996555999", 0.95)
    ])
    return numbers

def analyze_with_brain(number, text, main_conn, dynamic_conn, lang):
    total_score = 0
    reasons = []
    sources_found = []
    clean_num = clean_number_format(number)

    if is_whitelisted(main_conn, clean_num):
        return -100, ["⭐ Whitelisted"], "safe", 0

    c = main_conn.cursor()
    c.execute("SELECT reports FROM scam_numbers WHERE number=?", (clean_num,))
    res = c.fetchone()
    if res:
        score = 40 + min(res[0] * 5, 30)
        total_score += score
        sources_found.append("Local DB")
        reasons.append(f"Local DB: {res[0]} reports +{score}")

    dc = dynamic_conn.cursor()
    dc.execute("SELECT confidence, report_count, source FROM dynamic_scammers WHERE number=?", (clean_num,))
    res = dc.fetchone()
    if res:
        conf, count, src = res
        score = int(conf * 50) + min(count * 3, 20)
        total_score += score
        sources_found.append(f"Dynamic DB:{src}")
        reasons.append(f"Dynamic DB {src}: conf={conf:.2f} +{score}")

    if VIRTUAL_REGEX.search(clean_num):
        total_score += 30
        reasons.append("Virtual number +30")

    text_score, text_reasons = analyze_text(text)
    total_score += text_score
    reasons.extend(text_reasons)

    ml_score = 0
    if ML_AVAILABLE and ml_model.interpreter:
        ml_score = ml_model.predict(text + " + number)
        ml_points = int(ml_score * 50)
        total_score += ml_points
        if ml_score > 0.4:
            sources_found.append("ML Brain")
            reasons.append(f"ML Brain: {ml_score*100:.0f}% +{ml_points}")

    sensitivity = get_setting(main_conn, 'sensitivity', 'high')
    verdict, level = get_verdict(total_score, ml_score, sensitivity, lang)

    c.execute("INSERT INTO checked_history VALUES (NULL,?,?,?,?,?,?,0)",
             (clean_num, text[:100], total_score, ml_score, verdict, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    main_conn.commit()

    return total_score, reasons, level, ml_score

# ===== 3. ML MODEL =====
class ScamMLModel:
    def __init__(self):
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.vocab = {'code':1, 'urgent':2, 'account':3, 'password':4, 'link':5,
                      'bank':6, 'card':7, 'payment':8, 'won':9, 'prize':10,
                      'код':11, 'срочно':12, 'аккаунт':13, 'пароль':14}

    def load_model(self):
        if not ML_AVAILABLE:
            return False
        try:
            if os.path.exists(ML_MODEL_FILE):
                self.interpreter = tflite.Interpreter(model_path=ML_MODEL_FILE)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
                return True
        except:
            pass
        return False

    def text_to_sequence(self, text, max_len=100):
        words = re.findall(r'\w+', text.lower())
        sequence = [self.vocab.get(w, 0) for w in words[:max_len]]
        while len(sequence) < max_len:
            sequence.append(0)
        return np.array([sequence], dtype=np.float32)

    def predict(self, text):
        if not self.interpreter:
            return 0.0
        try:
            input_data = self.text_to_sequence(text)
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            return float(output_data[0][0])
        except:
            return 0.0

ml_model = ScamMLModel()

SCAM_WORDS = {
    "en": {"code":10, "urgent":15, "won":20, "blocked":15, "account":5, "password":15, "link":15},
    "ru": {"код":10, "срочно":15, "вы выиграли":20, "заблокирован":15, "аккаунт":5, "пароль":15},
    "ky": {"код":10, "срочно":15, "утуп алдыңыз":20, "бөгөттөлдү":15, "аккаунт":5, "пароль":15}
}

def analyze_text(text):
    score = 0
    reasons = []
    if not text:
        return score, reasons
    text_lower = text.lower()
    for lang_dict in SCAM_WORDS.values():
        for word, points in lang_dict.items():
            if word in text_lower:
                score += points
                reasons.append(f"'{word}' +{points}")
    if LINK_REGEX.search(text_lower):
        score += 30
        reasons.append("Suspicious link +30")
    if URGENCY_REGEX.search(text_lower):
        score += 20
        reasons.append("Urgency +20")
    if BANK_REGEX.search(text_lower):
        score += 15
        reasons.append("Bank mention +15")
    return score, reasons

def get_verdict(total_score, ml_score, sensitivity, lang):
    ml_bonus = ml_score * 50
    if sensitivity == 'low':
        high, warn, caution = 90, 70, 40
    elif sensitivity == 'medium':
        high, warn, caution = 85, 65, 35
    else:
        high, warn, caution = 80, 60, 30
    final_score = total_score + ml_bonus
    if final_score >= high or ml_score > 0.8:
        return f"{t('danger', lang)} {final_score}", "danger"
    elif final_score >= warn or ml_score > 0.6:
        return f"{t('warning', lang)} {final_score}", "warning"
    elif final_score >= caution or ml_score > 0.4:
        return f"{t('caution', lang)} {final_score}", "caution"
    else:
        return f"{t('safe', lang)} {final_score}", "safe"

# ===== 4. АВТО ЖАҢЫРТЫЧ THREAD =====
class AutoUpdater(threading.Thread):
    def __init__(self, dynamic_conn, interval=1800):
        super().__init__(daemon=True)
        self.dynamic_conn = dynamic_conn
        self.interval = interval
        self.running = True

    def run(self):
        while self.running:
            try:
                numbers = fetch_from_open_sources()
                added = add_to_dynamic_db(self.dynamic_conn, numbers, "OpenSource")
                cleanup_dynamic_db(self.dynamic_conn)
                print(f"[AutoUpdater] Added {added} new scammers. Total: {get_dynamic_count(self.dynamic_conn)}")
            except Exception as e:
                print(f"[AutoUpdater] Error: {e}")
            time.sleep(self.interval)

    def stop(self):
        self.running = False

# ===== 5. FLET UI =====
def main(page: ft.Page):
    key = get_or_create_key()
    main_conn = init_main_db(key)
    dynamic_conn = init_dynamic_db()
    ml_model.load_model()

    lang = get_setting(main_conn, 'language', 'en')
    sensitivity = get_setting(main_conn, 'sensitivity', 'high')

    updater = AutoUpdater(dynamic_conn)
    updater.start()

    page.title = t("app_title", lang)
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.window_width = 400
    page.window_height = 700

    sms_input = ft.TextField(label=t("sms_label", lang), multiline=True, min_lines=4, max_lines=6)
    number_input = ft.TextField(label=t("number_label", lang))
    result_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
    reasons_list = ft.Column([])
    status_text = ft.Text("", size=12)

    def update_db_status():
        count = get_dynamic_count(dynamic_conn)
        c = dynamic_conn.cursor()
        c.execute("SELECT update_time FROM update_log ORDER BY id DESC LIMIT 1")
        res = c.fetchone()
        last = res[0] if res else "Never"
        status_text.value = f"{t('dynamic_db', lang)}\n{t('total_scammers', lang)} {count}\n{t('last_update', lang)} {last}"
        page.update()

    def check_click(e):
        ok, wait = check_rate_limit()
        if not ok:
            page.snack_bar = ft.SnackBar(ft.Text(t("rate_limit", lang).format(wait)), bgcolor=ft.colors.ORANGE)
            page.snack_bar.open = True
            page.update()
            return

        score, reasons, level, ml = analyze_with_brain(number_input.value, sms_input.value, main_conn, dynamic_conn, lang)
        result_text.value = get_verdict(score, ml, sensitivity, lang)[0]
        colors = {"safe": ft.colors.GREEN, "caution": ft.colors.AMBER, "warning": ft.colors.ORANGE, "danger": ft.colors.RED}
        result_text.color = colors.get(level, ft.colors.WHITE)

        reasons_list.controls = [ft.Text(f"• {r}", size=12) for r in reasons]
        update_db_status()
        page.update()

    def block_click(e):
        c = main_conn.cursor()
        c.execute("INSERT OR IGNORE INTO scam_numbers VALUES (?,?,?,?)",
                 (clean_number_format(number_input.value), "User Blocked", datetime.now().strftime("%Y-%m-%d"), 1))
        main_conn.commit()
        page.snack_bar = ft.SnackBar(ft.Text(t("blocked_msg", lang)), bgcolor=ft.colors.RED)
        page.snack_bar.open = True
        page.update()

    def report_click(e):
        c = main_conn.cursor()
        c.execute("UPDATE scam_numbers SET reports = reports + 1 WHERE number=?", (clean_number_format(number_input.value),))
        if c.rowcount == 0:
            c.execute("INSERT INTO scam_numbers VALUES (?,?,?,?)",
                     (clean_number_format(number_input.value), "User Reported", datetime.now().strftime("%Y-%m-%d"), 1))
        main_conn.commit()
        add_to_dynamic_db(dynamic_conn, [(number_input.value, 0.9)], "User Report")
        page.snack_bar = ft.SnackBar(ft.Text(t("reported_msg", lang)), bgcolor=ft.colors.ORANGE)
        page.snack_bar.open = True
        update_db_status()
        page.update()

    def whitelist_click(e):
        if add_to_whitelist(main_conn, number_input.value):
            page.snack_bar = ft.SnackBar(ft.Text(t("added_whitelist", lang)), bgcolor=ft.colors.GREEN)
            page.snack_bar.open = True
            page.update()

    def update_db_click(e):
        numbers = fetch_from_open_sources()
        added = add_to_dynamic_db(dynamic_conn, numbers, "Manual")
        cleanup_dynamic_db(dynamic_conn)
        page.snack_bar = ft.SnackBar(ft.Text(f"Added {added} new scammers"), bgcolor=ft.colors.BLUE)
        page.snack_bar.open = True
        update_db_status()
        page.update()

    def sens_change(e):
        levels = ['low', 'medium', 'high']
        set_setting(main_conn, 'sensitivity', levels[int(e.control.value)])

    home_tab = ft.Column([
        ft.Text(t("app_title", lang), size=20, weight=ft.FontWeight.BOLD),
        number_input,
        sms_input,
        ft.ElevatedButton(t("paste", lang), on_click=lambda e: page.set_clipboard()),
        ft.ElevatedButton(t("check", lang), on_click=check_click, bgcolor=ft.colors.BLUE),
        ft.Row([
            ft.ElevatedButton(t("block", lang), on_click=block_click, bgcolor=ft.colors.RED),
            ft.ElevatedButton(t("report", lang), on_click=report_click, bgcolor=ft.colors.ORANGE),
            ft.ElevatedButton(t("add_whitelist", lang), on_click=whitelist_click, bgcolor=ft.colors.GREEN)
        ]),
        ft.Divider(),
        result_text,
        ft.Text(t("reasons", lang), weight=ft.FontWeight.BOLD),
        reasons_list,
        ft.Text(t("tip", lang), size=11, color=ft.colors.GREY)
    ], scroll=ft.ScrollMode.AUTO)

    stats_tab = ft.Column([
        ft.Text(t("stats", lang), size=18, weight=ft.FontWeight.BOLD),
        status_text,
        ft.ElevatedButton(t("update_now", lang), on_click=update_db_click),
        ft.Switch(label=t("auto_update", lang), value=True),
        ft.Text("ML Brain: " + ("Active" if ml_model.interpreter else "Offline"))
    ])

    settings_tab = ft.Column([
        ft.Text(t("settings", lang), size=18, weight=ft.FontWeight.BOLD),
        ft.Text(t("sensitivity", lang)),
        ft.Slider(min=0, max=2, divisions=2, value=2 if sensitivity=='high' else 1 if sensitivity=='medium' else 0, on_change=sens_change),
        ft.ElevatedButton(t("export_csv", lang), on_click=lambda e: export_csv(main_conn, page, lang)),
        ft.ElevatedButton(t("clear_history", lang), on_click=lambda e: clear_history(main_conn, page, lang)),
        ft.ElevatedButton(t("backup_db", lang), on_click=lambda e: backup_database(main_conn, page, lang)),
        ft.ElevatedButton(t("restore_db", lang), on_click=lambda e: restore_database(page, lang))
    ])

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text=t("home", lang), content=home_tab),
            ft.Tab(text=t("stats", lang), content=stats_tab),
            ft.Tab(text=t("settings", lang), content=settings_tab),
        ],
        expand=1
    )

    page.add(tabs)
    update_db_status()

    def on_close(e):
        updater.stop()
        main_conn.close()
        dynamic_conn.close()

    page.on_window_event = on_close

def export_csv(conn, page, lang):
    try:
        filename = f"scam_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        c = conn.cursor()
        c.execute("SELECT number, text_snippet, score, verdict, date_checked FROM checked_history ORDER BY date_checked DESC")
        rows = c.fetchall()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Number', 'Text', 'Score', 'Verdict', 'Date'])
            writer.writerows(rows)
        page.snack_bar = ft.SnackBar(ft.Text(f"CSV: {filename}"), bgcolor=ft.colors.GREEN)
        page.snack_bar.open = True
        page.update()
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(e)}"), bgcolor=ft.colors.RED)
        page.snack_bar.open = True
        page.update()

def clear_history(conn, page, lang):
    c = conn.cursor()
    c.execute("DELETE FROM checked_history")
    conn.commit()
    page.snack_bar = ft.SnackBar(ft.Text("History cleared"), bgcolor=ft.colors.BLUE)
    page.snack_bar.open = True
    page.update()

def backup_database(conn, page, lang):
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(DB_NAME, os.path.join(BACKUP_DIR, backup_name))
        page.snack_bar = ft.SnackBar(ft.Text(f"Backup: {backup_name}"), bgcolor=ft.colors.GREEN)
        page.snack_bar.open = True
        page.update()
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(e)}"), bgcolor=ft.colors.RED)
        page.snack_bar.open = True
        page.update()

def restore_database(page, lang):
    try:
        if os.path.exists(BACKUP_DIR):
            backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
            if backups:
                latest = sorted(backups)[-1]
                shutil.copy2(os.path.join(BACKUP_DIR, latest), DB_NAME)
                page.snack_bar = ft.SnackBar(ft.Text("Restored"), bgcolor=ft.colors.GREEN)
                page.snack_bar.open = True
                page.update()
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(e)}"), bgcolor=ft.colors.RED)
        page.snack_bar.open = True
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
