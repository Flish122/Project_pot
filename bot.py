# -*- coding: utf-8 -*-
import json
import re
import urllib3
import time
from datetime import datetime
import random

# === ОТКЛЮЧАЕМ ПРЕДУПРЕЖДЕНИЯ ===
urllib3.disable_warnings()

# === HTTP ===
http = urllib3.PoolManager(
    timeout=urllib3.Timeout(connect=10.0, read=15.0),
    maxsize=10,
    retries=urllib3.util.Retry(total=3, backoff_factor=1)
)

# === TELEGRAM ===
TOKEN = "8219329709:AAGLptnFMl4cJGMM-YwQuhzy8VBTpmfHcWU"
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

# === ЗАГРУЖАЕМ СЛОВАРЬ ===
try:
    with open("dictionary.json", "r", encoding="utf-8") as f:
        DICTIONARY = json.load(f)
    print(f"🎯 Словарь загружен: {len(DICTIONARY)} слов")
except FileNotFoundError:
    print("❌ ОШИБКА: dictionary.json не найден!")
    DICTIONARY = {}
except Exception as e:
    print(f"❌ Ошибка чтения словаря: {e}")
    DICTIONARY = {}

# === ХРАНИЛИЩЕ ===
user_modes = {}
user_stats = {}
user_sessions = {}

# === ЭМОДЗИ И СТИЛЬ ===
EMOJI = {
    "translate": "🔄", "slang": "🔥", "normal": "💬", "stats": "📊",
    "help": "❓", "back": "⬅️", "search": "🔍", "time": "⏱️",
    "words": "📚", "info": "ℹ️", "fire": "✨", "rocket": "🚀",
    "brain": "🧠", "mag": "🔎", "chart": "📈", "crown": "👑",
    "zap": "⚡", "star": "⭐", "tada": "🎯", "book": "📖",
    "bulb": "💡", "wave": "👋", "medal": "🏆", "flash": "💫"
}

# === УЛУЧШЕННАЯ ФУНКЦИЯ ПЕРЕВОДА СО СКЛОНЕНИЕМ ===
# === УЛУЧШЕННАЯ ФУНКЦИЯ ПЕРЕВОДА СО СКЛОНЕНИЕМ ===
def advanced_translate(text, mode):
    """
    Умный перевод с учетом склонений и форм слов
    """
    original_text = text
    words_found = []
    
    def replace_whole_words(text, search_word, replace_word):
        """
        Заменяет только целые слова, а не части слов
        """
        # Используем регулярное выражение для поиска целых слов
        pattern = r'\b' + re.escape(search_word) + r'\b'
        return re.sub(pattern, f"<b>{replace_word}</b>", text, flags=re.IGNORECASE)
    
    if mode == "slang_to_normal":
        # Сленг → Нормальный с учетом всех форм
        for slang, normal in DICTIONARY.items():
            # Базовые формы для поиска (склонения и спряжения)
            forms_to_check = [
                slang,  # исходная форма
                # падежи для существительных
                slang + 'а', slang + 'у', slang + 'ом', slang + 'е', 
                slang + 'ы', slang + 'ов', slang + 'ам', slang + 'ами',
                # формы глаголов
                slang + 'ю', slang + 'ешь', slang + 'ет', slang + 'ем', slang + 'ете', slang + 'ют',
                slang + 'л', slang + 'ла', slang + 'ло', slang + 'ли',
                slang + 'я', slang + 'в', slang + 'вши',
                # прилагательные и наречия
                slang + 'ый', slang + 'ого', slang + 'ому', slang + 'ым', slang + 'ом',
                slang + 'ая', slang + 'ой', slang + 'ую', slang + 'ою',
                slang + 'ое', slang + 'ые', slang + 'ых', slang + 'ыми',
                slang + 'о', slang + 'ее', slang + 'ей'
            ]
            
            for form in forms_to_check:
                # Используем поиск целых слов
                if re.search(r'\b' + re.escape(form) + r'\b', text, re.IGNORECASE):
                    text = replace_whole_words(text, form, normal)
                    words_found.append((form, normal))
                    break
    
    else:
        # Нормальный → Сленг с учетом всех форм
        reverse_dict = {v: k for k, v in DICTIONARY.items()}
        for normal, slang in reverse_dict.items():
            # Базовые формы для поиска
            forms_to_check = [
                normal,
                normal + 'а', normal + 'у', normal + 'ом', normal + 'е',
                normal + 'ы', normal + 'ов', normal + 'ам', normal + 'ами',
                normal + 'ю', normal + 'ешь', normal + 'ет', normal + 'ем', normal + 'ете', normal + 'ют',
                normal + 'л', normal + 'ла', normal + 'ло', normal + 'ли',
                normal + 'я', normal + 'в', normal + 'вши',
                normal + 'ый', normal + 'ого', normal + 'ому', normal + 'ым', normal + 'ом',
                normal + 'ая', normal + 'ой', normal + 'ую', normal + 'ою',
                normal + 'ое', normal + 'ые', normal + 'ых', normal + 'ыми',
                normal + 'о', normal + 'ее', normal + 'ей'
            ]
            
            for form in forms_to_check:
                # Используем поиск целых слов
                if re.search(r'\b' + re.escape(form) + r'\b', text, re.IGNORECASE):
                    text = replace_whole_words(text, form, slang)
                    words_found.append((form, slang))
                    break
    
    return text, len(words_found) > 0, words_found
# === КРАСИВЫЕ КЛАВИАТУРЫ ===
def get_main_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": f"{EMOJI['slang']} Сленг → Норма", "callback_data": "slang_to_normal"},
                {"text": f"{EMOJI['normal']} Норма → Сленг", "callback_data": "normal_to_slang"}
            ],
            [
                {"text": f"{EMOJI['search']} Поиск", "callback_data": "search_word"},
                {"text": f"{EMOJI['words']} Словарь", "callback_data": "random_words"}
            ],
            [
                {"text": f"{EMOJI['stats']} Статистика", "callback_data": "stats"},
                {"text": f"{EMOJI['chart']} Топ слов", "callback_data": "top_words"}
            ],
            [
                {"text": f"{EMOJI['brain']} Викторина", "callback_data": "quiz"},
                {"text": f"{EMOJI['help']} Помощь", "callback_data": "help"}
            ]
        ]
    }

def get_back_keyboard():
    return {
        "inline_keyboard": [
            [{"text": f"{EMOJI['back']} Главное меню", "callback_data": "back_to_main"}]
        ]
    }

def get_quiz_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": f"🎮 Начать", "callback_data": "start_quiz"},
                {"text": f"❌ Выйти", "callback_data": "back_to_main"}
            ]
        ]
    }

# === КРАСИВЫЕ СООБЩЕНИЯ ===
def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {
        "chat_id": chat_id, 
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        resp = http.request('POST', API_URL + "sendMessage", 
                          body=data, 
                          headers={'Content-Type': 'application/json; charset=utf-8'})
        return resp.status == 200
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False

# === СТАТИСТИКА И АНАЛИТИКА ===
def update_stats(user_id, direction, words_used=1):
    if user_id not in user_stats:
        user_stats[user_id] = {
            "slang_to_normal": 0,
            "normal_to_slang": 0,
            "total_translations": 0,
            "words_translated": 0,
            "quizzes_taken": 0,
            "correct_answers": 0,
            "first_use": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }
    
    stats = user_stats[user_id]
    stats[direction] += 1
    stats["total_translations"] += 1
    stats["words_translated"] += words_used
    stats["last_active"] = datetime.now().isoformat()

def get_user_stats(user_id):
    if user_id not in user_stats:
        return f"{EMOJI['stats']} <b>Статистика пуста</b>\n\nНачни использовать бота чтобы увидеть статистику! {EMOJI['rocket']}"
    
    stats = user_stats[user_id]
    accuracy = (stats["correct_answers"] / stats["quizzes_taken"] * 100) if stats["quizzes_taken"] > 0 else 0
    
    return f"""
{EMOJI['chart']} <b>ВАША СТАТИСТИКА</b> {EMOJI['chart']}

{EMOJI['translate']} <b>Переводы:</b> {stats['total_translations']}
{EMOJI['fire']} <b>Слов переведено:</b> {stats['words_translated']}
{EMOJI['brain']} <b>Викторин пройдено:</b> {stats['quizzes_taken']}
{EMOJI['star']} <b>Точность:</b> {accuracy:.1f}%

{EMOJI['slang']} <b>Сленг → Норма:</b> {stats['slang_to_normal']}
{EMOJI['normal']} <b>Норма → Сленг:</b> {stats['normal_to_slang']}

{EMOJI['time']} <b>Активен с:</b> {stats['first_use'][:10]}
"""

# === ТОП СЛОВ ===
def get_top_words():
    # В реальном приложении здесь была бы аналитика использования слов
    popular_words = [
        ("кринж", "стыд"), ("краш", "влюбленность"), ("рофл", "шутка"),
        ("агриться", "злиться"), ("чилить", "отдыхать"), ("вайб", "атмосфера"),
        ("имба", "круто"), ("го", "давай"), ("пруф", "доказательство")
    ]
    return popular_words

# === ВИКТОРИНА ===
class QuizManager:
    def __init__(self):
        self.questions = list(DICTIONARY.items())
        random.shuffle(self.questions)
    
    def get_question(self, user_id):
        if user_id not in user_sessions:
            user_sessions[user_id] = {"quiz_score": 0, "quiz_questions": 0}
        
        if not self.questions:
            self.questions = list(DICTIONARY.items())
            random.shuffle(self.questions)
        
        if self.questions:
            slang, normal = self.questions.pop()
            return {
                "question": f"Что означает <b>'{slang}'</b>?",
                "correct": normal,
                "options": self.generate_options(normal)
            }
        return None
    
    def generate_options(self, correct_answer):
        options = [correct_answer]
        other_words = random.sample(list(DICTIONARY.values()), min(3, len(DICTIONARY)))
        options.extend([w for w in other_words if w != correct_answer][:3])
        random.shuffle(options)
        return options

quiz_manager = QuizManager()

# === КРАСИВЫЕ ФОРМАТТЕРЫ ===
def format_welcome():
    return f"""
{EMOJI['wave']} <b>ПРИВЕТСТВУЕМ В СЛЕНГ-ПЕРЕВОДЧИКЕ!</b> {EMOJI['fire']}

{EMOJI['rocket']} <b>Умные возможности:</b>
• Перевод с учетом склонений слов
• Интерактивная викторина 
• Детальная статистика
• Топ популярных слов
• Быстрый поиск по словарю

{EMOJI['book']} <b>Словарь:</b> <code>{len(DICTIONARY)}</code> слов

{EMOJI['bulb']} <b>Теперь бот понимает разные формы слов!</b>
• "кринж", "кринжа", "кринжу", "кринжем"
• "агриться", "агрюсь", "агришься"
• и многие другие формы

<b>Выбери действие:</b>
"""

def format_translation_result(original, translated, mode, words_found):
    direction_emoji = EMOJI['slang'] if mode == "slang_to_normal" else EMOJI['normal']
    direction_text = "сленг → нормальный" if mode == "slang_to_normal" else "нормальный → сленг"
    
    words_info = ""
    if words_found:
        words_info = f"\n{EMOJI['mag']} <b>Найдено слов:</b> {len(words_found)}\n"
        for i, (orig, trans) in enumerate(words_found[:3]):
            words_info += f"• <code>{orig}</code> → <b>{trans}</b>\n"
    
    return f"""
{direction_emoji} <b>УСПЕШНЫЙ ПЕРЕВОД!</b> {EMOJI['tada']}

📝 <b>Исходный текст:</b>
<code>{original}</code>

🔄 <b>Результат:</b>
{translated}
{words_info}
💫 <i>Режим: {direction_text}</i>
"""

def format_no_translation(original, word_count):
    return f"""
{EMOJI['bulb']} <b>СОВЕТ ДЛЯ ПЕРЕВОДА</b>

📝 <b>Ваш текст:</b>
<code>{original}</code>

❌ <b>Не удалось найти сленговые слова</b>

💡 <b>Попробуй:</b>
• Использовать популярные слова из топа
• Проверить написание
• Воспользоваться поиском по словарю

📚 <b>Доступно слов:</b> {word_count}
"""

# === ОБРАБОТЧИКИ КОМАНД ===
def handle_start(chat_id, user_id):
    welcome = format_welcome()
    send_message(chat_id, welcome, get_main_keyboard())

def handle_help(chat_id):
    help_text = f"""
{EMOJI['help']} <b>ПОЛНОЕ РУКОВОДСТВО</b> {EMOJI['brain']}

{EMOJI['zap']} <b>Основные команды:</b>
/start - главное меню
/stats - ваша статистика
/quiz - начать викторину

{EMOJI['fire']} <b>Режимы перевода:</b>
• <b>Сленг → Норма</b> - переводит сленг на обычный язык
• <b>Норма → Сленг</b> - переводит обычную речь в сленг

{EMOJI['star']} <b>Дополнительные функции:</b>
• <b>Поиск</b> - найти слово в словаре
• <b>Словарь</b> - случайные слова
• <b>Статистика</b> - ваша активность
• <b>Топ слов</b> - популярные слова
• <b>Викторина</b> - проверить знания

{EMOJI['bulb']} <b>Теперь бот понимает разные формы слов!</b>
<code>Я испытываю кринж</code> → "Я испытываю <b>стыд</b>"
<code>От этого кринжа</code> → "От этого <b>стыда</b>"
<code>Не агрись по пустякам</code> → "Не <b>злись</b> по пустякам"
<code>Он агрится на всех</code> → "Он <b>злится</b> на всех"

{EMOJI['flash']} <b>Примеры для теста:</b>
<code>Этот видос просто кринж</code>
<code>Не агрись по пустякам</code>  
<code>Го играть в игры</code>
"""
    send_message(chat_id, help_text, get_back_keyboard())

def handle_stats(chat_id, user_id):
    stats_text = get_user_stats(user_id)
    send_message(chat_id, stats_text, get_back_keyboard())

def handle_random_words(chat_id):
    words = random.sample(list(DICTIONARY.items()), min(8, len(DICTIONARY)))
    words_text = f"{EMOJI['book']} <b>СЛУЧАЙНЫЕ СЛОВА ИЗ СЛОВАРЯ</b> {EMOJI['star']}\n\n"
    for i, (slang, normal) in enumerate(words, 1):
        words_text += f"{i}. <b>{slang}</b> → {normal}\n"
    words_text += f"\n{EMOJI['fire']} <b>Всего слов в словаре:</b> {len(DICTIONARY)}"
    send_message(chat_id, words_text, get_back_keyboard())

def handle_top_words(chat_id):
    top_words = get_top_words()
    words_text = f"{EMOJI['crown']} <b>ТОП ПОПУЛЯРНЫХ СЛОВ</b> {EMOJI['chart']}\n\n"
    for i, (slang, normal) in enumerate(top_words, 1):
        words_text += f"{EMOJI['medal']} <b>{slang}</b> → {normal}\n"
    send_message(chat_id, words_text, get_back_keyboard())

def handle_quiz(chat_id, user_id):
    quiz_text = f"""
{EMOJI['brain']} <b>ВИКТОРИНА ПО СЛЕНГУ</b> {EMOJI['tada']}

🎯 <b>Проверь свои знания!</b>
• Угадай значение сленговых слов
• 10 случайных вопросов  
• Следи за своей точностью

{EMOJI['star']} <b>Готов начать?</b>
"""
    send_message(chat_id, quiz_text, get_quiz_keyboard())

# === ОСНОВНАЯ ЛОГИКА ===
def answer_callback_query(callback_query_id, text=None):
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    try:
        http.request('POST', API_URL + "answerCallbackQuery",
                    body=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'})
    except:
        pass

def get_updates(offset=None):
    url = API_URL + "getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        resp = http.request('GET', url, fields=params)
        if resp.status == 200:
            return json.loads(resp.data.decode('utf-8'))
    except Exception as e:
        print(f"❌ Ошибка получения updates: {e}")
    return {"ok": False}

def main():
    offset = None
    print("🚀 УЛЬТРА-БОТ ЗАПУЩЕН!")
    print(f"📚 Словарь: {len(DICTIONARY)} слов")
    print(f"💫 Готов к умной работе со склонениями!")
    
    user_states = {}

    while True:
        try:
            updates = get_updates(offset)
            if not updates.get("ok"):
                time.sleep(2)
                continue

            for update in updates.get("result", []):
                offset = update["update_id"] + 1

                # === CALLBACK ОБРАБОТКА ===
                if "callback_query" in update:
                    q = update["callback_query"]
                    user_id = q["from"]["id"]
                    chat_id = q["message"]["chat"]["id"]
                    data = q["data"]

                    answer_callback_query(q["id"])
                    
                    if data == "back_to_main":
                        handle_start(chat_id, user_id)
                    elif data in ["slang_to_normal", "normal_to_slang"]:
                        user_modes[user_id] = data
                        user_states[user_id] = None
                        mode_text = "сленг → нормальный" if data == "slang_to_normal" else "нормальный → сленг"
                        send_message(chat_id, 
                                   f"{EMOJI['zap']} <b>РЕЖИМ АКТИВИРОВАН:</b> {mode_text}\n\nОтправь текст для перевода! {EMOJI['rocket']}",
                                   get_back_keyboard())
                    elif data == "search_word":
                        user_states[user_id] = "searching"
                        send_message(chat_id, 
                                   f"{EMOJI['search']} <b>РЕЖИМ ПОИСКА</b>\n\nВведи слово для поиска в словаре:",
                                   get_back_keyboard())
                    elif data == "stats":
                        handle_stats(chat_id, user_id)
                    elif data == "random_words":
                        handle_random_words(chat_id)
                    elif data == "top_words":
                        handle_top_words(chat_id)
                    elif data == "quiz":
                        handle_quiz(chat_id, user_id)
                    elif data == "help":
                        handle_help(chat_id)
                    continue

                # === СООБЩЕНИЯ ===
                if "message" not in update:
                    continue

                msg = update["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "").strip()

                if not text:
                    continue

                # Обработка команд
                if text.startswith('/'):
                    if text == '/start':
                        handle_start(chat_id, user_id)
                    elif text == '/stats':
                        handle_stats(chat_id, user_id)
                    elif text == '/help':
                        handle_help(chat_id)
                    elif text == '/quiz':
                        handle_quiz(chat_id, user_id)
                    continue

                # Обработка состояний
                current_state = user_states.get(user_id)
                
                if current_state == "searching":
                    results = [(s, n) for s, n in DICTIONARY.items() if text.lower() in s.lower() or text.lower() in n.lower()][:5]
                    if results:
                        search_result = f"{EMOJI['mag']} <b>РЕЗУЛЬТАТЫ ПОИСКА</b>\n\n"
                        for slang, normal in results:
                            search_result += f"• <b>{slang}</b> → {normal}\n"
                    else:
                        search_result = f"❌ По запросу '<b>{text}</b>' ничего не найдено"
                    send_message(chat_id, search_result, get_back_keyboard())
                    user_states[user_id] = None
                    continue

                # Основной перевод
                if user_id not in user_modes:
                    send_message(chat_id, 
                               f"{EMOJI['bulb']} <b>СНАЧАЛА ВЫБЕРИ РЕЖИМ!</b>\n\nИспользуй /start для выбора режима перевода {EMOJI['zap']}")
                    continue

                mode = user_modes[user_id]
                translated, changed, words_found = advanced_translate(text, mode)
                
                update_stats(user_id, mode, len(words_found))

                if changed:
                    response = format_translation_result(text, translated, mode, words_found)
                else:
                    response = format_no_translation(text, len(DICTIONARY))

                send_message(chat_id, response, get_back_keyboard())

        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
