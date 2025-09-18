import os
import sys
import subprocess
import argparse

def get_prompt():
    """Формирует приглашение к вводу в формате username@hostname:directory$"""
    username = os.getenv('USER') or os.getenv('USERNAME')
    hostname = os.getenv('HOSTNAME') or subprocess.getoutput('hostname')
    current_dir = os.getcwd()
    return f"{username}@{hostname}:{current_dir}$ "

def parse_command(input_line):
    """Парсит команду и раскрывает переменные окружения"""
    # Раскрываем переменные окружения
    expanded_line = os.path.expandvars(input_line)
    
    return expanded_line.split()

def execute_script(script_path, vfs_path):
    """Выполняет стартовый скрипт"""
    try:
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        print(f"Выполнение скрипта: {script_path}")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):  # Пропускаем пустые строки и комментарии
                continue
                
            # Имитируем ввод пользователя
            print(get_prompt() + line)
            
            args = parse_command(line)
            if not args:
                continue
                
            command = args[0]
            
            if command == 'exit':
                print("Выход из эмулятора")
                return True
            elif command == 'ls':
                print(f"Команда 'ls' вызвана с аргументами: {args[1:]}")
            elif command == 'cd':
                print(f"Команда 'cd' вызвана с аргументами: {args[1:]}")
            else:
                print(f"Ошибка: неизвестная команда '{command}'")
                print(f"Остановка скрипта на строке {line_num} из-за ошибки")
                return False
                
        return True
        
    except FileNotFoundError:
        print(f"Ошибка: скрипт '{script_path}' не найден")
        return False
    except Exception as e:
        print(f"Ошибка выполнения скрипта: {e}")
        return False

def main():
    """Основной цикл REPL с поддержкой параметров командной строки"""
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description='Эмулятор командной строки UNIX')
    parser.add_argument('--vfs', help='Путь к физическому расположению VFS')
    parser.add_argument('--script', help='Путь к стартовому скрипту')
    
    args = parser.parse_args()
    
    # Отладочный вывод параметров
    print("=== КОНФИГУРАЦИЯ ЭМУЛЯТОРА ===")
    print(f"VFS путь: {args.vfs or 'Не указан'}")
    print(f"Скрипт: {args.script or 'Не указан'}")
    print("===============================")
    
    # Выполнение скрипта
    if args.script:
        success = execute_script(args.script, args.vfs)
        if not success:
            sys.exit(1)
        return
    
    # Интерактивный режим
    print("Добро пожаловать в эмулятор командной строки!")
    print("Введите 'exit' для выхода.")
    
    while True:
        try:
            user_input = input(get_prompt()).strip()
            
            if not user_input:
                continue
                
            cmd_args = parse_command(user_input)
            command = cmd_args[0]
            
            if command == 'exit':
                print("Выход из эмулятора")
                break
            elif command == 'ls':
                print(f"Команда 'ls' вызвана с аргументами: {cmd_args[1:]}")
            elif command == 'cd':
                print(f"Команда 'cd' вызвана с аргументами: {cmd_args[1:]}")
            else:
                print(f"Ошибка: неизвестная команда '{command}'")
                
        except KeyboardInterrupt:
            print("\nДля выхода введите 'exit'")
        except Exception as e:
            print(f"Ошибка выполнения: {e}")

if __name__ == "__main__":
    main()