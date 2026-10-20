"""Небольшие функции, настройки и работа с файлами игры."""

import json
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
WORDS_FILE = BASE_DIR / "words.json"
GALLOWS_DIR = BASE_DIR / "gallows"
MAX_MISTAKES = 6
EXIT_COMMAND = "/выход"
RUSSIAN_LETTERS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"


def normalize(text):
    """Убрать внешние пробелы и привести буквы к нижнему регистру."""
    return text.strip().lower()


def valid_word(word):
    return isinstance(word, str) and bool(word) and all(
        letter in RUSSIAN_LETTERS for letter in word
    )


def valid_entry(entry):
    return (
        isinstance(entry, dict)
        and valid_word(entry.get("word"))
        and isinstance(entry.get("description"), str)
        and bool(entry["description"].strip())
    )


def load_words():
    """Прочитать и проверить словарь, объяснив ошибку пользователю."""
    try:
        with WORDS_FILE.open(encoding="utf-8") as source:
            words = json.load(source)
        if not isinstance(words, list) or not words:
            raise ValueError("В файле должен быть непустой список слов.")
        if not all(valid_entry(entry) for entry in words):
            raise ValueError(
                "Каждая запись должна содержать word (русское слово "
                "строчными буквами) и непустое description."
            )
        return words
    except (OSError, ValueError) as error:
        print(f"Не удалось загрузить слова: {error}")
        return []


def has_words(words):
    return bool(words)


def show_intro():
    print("ВИСЕЛИЦА НА ПОЛЕ ЧУДЕС")
    print("Угадывайте русские буквы или слово целиком.")
    print("Ошибка добавляет часть человечка. Шесть ошибок — поражение.")
    print("Повторный и некорректный ввод не считаются ошибками.")
    print("Буквы е и ё различаются. Для выхода введите /выход.\n")


def create_round(words):
    entry = random.choice(words)
    return {
        "word": entry["word"],
        "description": entry["description"],
        "opened": set(),
        "attempts": [],
        "mistakes": 0,
        "stopped": False,
    }


def is_won(state):
    return set(state["word"]).issubset(state["opened"])


def round_active(state):
    return (
        not state["stopped"]
        and state["mistakes"] < MAX_MISTAKES
        and not is_won(state)
    )


def show_gallows(state):
    """На каждом вызове прочитать соответствующий рисунок из файла."""
    path = GALLOWS_DIR / f'{state["mistakes"]}.txt'
    try:
        print(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        print(f"Не удалось прочитать рисунок {path.name}: {error}")
        stop_round(state)


def show_board(state):
    print(f'\nПодсказка: {state["description"]}')
    print("Слово:", " ".join(
        letter.upper() if letter in state["opened"] else "_"
        for letter in state["word"]
    ))
    if state["attempts"]:
        print("Уже пробовали:", ", ".join(state["attempts"]))


def read_answer():
    try:
        return normalize(input("Буква или слово: "))
    except (EOFError, KeyboardInterrupt):
        print()
        return EXIT_COMMAND


def is_exit(answer):
    return answer == EXIT_COMMAND


def is_invalid(answer):
    return not valid_word(answer)


def was_tried(state, answer):
    return answer in state["attempts"]


def remember_answer(state, answer):
    state["attempts"].append(answer)


def is_correct(state, answer):
    if len(answer) == 1:
        return answer in state["word"]
    return answer == state["word"]


def reveal_answer(state, answer):
    state["opened"].update(answer)


def add_mistake(state):
    state["mistakes"] += 1


def stop_round(state):
    state["stopped"] = True


def was_stopped(state):
    return state["stopped"]


def disabled():
    return False


def show_invalid():
    print("Введите одну русскую букву или слово без пробелов и цифр.")


def show_repeated():
    print("Такой ответ уже был. Попробуйте другой!")


def show_correct():
    print("Верно!")


def show_wrong():
    print("Неверно! На виселице появилась новая часть человечка.")


def show_result(state):
    if was_stopped(state):
        print("Игра прервана.")
    elif is_won(state):
        print(f'\nПобеда! Вы угадали слово: {state["word"].upper()}')
    else:
        print(f'\nВы проиграли. Загаданное слово: {state["word"].upper()}')


def ask_again():
    while True:
        try:
            answer = normalize(input("\nСыграть ещё? (да/нет): "))
        except (EOFError, KeyboardInterrupt):
            print()
            return False
        if answer in ("да", "д"):
            return True
        if answer in ("нет", "н", EXIT_COMMAND):
            return False
        print("Введите «да» или «нет».")


def show_goodbye():
    print("Спасибо за игру!")
