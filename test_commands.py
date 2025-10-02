import pytest
import os
import tempfile
import sys
from io import StringIO
from unittest.mock import patch, MagicMock

# Добавляем путь к модулю для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Main import VFS, VFSNode, format_ls_output, parse_command, get_prompt, execute_command

class TestVFSCommands:
    """Тесты для команд VFS"""
    
    def setup_method(self):
        self.vfs = VFS()
        self.vfs.load_from_xml("vfs2.xml")
    
    def test_format_ls_output(self):
        """Тест форматирования вывода ls"""
        # Тест с пустым списком
        assert format_ls_output([]) == ""
        
        # Тест с одним элементом
        items = [("file.txt", "file")]
        output = format_ls_output(items)
        assert "file.txt" in output
        
        # Тест с директорией
        items = [("docs", "dir")]
        output = format_ls_output(items)
        assert "docs/" in output
        
        # Тест с несколькими элементами
        items = [
            ("dir1", "dir"),
            ("file1.txt", "file"),
            ("dir2", "dir"),
            ("file2.txt", "file")
        ]
        output = format_ls_output(items)
        assert "dir1/" in output
        assert "file1.txt" in output
        assert "dir2/" in output
        assert "file2.txt" in output
    
    def test_parse_command(self):
        """Тест парсинга команд"""
        # Базовая команда
        result = parse_command("ls -l")
        assert result == ["ls", "-l"]
        
        # Команда с переменными окружения
        os.environ["TEST_VAR"] = "test_value"
        result = parse_command("echo $TEST_VAR")
        assert result == ["echo", "test_value"]
        
        # Пустая строка
        result = parse_command("")
        assert result == []
        
        # Команда с пробелами
        result = parse_command("  ls   -l   /path  ")
        assert result == ["ls", "-l", "/path"]
    
    def test_get_prompt(self):
        """Тест формирования приглашения командной строки"""
        prompt = get_prompt(self.vfs)
        assert "$" in prompt
        assert ":" in prompt
        
        # Проверяем, что путь отображается корректно
        assert "/" in prompt
        
        # После смены директории
        self.vfs.current_dir = self.vfs.resolve_path("/home/user")
        prompt = get_prompt(self.vfs)
        assert "user" in prompt or "/home/user" in prompt

class TestCommandExecution:
    """Тесты выполнения команд"""
    
    def setup_method(self):
        self.vfs = VFS()
        self.vfs_loaded = False
    
    def test_command_exit(self):
        """Тест команды exit"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("exit", [], self.vfs, self.vfs_loaded)
            assert exit_requested == True
            mock_print.assert_called_with("Выход из эмулятора")
    
    def test_command_who(self):
        """Тест команды who"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("who", [], self.vfs, self.vfs_loaded)
            assert exit_requested == False
            assert error is None
            mock_print.assert_called_once()
    
    def test_command_ls_without_vfs(self):
        """Тест команды ls без загруженной VFS"""
        exit_requested, error = execute_command("ls", [], self.vfs, False)
        assert exit_requested == False
        assert error == "Ошибка выполнения"
    
    def test_command_cd_without_vfs(self):
        """Тест команды cd без загруженной VFS"""
        exit_requested, error = execute_command("cd", ["/home"], self.vfs, False)
        assert exit_requested == False
        assert error == "Ошибка выполнения"
    
    def test_command_cat_without_vfs(self):
        """Тест команды cat без загруженной VFS"""
        exit_requested, error = execute_command("cat", ["file.txt"], self.vfs, False)
        assert exit_requested == False
        assert error == "Ошибка выполнения"

class TestVFSCommandExecution:
    """Тесты выполнения команд с загруженной VFS"""
    
    def setup_method(self):
        self.vfs = VFS()
        self.vfs.load_from_xml("vfs2.xml")
        self.vfs_loaded = True
    
    def test_command_ls_root(self):
        """Тест команды ls для корневой директории"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("ls", ["/"], self.vfs, self.vfs_loaded)
            assert exit_requested == False
            assert error is None
            # Проверяем, что вывод содержит ожидаемые директории
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "home" in call_args or "root" in call_args
    
    def test_command_ls_current_dir(self):
        """Тест команды ls для текущей директории"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("ls", [], self.vfs, self.vfs_loaded)
            assert exit_requested == False
            assert error is None
            mock_print.assert_called_once()
    
    def test_command_cd_success(self):
        """Тест успешной команды cd"""
        # Переходим в home
        exit_requested, error = execute_command("cd", ["/home"], self.vfs, self.vfs_loaded)
        assert exit_requested == False
        assert error is None
        assert self.vfs.current_dir.name == "home"
        
        # Возвращаемся в корень
        exit_requested, error = execute_command("cd", ["/"], self.vfs, self.vfs_loaded)
        assert exit_requested == False
        assert error is None
        assert self.vfs.current_dir == self.vfs.root
    
    def test_command_cd_nonexistent(self):
        """Тест команды cd с несуществующей директорией"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("cd", ["/nonexistent"], self.vfs, self.vfs_loaded)
            assert exit_requested == False
            assert error == "Ошибка выполнения"
            mock_print.assert_called_with("cd: Директория не найдена: /nonexistent")
    
    def test_command_cat_success(self):
        """Тест успешной команды cat"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("cat", ["/home/user/document.txt"], self.vfs, self.vfs_loaded)
            assert exit_requested == False
            assert error is None
            mock_print.assert_called_once()
    
    def test_command_cat_nonexistent(self):
        """Тест команды cat с несуществующим файлом"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("cat", ["/nonexistent.txt"], self.vfs, self.vfs_loaded)
            assert exit_requested == False
            assert error == "Ошибка выполнения"
            mock_print.assert_called_with("cat: Файл не найден")
    
    def test_command_tail_success(self):
        """Тест успешной команды tail"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("tail", ["/root/file1.txt"], self.vfs, self.vfs_loaded)
            assert exit_requested == False
            assert error is None
            mock_print.assert_called_once()
    
    def test_command_tail_with_lines(self):
        """Тест команды tail с указанием количества строк"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("tail", ["-n", "5", "/root/file1.txt"], self.vfs, self.vfs_loaded)
            assert exit_requested == False
            assert error is None
            mock_print.assert_called_once()
    
    def test_command_touch_success(self):
        """Тест успешной команды touch"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("touch", ["/home/user/newfile.txt"], self.vfs, self.vfs_loaded)
            assert exit_requested == False
            assert error is None
            mock_print.assert_called_with("touch: создан файл '/home/user/newfile.txt'")
            
            # Проверяем, что файл действительно создан
            file_node = self.vfs.resolve_path("/home/user/newfile.txt")
            assert file_node is not None
            assert file_node.is_file == True
    
    def test_command_cp_success(self):
        """Тест успешной команды cp"""
        # Сначала создаем исходный файл
        self.vfs.create_file("/home/user/source.txt", "test content")
        
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("cp", 
                ["/home/user/source.txt", "/home/user/destination.txt"], 
                self.vfs, self.vfs_loaded)
            
            assert exit_requested == False
            assert error is None
            mock_print.assert_called_with("cp: файл скопирован из '/home/user/source.txt' в '/home/user/destination.txt'")
            
            # Проверяем, что копия создана
            original = self.vfs.resolve_path("/home/user/source.txt")
            copy = self.vfs.resolve_path("/home/user/destination.txt")
            assert original.content == copy.content
    
    def test_command_cp_insufficient_args(self):
        """Тест команды cp с недостаточным количеством аргументов"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("cp", ["/source.txt"], self.vfs, self.vfs_loaded)
            assert exit_requested == False
            assert error == "Ошибка выполнения"
            mock_print.assert_called_with("cp: Использование: cp <источник> <назначение>")


class TestUnknownCommand:
    """Тесты неизвестных команд"""
    
    def setup_method(self):
        self.vfs = VFS()
        self.vfs_loaded = True
    
    def test_unknown_command(self):
        """Тест неизвестной команды"""
        with patch('builtins.print') as mock_print:
            exit_requested, error = execute_command("unknown_cmd", [], self.vfs, self.vfs_loaded)
            assert exit_requested == False
            assert error == "Ошибка выполнения"
            mock_print.assert_called_with("Ошибка: неизвестная команда 'unknown_cmd'")

class TestVFSComplexScenarios:
    """Тесты сложных сценариев работы с VFS"""
    
    def setup_method(self):
        self.vfs = VFS()
        self.vfs.load_from_xml("vfs2.xml")
    
    def test_navigation_and_listing(self):
        """Тест навигации и листинга"""
        # Начинаем с корня
        items, error = self.vfs.list_directory("/")
        assert error is None
        root_items = [name for name, _ in items]
        assert "home" in root_items
        
        # Переходим в home
        self.vfs.current_dir = self.vfs.resolve_path("/home")
        items, error = self.vfs.list_directory(".")
        assert error is None
        home_items = [name for name, _ in items]
        assert "user" in home_items
        
        # Переходим в user
        self.vfs.current_dir = self.vfs.resolve_path("user")
        items, error = self.vfs.list_directory(".")
        assert error is None
        user_items = [name for name, _ in items]
        assert "projects" in user_items
        assert "document.txt" in user_items
    
    def test_file_operations_chain(self):
        """Тест цепочки операций с файлами"""
        # Создаем файл
        success, message = self.vfs.create_file("/home/user/test_chain.txt", "initial content")
        assert success == True
        
        # Проверяем создание
        content, error = self.vfs.get_file_content("/home/user/test_chain.txt")
        assert error is None
        assert content == "initial content"
        
        # Копируем файл
        success, message = self.vfs.copy_file(
            "/home/user/test_chain.txt", 
            "/home/user/test_chain_copy.txt"
        )
        assert success == True
        
        # Проверяем копию
        copy_content, error = self.vfs.get_file_content("/home/user/test_chain_copy.txt")
        assert error is None
        assert copy_content == "initial content"
        
        # Проверяем tail
        tail_content, error = self.vfs.get_file_tail("/home/user/test_chain.txt", 2)
        assert error is None
        assert "initial content" in tail_content
    
    def test_path_resolution_edge_cases(self):
        """Тест граничных случаев разрешения путей"""
        # Множественные слэши
        node = self.vfs.resolve_path("//home//user///")
        assert node is not None
        assert node.name == "user"
        
        # Точки в пути
        node = self.vfs.resolve_path("/home/./user/../user/./projects")
        assert node is not None
        assert node.name == "projects"
        
        # Пустая строка
        node = self.vfs.resolve_path("")
        assert node == self.vfs.current_dir
        
        # Только точки
        node = self.vfs.resolve_path("..")
        assert node == self.vfs.root.parent or node == self.vfs.root
    
    def test_ls_formatting_edge_cases(self):
        """Тест граничных случаев форматирования ls"""
        # Очень длинные имена
        long_items = [
            ("very_long_directory_name_that_exceeds_typical_width", "dir"),
            ("another_very_long_file_name_with_extension.txt", "file"),
            ("short", "file")
        ]
        output = format_ls_output(long_items)
        assert output != "" 
        
        # Один очень длинный элемент
        single_long_item = [("extremely_long_name_that_should_handle_properly", "dir")]
        output = format_ls_output(single_long_item)
        assert "extremely_long_name_that_should_handle_properly/" in output