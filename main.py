import tkinter as tk
from tkinter import scrolledtext
import os
import re
import sys
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime

class SimpleShell:
    def __init__(self, root, vfs_path, log_file, startup_script):
        self.root = root
        self.username = os.getlogin()
        try:
            self.hostname = os.uname().nodename
        except:
            self.hostname = "localhost"
        self.current_dir = os.getcwd()
        
        self.vfs_path = vfs_path
        self.log_file = log_file
        self.startup_script = startup_script
        
        print(f"VFS путь: {self.vfs_path}")
        print(f"Лог-файл: {self.log_file}")
        print(f"Стартовый скрипт: {self.startup_script}")
        
        self.root.title(f"Эмулятор - [{self.username}@{self.hostname}]")
        self.root.geometry("700x500")
        
        self.create_widgets()
        self.print_text("=== Простой эмулятор терминала ===\n")
        self.print_text("Команды: ls, cd, exit, help\n")

        if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<shell_log>\n')
        
        if self.startup_script:
            self.run_script()

    def init_log(self):
        """Создание пустого XML лог-файла"""
        try:
            root = ET.Element("shell_log")
            tree = ET.ElementTree(root)
            tree.write(self.log_file)
        except:
            pass

    def log_command(self, command, args, success=True, error=""):
        """Запись команды в лог"""
        try:
            timestamp = datetime.now().isoformat()
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write('\n<event>\n')
                f.write(f'  <timestamp>{timestamp}</timestamp>\n')
                f.write(f'  <username>{self.username}</username>\n')
                f.write(f'  <command>{command}</command>\n')
                f.write(f'  <arguments>{args}</arguments>\n')
                f.write(f'  <success>{success}</success>\n')
                if error:
                    f.write(f'  <error>{error}</error>\n')
                f.write('</event>\n')
                
        except Exception as e:
            print(f"Ошибка логирования: {e}")

    def run_command(self, event):
        """Обработка команды (для привязки клавиши Enter)"""
        cmd_text = self.command_input.get().strip()
        self.command_input.delete(0, tk.END)
        
        if not cmd_text:
            return
        
        self.print_text(f"{self.prompt.cget('text')}{cmd_text}\n")
        
        cmd_text = self.expand_vars(cmd_text)
        
        parts = cmd_text.split()
        command = parts[0]
        args = parts[1:]
        
        if command == "exit":
            self.log_command("exit", args, True)
            self.do_exit()
        elif command == "ls":
            self.do_ls(args)
        elif command == "cd":
            self.do_cd(args)
        elif command == "help":
            self.do_help()
        else:
            self.print_text(f"Ошибка: неизвестная команда '{command}'\n")
            self.log_command(command, args, False, "Неизвестная команда")
    
    def create_widgets(self):
        self.output_area = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD,
            bg='black',
            fg='white',
            font=('Courier New', 10)
        )
        self.output_area.pack(fill='both', expand=True, padx=5, pady=5)
        self.output_area.config(state='disabled')
        
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        self.prompt = tk.Label(
            input_frame, 
            text=f"{self.username}@{self.hostname}$ ",
            fg='green',
            bg='black',
            font=('Courier New', 10)
        )
        self.prompt.pack(side='left')
        
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
        """Раскрытие переменных типа $HOME, $USER, $PWD"""
        def replace(match):
            var = match.group(1)
            if var == "HOME":
                return os.path.expanduser("~")
            elif var == "USER":
                return self.username
            elif var == "PWD":
                return self.current_dir
            elif var == "HOSTNAME":
                return self.hostname
            else:
                return os.getenv(var, f'${var}')
        
        return re.sub(r'\$(\w+)', replace, text)
    
    def run_script(self):
        """Выполнение стартового скрипта"""
        if not os.path.exists(self.startup_script):
            self.print_text(f"Ошибка: скрипт '{self.startup_script}' не найден\n")
            self.log_command("script_error", [self.startup_script], False, "Файл не найден")
            return
        
        self.print_text(f"\n=== Выполнение скрипта {self.startup_script} ===\n")
        
        try:
            with open(self.startup_script, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue  
                    
                    self.print_text(f"{self.prompt.cget('text')}{line}\n")
                    
                    try:
                        cmd_text = self.expand_vars(line)
                        if not cmd_text.strip():  
                            continue
                            
                        parts = cmd_text.split()
                        if not parts:  
                            continue
                            
                        command = parts[0]
                        args = parts[1:] if len(parts) > 1 else []
                        
                        if command == "exit":
                            break
                        elif command == "ls":
                            self.do_ls(args)
                        elif command == "cd":
                            self.do_cd(args)
                        elif command == "help":
                            self.do_help()
                        else:
                            self.print_text(f"Ошибка в строке {line_num}: неизвестная команда '{command}'\n")
                            self.log_command("script_error", [f"line {line_num}: {command}"], False, "Неизвестная команда")
                            
                    except Exception as e:
                        self.print_text(f"Ошибка в строке {line_num}: {str(e)}\n")
                        self.log_command("script_error", [f"line {line_num}"], False, str(e))
                        continue  
                        
        except Exception as e:
            self.print_text(f"Ошибка чтения скрипта: {str(e)}\n")
            self.log_command("script_error", [self.startup_script], False, str(e))
        
        self.print_text("\n=== Скрипт выполнен ===\n")
    
    def do_exit(self):
        self.root.quit()
    
    def do_ls(self, args):
        self.print_text(f"Команда 'ls' вызвана с аргументами: {args}\n")
        self.log_command("ls", args, True)
        
        if not args:
            self.print_text("ls: вывод списка файлов в текущей директории (заглушка)\n")
        else:
            self.print_text(f"ls: вывод списка файлов в {args[0]} (заглушка)\n")
        
    def do_cd(self, args):
        self.print_text(f"Команда 'cd' вызвана с аргументами: {args}\n")
        self.log_command("cd", args, True)
        
        if not args:
            self.print_text("cd: переход в домашнюю директорию (заглушка)\n")
        else:
            self.print_text(f"cd: переход в директорию {args[0]} (заглушка)\n")
    
    def do_help(self):
        help_text = """
СПРАВКА ПО КОМАНДАМ:

ls [путь]    - показать имя команды и аргументы
             Пример: ls /home → выведет "ls вызвана с аргументами: ['/home']"
             Пример: ls $HOME → выведет "ls вызвана с аргументами: ['/home/username']"

cd [путь]    - показать имя команды и аргументы  
             Пример: cd /tmp → выведет "cd вызвана с аргументами: ['/tmp']"
             Пример: cd $HOME → выведет "cd вызвана с аргументами: ['/home/username']"

exit         - выход из эмулятора
help         - эта справка
"""
        self.print_text(help_text)
        self.log_command("help", [], True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vfs', default='.')
    parser.add_argument('--log', default='shell.xml')
    parser.add_argument('--script', default=None)
    args = parser.parse_args()
    
    root = tk.Tk()
    app = SimpleShell(root, args.vfs, args.log, args.script)
    root.mainloop()

if __name__ == "__main__":
    main()