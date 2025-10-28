# -*- coding: utf-8 -*-
import json
import re
import urllib3
import time

# === ОТКЛЮЧАЕМ ПРЕДУПРЕЖДЕНИЯ ===
urllib3.disable_warnings()

# === HTTP ПОТОК ===
http = urllib3.PoolManager(
    timeout=urllib3.Timeout(connect=10.0, read=15.0),
    maxsize=10,
    retries=urllib3.util.Retry(total=3, backoff_factor=1),
    cert_reqs='CERT_REQUIRED'
)

# === TELEGRAM ===
TOKEN = "8219329709:AAGLptnFMl4cJGMM-YwQuhzy8VBTpmfHcWU"
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

# === HUGGING FACE (ТОЛЬКО НЕЙРОНКА) ===
HF_API_KEY = "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"  # ← ВСТАВЬ СВОЙ КЛЮЧ!
HF_API_URL = "https://api-inference.huggingface.co/models/ai-forever/rugpt3small_based_on_gpt2"

# Режимы пользователей
user_modes = {}

# === УНИВЕРСАЛЬНАЯ ОТПРАВКА ===
def http_post(url, payload):
    try:
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'SlangBot/1.0'
        }
        resp = http.request('POST', url, body=data, headers=headers)
        if resp.status == 200:
            return json.loads(resp.data.decode('utf-8'))
        else:
            print(f"HTTP {resp.status}: {resp.data.decode('utf-8')[:200]}")
            return None
    except Exception as e:
        print(f"HTTP ошибка: {e}")
        return None

# === TELEGRAM: ОТПРАВКА ===
def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return http_post(API_URL + "sendMessage", payload)

# === TELEGRAM: CALLBACK ===
def answer_callback_query(callback_query_id):
    payload = {"callback_query_id": callback_query_id}
    http_post(API_URL + "answerCallbackQuery", payload)

# === ПЕРЕВОД — ТОЛЬКО НЕЙРОНКА ===
def get_ai_translation(text, mode):
    direction = "из молодежного сленга в обычный русский" if mode == "slang_to_normal" else "из обычного русского в молодежный сленг"
    prompt = f"Переведи фразу '{text}' {direction}. Ответь ТОЛЬКО переведённым текстом, без кавычек и лишних слов."

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 100,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json; charset=utf-8"
    }

    try:
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        resp = http.request('POST', HF_API_URL, body=data, headers=headers)

        if resp.status == 200:
            result = json.loads(resp.data.decode('utf-8'))
            if isinstance(result, list) and len(result) > 0:
                translation = result[0].get("generated_text", text).strip().strip('"')
                print(f"AI перевёл: '{text}' → '{translation}'")
                return translation
        elif resp.status == 503:
            print("Модель загружается... жду 30 сек")
            time.sleep(30)
            return get_ai_translation(text, mode)
        else:
            print(f"HF {resp.status}: {resp.data.decode('utf-8')[:150]}")
    except Exception as e:
        print(f"AI ошибка: {e}")

    return text  # если AI упал — возвращаем оригинал

# === GET UPDATES ===
def get_updates(offset=None):
    url = API_URL + "getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        resp = http.request('GET', url, fields=params)
        if resp.status == 200:
            return json.loads(resp.data.decode('utf-8'))
    except:
        pass
    return {"ok": False}

# === ГЛАВНЫЙ ЦИКЛ ===
def main():
    offset = None
    print("Бот запущен — ТОЛЬКО НЕЙРОНКА, БЕЗ СЛОВАРЯ!")

    while True:
        try:
            updates = get_updates(offset)
            if not updates.get("ok"):
                time.sleep(5)
                continue

            for update in updates.get("result", []):
                offset = update["update_id"] + 1

                # === CALLBACK ===
                if "callback_query" in update:
                    q = update["callback_query"]
                    user_id = q["from"]["id"]
                    chat_id = q["message"]["chat"]["id"]
                    data = q["data"]

                    answer_callback_query(q["id"])
                    user_modes[user_id] = data
                    mode_text = "сленг → обычный" if data == "slang_to_normal" else "обычный → сленг"
                    send_message(chat_id, f"Режим: {mode_text}\nОтправь фразу!")
                    continue

                # === СООБЩЕНИЕ ===
                if "message" not in update:
                    continue

                msg = update["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "").strip()

                if not text:
                    continue

                if text == "/start":
                    kb = {
                        "inline_keyboard": [
                            [{"text": "Сленг → Обычный", "callback_data": "slang_to_normal"}],
                            [{"text": "Обычный → Сленг", "callback_data": "normal_to_slang"}]
                        ]
                    }
                    send_message(chat_id, "Привет! Я ИИ-переводчик сленга\nТолько нейронка, без словарей\nВыбери режим:", kb)
                    continue

                user_id = msg["from"]["id"]
                if user_id not in user_modes:
                    send_message(chat_id, "Сначала выбери режим через /start")
                    continue

                # Переводим ВСЮ ФРАЗУ целиком (а не по словам)
                clean_text = re.sub(r'[^\w\s]', '', text.lower())
                translation = get_ai_translation(clean_text, user_modes[user_id])

                if translation.lower() == clean_text:
                    send_message(chat_id, "Не смог перевести. Попробуй по-другому.")
                else:
                    send_message(chat_id, f"Перевод:\n{translation}")

        except Exception as e:
            print(f"Критическая ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()