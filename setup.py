from cx_Freeze import setup, Executable
import os


os.environ['TCL_LIBRARY'] = r"C:\Users\shirooyaa\AppData\Local\Programs\Python\Python312\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Users\shirooyaa\AppData\Local\Programs\Python\Python312\tcl\tk8.6"

# Опции для сборки
build_exe_options = {
    "packages": ["os", "tkinter", "requests", "PIL", "pyautogui", "keyboard", "threading"],
    "include_files": [
        
        (r"C:\Users\shirooyaa\AppData\Local\Programs\Python\Python312\tcl\tcl8.6", "tcl/tcl8.6"),
        (r"C:\Users\shirooyaa\AppData\Local\Programs\Python\Python312\tcl\tk8.6", "tcl/tk8.6"),
        
        "diablo.webp"
    ]
}


base = None
if os.name == 'nt':
    base = 'Win32GUI'  

setup(
    name="KeyPresserApp",
    version="1.0",
    description="Tkinter-based key presser application",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)
