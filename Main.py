import os
import sys
import subprocess
import argparse
import xml.etree.ElementTree as ET
import base64
import getpass
from datetime import datetime

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
    
    def resolve_path(self, path):
        """Разрешает путь в VFS"""
        if not path or path == ".":
            return self.current_dir
        
        if path == "..":
            if self.current_dir.parent:
                return self.current_dir.parent
            return self.current_dir
        
        if path.startswith("/"):
            current = self.root
            path_parts = [p for p in path.split("/") if p]
        else:
            current = self.current_dir
            path_parts = [p for p in path.split("/") if p]
        
        for part in path_parts:
            if part == "":
                continue
            if part == ".":
                continue
            if part == "..":
                if current.parent:
                    current = current.parent
                continue
            
            if part in current.children:
                current = current.children[part]
            else:
                return None
        
        return current
    
    def list_directory(self, path="."):
        """Список содержимого директории"""
        node = self.resolve_path(path)
        if not node:
            return None, "Директория не найдена"
        if node.is_file:
            return None, "Это файл, а не директория"
        
        items = []
        for name, child in node.children.items():
            item_type = "file" if child.is_file else "dir"
            items.append((name, item_type))
        
        items.sort(key=lambda x: (x[1] != "dir", x[0].lower()))
        return items, None
    
    def get_file_content(self, path):
        """Получает содержимое файла"""
        node = self.resolve_path(path)
        if not node:
            return None, "Файл не найден"
        if not node.is_file:
            return None, "Это директория, а не файл"
        
        return node.content, None
    
    def get_file_tail(self, path, lines=10):
        """Получает последние строки файла"""
        content, error = self.get_file_content(path)
        if error:
            return None, error
        
        if not content:
            return "", None
        
        file_lines = content.split('\n')
        start_index = max(0, len(file_lines) - lines)
        return '\n'.join(file_lines[start_index:]), None

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

def execute_command(command, args, vfs, vfs_loaded):
    """Выполняет одну команду"""
    if command == 'exit':
        print("Выход из эмулятора")
        return True, None
    
    elif command == 'ls':
        if not vfs_loaded:
            print("Ошибка: VFS не загружена")
            return False, "Ошибка выполнения" 
        
        path = args[0] if args else "."
        items, error = vfs.list_directory(path)
        if error:
            print(f"ls: {error}")
            return False, "Ошибка выполнения" 
        else:
            for name, item_type in items:
                print(f"{name} ({item_type})")
            return False, None 
    
    elif command == 'cd':
        if not vfs_loaded:
            print("Ошибка: VFS не загружена")
            return False, "Ошибка выполнения" 
        
        if args:
            path = args[0]
            node = vfs.resolve_path(path)
            if node and not node.is_file:
                vfs.current_dir = node
            else:
                print(f"cd: Директория не найдена: {path}")
                return False, "Ошибка выполнения"  
        else:
            vfs.current_dir = vfs.root
        return False, None  
    
    elif command == 'cat':
        if not vfs_loaded:
            print("Ошибка: VFS не загружена")
            return False, "Ошибка выполнения" 
        
        if not args:
            print("cat: Укажите путь к файлу")
            return False, "Ошибка выполнения"  
        
        success = True
        for file_path in args:
            content, error = vfs.get_file_content(file_path)
            if error:
                print(f"cat: {error}")
                success = False
            else:
                print(content or "(файл пуст)")
        
        return False, "Ошибка выполнения" if not success else None
    
    elif command == 'tail':
        if not vfs_loaded:
            print("Ошибка: VFS не загружена")
            return False, "Ошибка выполнения"
        
        if not args:
            print("tail: Укажите путь к файлу")
            return False, "Ошибка выполнения"  

        lines = 10
        file_path = args[-1] 
        
        # Обрабатываем опцию -n
        if len(args) > 1 and args[0] == '-n':
            if len(args) > 2:
                try:
                    lines = int(args[1])
                    file_path = args[2]
                except ValueError:
                    print("tail: неверное число строк")
                    return False, "Ошибка выполнения"
            else:
                print("tail: опция требует аргумента -n")
                return False, "Ошибка выполнения" 
        
        content, error = vfs.get_file_tail(file_path, lines)
        if error:
            print(f"tail: {error}")
            return False, "Ошибка выполнения" 
        else:
            print(content or "(файл пуст)")
            return False, None  
    
    elif command == 'who':
        # Команда who работает без VFS
        username = getpass.getuser()
        hostname = os.getenv('HOSTNAME') or subprocess.getoutput('hostname')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{username}@{hostname} {current_time}")
        return False, None  
    
    else:
        print(f"Ошибка: неизвестная команда '{command}'")
        return False, "Ошибка выполнения" 

def execute_script(script_path, vfs, vfs_loaded):
    """Выполняет стартовый скрипт (останавливается при первой ошибке)"""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"Выполнение скрипта: {script_path}")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            print(get_prompt(vfs) + line)
            
            cmd_args = parse_command(line)
            if not cmd_args:
                continue
                
            command = cmd_args[0]
            args = cmd_args[1:]
            
            exit_requested, error = execute_command(command, args, vfs, vfs_loaded)
            
            if exit_requested:
                return True 
            
            if error:  
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
    """Основной цикл REPL с поддержкой VFS и новых команд"""
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
        success = execute_script(args.script, vfs, vfs_loaded)
        if success:
            return
    
    # Интерактивный режим
    print("Добро пожаловать в эмулятор командной строки!")
    if vfs_loaded:
        print("VFS загружена. Доступные команды: ls, cd, cat, tail, who, exit")
    else:
        print("VFS не загружена. Доступные команды: who, exit")
    
    while True:
        try:
            user_input = input(get_prompt(vfs)).strip()
            
            if not user_input:
                continue
                
            cmd_args = parse_command(user_input)
            command = cmd_args[0]
            args = cmd_args[1:]
            
            exit_requested, error = execute_command(command, args, vfs, vfs_loaded)
            
            if exit_requested:
                break
                
        except KeyboardInterrupt:
            print("\nДля выхода введите 'exit'")
        except Exception as e:
            print(f"Ошибка выполнения: {e}")

if __name__ == "__main__":
    main()