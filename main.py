import tkinter as tk
from tkinter import scrolledtext
import os
import re

class SimpleShell:
    def __init__(self, root):
        self.root = root
        self.username = os.getlogin()
        try:
            self.hostname = os.uname().nodename
        except:
            self.hostname = "localhost"
        self.current_dir = os.getcwd()
        
        # Настройка окна
        self.root.title(f"Эмулятор - [{self.username}@{self.hostname}]")
        self.root.geometry("700x500")
        
        self.create_widgets()
        self.print_text("=== Простой эмулятор терминала ===\n")
        self.print_text("Команды: ls, cd, exit, help\n")

    
    def create_widgets(self):
        # Текстовое поле для вывода
        self.output_area = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD,
            bg='black',
            fg='white',
            font=('Courier New', 10)
        )
        self.output_area.pack(fill='both', expand=True, padx=5, pady=5)
        self.output_area.config(state='disabled')
        
        # Фрейм для ввода
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        # Приглашение
        self.prompt = tk.Label(
            input_frame, 
            text=f"{self.username}@{self.hostname}$ ",
            fg='green',
            bg='black',
            font=('Courier New', 10)
        )
        self.prompt.pack(side='left')
        
        # Поле ввода команды
        self.command_input = tk.Entry(
            input_frame,
            bg='black',
            fg='white',
            font=('Courier New', 10),
            width=50
        )
        self.command_input.pack(side='left', fill='x', expand=True, padx=5)
        self.command_input.bind('<Return>', self.run_command)
        self.command_input.focus()
    
    def print_text(self, text):
        """Вывод текста в область"""
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)
        self.output_area.config(state='disabled')
    
    def expand_vars(self, text):
        """Раскрытие переменных типа $HOME"""
        def replace(match):
            var = match.group(1)
            return os.getenv(var, f'${var}')
        
        return re.sub(r'\$(\w+)', replace, text)
    
    def run_command(self, event):
        """Обработка команды"""
        cmd_text = self.command_input.get().strip()
        self.command_input.delete(0, tk.END)
        
        if not cmd_text:
            return
        
        self.print_text(f"{self.prompt.cget('text')}{cmd_text}\n")
        
        # Раскрытие переменных
        cmd_text = self.expand_vars(cmd_text)
        
        # Разделение на команду и аргументы
        parts = cmd_text.split()
        command = parts[0]
        args = parts[1:]
        
        # Выполнение команды
        if command == "exit":
            self.do_exit()
        elif command == "ls":
            self.do_ls(args)
        elif command == "cd":
            self.do_cd(args)
        elif command == "help":
            self.do_help()
        else:
            self.print_text(f"Ошибка: неизвестная команда '{command}'\n")
    
    def do_exit(self):
        self.root.quit()
    
    def do_ls(self, args):
        self.print_text(f"Команда 'ls' вызвана с аргументами: {args}\n")
        
        if not args:
            self.print_text("ls: вывод списка файлов в текущей директории (заглушка)\n")
        else:
            self.print_text(f"ls: вывод списка файлов в {args[0]} (заглушка)\n")
        
    
    def do_cd(self, args):
        self.print_text(f"Команда 'cd' вызвана с аргументами: {args}\n")
        
        if not args:
            self.print_text("cd: переход в домашнюю директорию (заглушка)\n")
        else:
            self.print_text(f"cd: переход в директорию {args[0]} (заглушка)\n")
        
    
    def do_help(self):
        help_text = """
СПРАВКА ПО КОМАНДАМ:

ls [путь]    - показать имя команды и аргументы
             Пример: ls /home → выведет "ls вызвана с аргументами: ['/home']"

cd [путь]    - показать имя команды и аргументы  
             Пример: cd /tmp → выведет "cd вызвана с аргументами: ['/tmp']"

exit         - выход из эмулятора
help         - эта справка

Переменные окружения: $HOME, $USER, $PWD и др.
Пример: cd $HOME → cd вызвана с аргументами: ['/home/username']

"""
        self.print_text(help_text)

def main():
    root = tk.Tk()
    app = SimpleShell(root)
    root.mainloop()

if __name__ == "__main__":
    main()