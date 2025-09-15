import os
import shlex
import subprocess

def get_prompt():
    """Формирует приглашение к вводу в формате username@hostname:directory$"""
    username = os.getenv('USER') or os.getenv('USERNAME')  # Получаем имя пользователя
    hostname = os.getenv('HOSTNAME') or subprocess.getoutput('hostname')  # Получаем имя хоста
    current_dir = os.getcwd()  # Текущая директория
    return f"{username}@{hostname}:{current_dir}$ "

def parse_command(input_line):
    """Парсит команду и раскрывает переменные окружения"""
    # Раскрываем переменные окружения перед парсингом
    expanded_line = os.path.expandvars(input_line)
    # Разбиваем на аргументы с учетом кавычек
    return expanded_line.split()

def main():
    """Основной цикл REPL (Read-Eval-Print Loop)"""
    print("Добро пожаловать в эмулятор командной строки!")
    print("Введите 'exit' для выхода.")
    
    while True:
        try:
            # Выводим приглашение и читаем ввод
            user_input = input(get_prompt()).strip()
            
            # Пропускаем пустые строки
            if not user_input:
                continue
                
            # Парсим команду
            args = parse_command(user_input)
            command = args[0]
            
            # Обрабатываем команду exit
            if command == 'exit':
                print("Выход из эмулятора")
                break
                
            # Обрабатываем команду ls
            elif command == 'ls':
                print(f"Команда 'ls' вызвана с аргументами: {args[1:]}")
                
            # Обрабатываем команду cd
            elif command == 'cd':
                print(f"Команда 'cd' вызвана с аргументами: {args[1:]}")
                
            # Неизвестная команда
            else:
                print(f"Ошибка: неизвестная команда '{command}'")
                
        except KeyboardInterrupt:
            print("\nДля выхода введите 'exit'")
        except Exception as e:
            print(f"Ошибка выполнения: {e}")

if __name__ == "__main__":
    main()