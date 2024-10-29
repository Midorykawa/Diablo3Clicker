import tkinter as tk
from tkinter import messagebox
import pyautogui
import threading
import time
import json
import requests
from PIL import Image, ImageTk
import keyboard


BACKGROUND_IMAGE_PATH = "diablo.png"
CONFIG_FILE = "config.json"


pressing_active = False
pressing_thread = None
pressing_thread_lock = threading.Lock()


def check_for_updates():
    try:
        response = requests.get("https://example.com/version")  # URL для проверки версии
        if response.status_code == 200:
            latest_version = response.json().get("version")
            if latest_version != "1.0":
                messagebox.showinfo("Обновление найдено!", "Новая версия найдена. Обновитесь!")
    except Exception as e:
        print(f"Update check failed: {e}")


def save_config(config):
    with open(CONFIG_FILE, 'w') as config_file:
        json.dump(config, config_file)


def load_config():
    try:
        with open(CONFIG_FILE, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {"keys": ["1", "2", "3"], "hotkey": "f8"}


def press_keys(keys):
    global pressing_active
    while pressing_active:
        for key in keys:
            if not pressing_active:
                break
            pyautogui.press(key)
            time.sleep(0.3)


class KeyPresserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Key Presser App")
        self.root.geometry("1024x768")
        self.root.resizable(False, False)

        
        self.background_image = Image.open(BACKGROUND_IMAGE_PATH)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(root, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        
        self.config = load_config()

        
        self.select_keys_button = tk.Button(root, text="Выбор клавиш \n которые будут нажиматься", command=self.select_keys)
        self.select_keys_button.pack(pady=20)        
        self.select_hotkey_button = tk.Button(root, text="Выбор клавиши для старта программы", command=self.select_hotkey)
        self.select_hotkey_button.pack(pady=20)

        
        check_for_updates()

        
        self.set_hotkey()

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
        self.config["keys"] = keys
        save_config(self.config)
        messagebox.showinfo("Конфиг сохранен", "Клавиши сохранены!")

    def select_hotkey(self):
        
        hotkey_window = tk.Toplevel(self.root)
        hotkey_window.title("Выбор горячей клавиши")
        hotkey_window.geometry("300x150")

        tk.Label(hotkey_window, text="Пожалуйста нажмите клавишу\n для работы программы:").pack(pady=10)       
        self.hotkey_label = tk.Label(hotkey_window, text=self.config.get("hotkey", "Не выбрана"))
        self.hotkey_label.pack(pady=5)

        def on_key(event):
            self.config["hotkey"] = event.keysym
            self.hotkey_label.config(text=event.keysym)
            save_config(self.config)
            self.set_hotkey()
            hotkey_window.destroy()
            messagebox.showinfo("Конфигурация сохранена", "горячая клавиша сохранена!")

        hotkey_window.bind("<Key>", on_key)
        hotkey_window.focus_set()

    def set_hotkey(self):
        hotkey = self.config.get("hotkey", "f8")
        keyboard.add_hotkey(hotkey, self.toggle_pressing)

    def toggle_pressing(self):
        global pressing_active, pressing_thread
        with pressing_thread_lock:
            if pressing_active:
                pressing_active = False
            else:
                pressing_active = True
                keys = self.config.get("keys", ["1", "2", "3"])
                pressing_thread = threading.Thread(target=press_keys, args=(keys,), daemon=True)
                pressing_thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = KeyPresserApp(root)
    root.mainloop()