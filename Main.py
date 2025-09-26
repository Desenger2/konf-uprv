import os
import sys
import subprocess
import argparse
import xml.etree.ElementTree as ET
import base64

class VFSNode:
    """Узел виртуальной файловой системы"""
    def __init__(self, name, is_file=False, content=None, parent=None):
        self.name = name
        self.is_file = is_file
        self.content = content
        self.children = {}
        self.parent = parent

class VFS:
    """Виртуальная файловая система"""
    def __init__(self):
        self.root = VFSNode("", is_file=False)
        self.current_dir = self.root
    
    def load_from_xml(self, xml_path):
        """Загружает VFS из XML файла"""
        try:
            if not os.path.exists(xml_path):
                return False, "Файл VFS не найден"
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            if root.tag != "vfs":
                return False, "Неверный формат XML: ожидается корневой элемент <vfs>"
            
            self.root = VFSNode("", is_file=False)
            self.current_dir = self.root
            
            for child in root:
                self._parse_node(child, self.root)
            
            return True, "VFS успешно загружена"
            
        except ET.ParseError as e:
            return False, f"Ошибка парсинга XML: {e}"
        except Exception as e:
            return False, f"Ошибка загрузки VFS: {e}"
    
    def _parse_node(self, element, parent_node):
        """Рекурсивно парсит XML элемент в узел VFS"""
        name = element.get("name", "")
        is_file = (element.tag == "file")
        
        node = VFSNode(name, is_file, parent=parent_node)
        
        if is_file:
            # Декодируем содержимое файла из base64
            content = element.text.strip() if element.text else ""
            if content:
                try:
                    node.content = base64.b64decode(content).decode('utf-8')
                except:
                    node.content = content
            parent_node.children[name] = node
        else:
            parent_node.children[name] = node
            for child in element:
                self._parse_node(child, node)

def get_prompt(vfs):
    """Формирует приглашение к вводу с учетом текущей директории VFS"""
    username = os.getenv('USER') or os.getenv('USERNAME')
    hostname = os.getenv('HOSTNAME') or subprocess.getoutput('hostname')
    
    # Формируем текущий путь в VFS
    path_parts = []
    current = vfs.current_dir
    while current and current != vfs.root:
        path_parts.insert(0, current.name)
        current = current.parent
    
    current_path = "/" + "/".join(path_parts) if path_parts else "/"
    
    return f"{username}@{hostname}:{current_path}$ "

def parse_command(input_line):
    """Парсит команду и раскрывает переменные окружения"""
    expanded_line = os.path.expandvars(input_line)
    return expanded_line.split()

def execute_script(script_path, vfs):
    """Выполняет стартовый скрипт"""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"Выполнение скрипта: {script_path}")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            print(get_prompt(vfs) + line)
            
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
    """Основной цикл REPL с поддержкой VFS"""
    parser = argparse.ArgumentParser(description='Эмулятор командной строки UNIX')
    parser.add_argument('--vfs', help='Путь к XML файлу VFS')
    parser.add_argument('--script', help='Путь к стартовому скрипту')
    
    args = parser.parse_args()
    
    # Инициализация VFS
    vfs = VFS()
    vfs_loaded = False
    
    if args.vfs:
        success, message = vfs.load_from_xml(args.vfs)
        print(f"Загрузка VFS: {message}")
        if success:
            vfs_loaded = True
        else:
            print(f"Ошибка: {message}")
    
    print("=== КОНФИГУРАЦИЯ ЭМУЛЯТОРА ===")
    print(f"VFS файл: {args.vfs or 'Не указан'}")
    print(f"VFS загружена: {'Да' if vfs_loaded else 'Нет'}")
    print(f"Скрипт: {args.script or 'Не указан'}")
    print("===============================")
    
    # Выполнение скрипта
    if args.script:
        success = execute_script(args.script, vfs)
        if success:
            return
    
    # Интерактивный режим
    print("Добро пожаловать в эмулятор командной строки!")
    print("Введите 'exit' для выхода.")
    
    while True:
        try:
            user_input = input(get_prompt(vfs)).strip()
            
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