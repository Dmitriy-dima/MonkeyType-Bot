import json
import os
import threading
import keyboard
import time
import random
from pynput.keyboard import Controller, Key
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import tkinter as tk
from tkinter import messagebox, ttk

# Загрузка состояния из файла
state_file = "state.json"
if os.path.exists(state_file):
    with open(state_file, "r") as f:
        state = json.load(f)
else:
    state = {}

CHROMEDRIVER_PATH = 'path_to_chromedriver'  # Replace with the path to your chromedriver executable
remaining_text = None
global_driver = None
typed_words = set()

def fetch_text_from_website(url):
    global global_driver
    status_var.set("Статус: Получение текста...")  # Update status
    try:
        # Always close the existing WebDriver session if it exists
        if global_driver:
            global_driver.quit()  # Use quit instead of close to ensure the entire browser is closed
        # Always start a new WebDriver session
        global_driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH))
        global_driver.get(url)
        time.sleep(2)  # Allow time for the page to load
        word_elements = global_driver.find_elements(By.CSS_SELECTOR, '.word')
        words = [word.text for word in word_elements]

        return words    
    except Exception as e:
        messagebox.showerror("Error", f"Произошла ошибка при получении текста: {str(e)}")
        return []


def type_text(words, wpm, error_rate, language='en'):
    global stop_flag, remaining_text
    keyboard = Controller()
    typed_words.clear()

    character_mappings = {
        'en': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ',
        'ru': 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ '
    }

    # Calculate delay between each character based on desired wpm
    char_delay = 60 / (wpm * 5)  # Assuming average word length of 5

    while words:
        word = words.pop(0)
        for i, char in enumerate(word):
            if stop_flag:
                remaining_text = words
                return
            if random.random() < error_rate:
                random_char = random.choice(character_mappings[language])
                if random.random() < 0.5:  # Additional condition for double press
                    word = word[:i] + random_char + word[i]
                else:
                    word = word[:i] + random_char + word[i + 1:]
        for char in word:
            if stop_flag:
                return
            keyboard.press(char)
            keyboard.release(char)
            time.sleep(char_delay)  # Delay between each character
        if stop_flag:
            return
        keyboard.press(Key.space)
        keyboard.release(Key.space)
    remaining_text = None
    window.after(0, lambda: status_var.set("Статус: Закончил набор текста"))  # Update status


def start_typing():
    global stop_flag
    stop_flag = False  # Reset the stop flag

    website_url = url_entry.get()
    try:
        typing_speed_wpm = int(wpm_entry.get())
        error_rate = float(error_rate_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Неверная скорость набора текста или процент ошибок. Пожалуйста, введите числовые значения.")
        return
    language = language_var.get()

    # Always fetch new text from the website
    text_to_type = fetch_text_from_website(website_url)

    if text_to_type:
        status_var.set("Статус: Начинаем печатать...")  # Обновить статус
        time.sleep(2)  # Задержка для переключения фокуса на область ввода текста

        # Запуск type_text в отдельном потоке
        typing_thread = threading.Thread(target=type_text, args=(text_to_type, typing_speed_wpm, error_rate, language))
        typing_thread.start()

def stop_typing():
    global stop_flag, global_driver
    stop_flag = True
    status_var.set("Статус: Набор текста прекращен")
    close_driver()


def quit():
    window.quit()

def close_driver():
    if global_driver:
        global_driver.quit()
        global_driver = None

# GUI
window = tk.Tk()
window.title("Monkey Type Bot")
window.geometry("450x300")

frame = ttk.Frame(window, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Ввод URL
url_label = ttk.Label(frame, text="URL сайта:")
url_label.grid(row=0, column=0, sticky=tk.W)
url_entry = ttk.Entry(frame, width=50)
url_entry.grid(row=0, column=1)

# Ввод WPM
wpm_label = ttk.Label(frame, text="Скорость набора текста (WPM):")
wpm_label.grid(row=1, column=0, sticky=tk.W)
wpm_entry = ttk.Entry(frame, width=20)
wpm_entry.grid(row=1, column=1)

# Ввод процента ошибок
error_rate_label = ttk.Label(frame, text="Процент ошибок (0.05 = 5%):")
error_rate_label.grid(row=2, column=0, sticky=tk.W)
error_rate_entry = ttk.Entry(frame, width=20)
error_rate_entry.grid(row=2, column=1)

# Выбор языка
language_label = ttk.Label(frame, text="Язык (для печатания):")
language_label.grid(row=3, column=0, sticky=tk.W)

language_var = tk.StringVar(window)
language_var.set('en') # Выбор языка по умолчанию

language_options = [('English', 'en'), ('Русский', 'ru')]

for i, (option_text, option_value) in enumerate(language_options):
    language_radio = ttk.Radiobutton(frame, text=option_text, variable=language_var, value=option_value)
    language_radio.grid(row=3, column=1+i, sticky=tk.W)

# Кнопка запуска
start_button = ttk.Button(frame, text="Начать печатать", command=start_typing)
start_button.grid(row=4, column=0, columnspan=2, pady=10)

start_hotkey_description = ttk.Label(frame, text="Hotkey: Z")
start_hotkey_description.grid(row=4, column=2, padx=10)

window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)

# Кнопка остановки
stop_button = ttk.Button(frame, text="Перестать печатать", command=stop_typing)
stop_button.grid(row=5, column=0, columnspan=2, pady=10)

stop_hotkey_description = ttk.Label(frame, text="Hotkey: X")
stop_hotkey_description.grid(row=5, column=2, padx=10)

# Кнопка выхода
quit_button = ttk.Button(frame, text="Выход", command=window.destroy)
quit_button.grid(row=6, column=0, columnspan=2, pady=10)

quit_hotkey_description = ttk.Label(frame, text="Hotkey: Ctrl + Q")
quit_hotkey_description.grid(row=6, column=2, padx=10)

status_var = tk.StringVar()
status_var.set("Статус: Готово")

# Текст состояния
status_label = ttk.Label(frame, textvariable=status_var)
status_label.grid(row=7, column=0, columnspan=2, sticky=tk.W)

# Функция сохранения состояния
def save_state():
    state = {
        "url": url_entry.get(),
        "wpm": wpm_entry.get(),
        "error_rate": error_rate_entry.get(),
        "language": language_var.get(),
    }
    with open(state_file, "w") as f:
        json.dump(state, f)
    status_var.set("Статус: Состояние сохранено")  # Обновить статус


# Функция копирования
def copy_text():
    focused_widget = window.focus_get()
    if isinstance(focused_widget, tk.Entry):
        selected_text = focused_widget.selection_get()
        window.clipboard_clear()
        window.clipboard_append(selected_text)

# Функция вставки
def paste_text():
    focused_widget = window.focus_get()
    if isinstance(focused_widget, tk.Entry):
        focused_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        focused_widget.insert(tk.INSERT, window.clipboard_get())

save_state_button = ttk.Button(frame, text="Сохранить Состояние", command=save_state)
save_state_button.grid(row=11, column=0, columnspan=2, pady=10)

# Привязать горячие клавиши
keyboard.add_hotkey('z', start_typing)  # Control + T для начала
keyboard.add_hotkey('x', stop_typing)  # Control + X для остановки
keyboard.add_hotkey('ctrl + q', quit)  # Control + Q для выхода

keyboard.add_hotkey('ctrl+c', copy_text)
keyboard.add_hotkey('ctrl+v', paste_text)


# Состояние загрузки
url_entry.insert(0, state.get("url", ""))
wpm_entry.insert(0, state.get("wpm", ""))
error_rate_entry.insert(0, state.get("error_rate", ""))
language_var.set(state.get("language", "en"))

window.mainloop()