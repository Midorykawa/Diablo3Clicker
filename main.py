import tkinter as tk
from tkinter import messagebox
import pyautogui
import threading
import time
import json
import requests
from PIL import Image, ImageTk
import keyboard
import os
import sys
import shutil
import zipfile
import subprocess
import platform
import configparser


def set_tk_environment():
    if getattr(sys, 'frozen', False):
        
        base_path = sys._MEIPASS
        os.environ['TCL_LIBRARY'] = os.path.join(base_path, 'tcl', 'tcl8.6')
        os.environ['TK_LIBRARY'] = os.path.join(base_path, 'tcl', 'tk8.6')


CURRENT_VERSION = "1.0.1"
CONFIG_FILE = "config.json"
BACKGROUND_IMAGE_NAME = "diablo.webp"
GITHUB_API_LATEST_RELEASE_URL = "https://api.github.com/repos/Midorykawa/Diablo3Clicker/releases/latest"


if getattr(sys, 'frozen', False):
    
    application_path = sys._MEIPASS
else:
    
    application_path = os.path.dirname(os.path.abspath(__file__))

BACKGROUND_IMAGE_PATH = os.path.join(application_path, BACKGROUND_IMAGE_NAME)

#
pressing_event = threading.Event()
lock = threading.Lock()


def check_for_updates():
    try:
        response = requests.get(GITHUB_API_LATEST_RELEASE_URL, timeout=5)
        response.raise_for_status()
        latest_release = response.json()
        latest_version = latest_release.get("tag_name")
        if latest_version and latest_version != CURRENT_VERSION:
            download_url = latest_release["assets"][0]["browser_download_url"]
            messagebox.showinfo("Обновление найдено!", f"Доступна новая версия {latest_version}. Обновляем...")
            download_and_update(download_url)
    except requests.exceptions.RequestException as e:
        print(f"Update check failed: {e}")


def download_and_update(download_url):
    try:
        response = requests.get(download_url, stream=True, timeout=10)
        response.raise_for_status()
        update_path = os.path.join(application_path, "update.zip")
        with open(update_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        messagebox.showinfo("Обновление завершено", "Перезапустите приложение для установки обновления.")
        install_update(update_path)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка обновления", f"Не удалось скачать обновление: {e}")


def install_update(update_path):
    try:
        temp_update_folder = os.path.join(application_path, "temp_update")
        if os.path.exists(temp_update_folder):
            shutil.rmtree(temp_update_folder)
        os.makedirs(temp_update_folder)

        with zipfile.ZipFile(update_path, 'r') as zip_ref:
            zip_ref.extractall(temp_update_folder)

        for root, dirs, files in os.walk(temp_update_folder):
            for file in files:
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(source_file, temp_update_folder)
                destination_file = os.path.join(application_path, relative_path)
                shutil.move(source_file, destination_file)

        shutil.rmtree(temp_update_folder)
        os.remove(update_path)
        restart_application()
    except Exception as e:
        messagebox.showerror("Ошибка установки обновления", f"Не удалось установить обновление: {e}")


def restart_application():
    try:
        if platform.system() == "Windows":
            os.startfile(sys.executable)
        elif platform.system() == "Darwin":
            subprocess.call(["open", sys.executable])
        elif platform.system() == "Linux":
            subprocess.call(["python3", sys.executable])
        sys.exit()
    except Exception as e:
        messagebox.showerror("Ошибка перезапуска", f"Не удалось перезапустить приложение: {e}")


def save_config(config):
    with lock:
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file, indent=4)


def load_config():
    try:
        with lock:
            with open(CONFIG_FILE, 'r') as config_file:
                return json.load(config_file)
    except FileNotFoundError:
        return {"keys": ["1", "2", "3"], "hotkey": "f8"}


def press_keys(keys):
    while pressing_event.is_set():
        for key in keys:
            if not pressing_event.is_set():
                break
            pyautogui.press(key)
            time.sleep(0.3)


class KeyPresserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Key Presser App")
        self.root.geometry("1024x768")
        self.root.resizable(False, False)

        
        self.load_background_image()

        self.config = load_config()

        
        self.init_ui()

        
        check_for_updates()

        
        self.set_hotkey()

        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_background_image(self):
        try:
            self.background_image = Image.open(BACKGROUND_IMAGE_PATH)
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.background_label = tk.Label(self.root, image=self.background_photo)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            self.root.configure(bg='gray')

    def init_ui(self):
        
        self.select_keys_button = tk.Button(self.root, text="Выбор клавиш \n которые будут нажиматься", command=self.select_keys)
        self.select_keys_button.pack(pady=20)

        
        self.select_hotkey_button = tk.Button(self.root, text="Выбор клавиши для старта программы", command=self.select_hotkey)
        self.select_hotkey_button.pack(pady=20)

    def select_keys(self):
        keys_window = tk.Toplevel(self.root)
        keys_window.title("Выбор клавиш")
        keys_window.geometry("300x200")

        tk.Label(keys_window, text="Введите клавиши \n которые будут прожиматься, через запятую:").pack(pady=10)
        self.keys_entry = tk.Entry(keys_window)
        self.keys_entry.pack(pady=5)
        self.keys_entry.insert(0, ", ".join(self.config["keys"]))

        tk.Button(keys_window, text="Сохранить", command=self.save_keys).pack(pady=10)

    def save_keys(self):
        keys = self.keys_entry.get().replace(" ", "").split(",")
        if all(len(key) > 0 for key in keys):
            self.config["keys"] = keys
            save_config(self.config)
            messagebox.showinfo("Конфиг сохранен", "Клавиши сохранены!")
        else:
            messagebox.showerror("Ошибка", "Неправильные клавиши!")

    def select_hotkey(self):
        hotkey_window = tk.Toplevel(self.root)
        hotkey_window.title("Выбор горячей клавиши")
        hotkey_window.geometry("300x150")

        tk.Label(hotkey_window, text="Пожалуйста нажмите клавишу\n для работы программы:").pack(pady=10)
        self.hotkey_label = tk.Label(hotkey_window, text=self.config.get("hotkey", "Не выбрана"))
        self.hotkey_label.pack(pady=5)

        def on_key(event):
            if hasattr(event, 'keysym'):
                self.config["hotkey"] = event.keysym
                self.hotkey_label.config(text=event.keysym)
                save_config(self.config)
                self.set_hotkey()
                hotkey_window.destroy()
                messagebox.showinfo("Конфигурация сохранена", "Горячая клавиша сохранена!")

        hotkey_window.bind("<Key>", on_key)
        hotkey_window.focus_set()

    def set_hotkey(self):
        hotkey = self.config.get("hotkey", "f8")
        keyboard.add_hotkey(hotkey, self.toggle_pressing)

    def toggle_pressing(self):
        if pressing_event.is_set():
            pressing_event.clear()
        else:
            pressing_event.set()
            keys = self.config.get("keys", ["1", "2", "3"])
            pressing_thread = threading.Thread(target=press_keys, args=(keys,), daemon=True)
            pressing_thread.start()

    def on_closing(self):
        pressing_event.clear()
        self.root.destroy()

if __name__ == "__main__":
    set_tk_environment()
    root = tk.Tk()
    app = KeyPresserApp(root)
    root.mainloop()
