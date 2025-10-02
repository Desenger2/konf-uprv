import pytest
import os
import tempfile
import xml.etree.ElementTree as ET
from Main import VFS, VFSNode

class TestVFS:
    """Тесты для виртуальной файловой системы"""
    
    def setup_method(self):
        """Инициализация перед каждым тестом"""
        self.vfs = VFS()
    
    def test_vfs_initialization(self):
        """Тест инициализации VFS"""
        assert self.vfs.root is not None
        assert self.vfs.root.name == ""
        assert self.vfs.root.is_file == False
        assert self.vfs.current_dir == self.vfs.root
    
    def test_load_from_xml_success(self):
        """Тест успешной загрузки VFS из vfs2.xml"""
        success, message = self.vfs.load_from_xml("vfs2.xml")
        assert success == True
        assert "успешно" in message.lower()
        
        # Проверяем структуру VFS согласно vfs2.xml
        root_dir = self.vfs.resolve_path("/")
        assert root_dir is not None
        
        # Проверяем корневые директории
        items, error = self.vfs.list_directory("/")
        assert error is None
        dir_names = [name for name, item_type in items]
        assert "root" in dir_names
        assert "home" in dir_names
    
    def test_load_from_xml_structure(self):
        """Тест структуры загруженной VFS"""
        success, message = self.vfs.load_from_xml("vfs2.xml")
        assert success == True
        
        # Проверяем путь /root/file1.txt
        file1 = self.vfs.resolve_path("/root/file1.txt")
        assert file1 is not None
        assert file1.name == "file1.txt"
        assert file1.is_file == True
        assert "Строка 1" in file1.content
        assert "Строка 11" in file1.content
        
        # Проверяем путь /home/user/document.txt
        document = self.vfs.resolve_path("/home/user/document.txt")
        assert document is not None
        assert document.name == "document.txt"
        assert document.is_file == True
        assert "содержимое документа" in document.content
        
        # Проверяем путь /home/user/projects/project1.py
        project1 = self.vfs.resolve_path("/home/user/projects/project1.py")
        assert project1 is not None
        assert project1.name == "project1.py"
        assert project1.is_file == True
        assert "print(" in project1.content
        
        # Проверяем путь /home/user/projects/readme.md
        readme = self.vfs.resolve_path("/home/user/projects/readme.md")
        assert readme is not None
        assert readme.name == "readme.md"
        assert readme.is_file == True
        assert "# Проект 1" in readme.content
        assert "## Описание" in readme.content
    
    def test_load_from_xml_file_not_found(self):
        """Тест загрузки несуществующего XML файла"""
        success, message = self.vfs.load_from_xml("nonexistent.xml")
        assert success == False
        assert "не найден" in message.lower()
    
    def test_load_from_xml_invalid_format(self):
        """Тест загрузки XML с неверным форматом"""
        xml_content = '''<invalid_root>
            <dir name="test"></dir>
        </invalid_root>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            xml_path = f.name
        
        try:
            success, message = self.vfs.load_from_xml(xml_path)
            assert success == False
            assert "формат" in message.lower() or "vfs" in message.lower()
        finally:
            os.unlink(xml_path)
    
    def test_resolve_path_absolute(self):
        """Тест разрешения абсолютных путей в vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        root_dir = self.vfs.resolve_path("/")
        assert root_dir == self.vfs.root
        
        home_dir = self.vfs.resolve_path("/home")
        assert home_dir is not None
        assert home_dir.name == "home"
        
        user_dir = self.vfs.resolve_path("/home/user")
        assert user_dir is not None
        assert user_dir.name == "user"
        
        projects_dir = self.vfs.resolve_path("/home/user/projects")
        assert projects_dir is not None
        assert projects_dir.name == "projects"
    
    def test_resolve_path_relative(self):
        """Тест разрешения относительных путей в vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        # Переходим в домашнюю директорию
        self.vfs.current_dir = self.vfs.resolve_path("/home")
        
        user_dir = self.vfs.resolve_path("user")
        assert user_dir is not None
        assert user_dir.name == "user"
        
        # Переходим в пользовательскую директорию
        self.vfs.current_dir = user_dir
        
        projects_dir = self.vfs.resolve_path("projects")
        assert projects_dir is not None
        assert projects_dir.name == "projects"
        
        current_dir = self.vfs.resolve_path(".")
        assert current_dir == self.vfs.current_dir
        
        parent_dir = self.vfs.resolve_path("..")
        assert parent_dir.name == "home"
    
    def test_resolve_path_nonexistent(self):
        """Тест разрешения несуществующих путей в vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        result = self.vfs.resolve_path("/nonexistent")
        assert result is None
        
        result = self.vfs.resolve_path("/home/nonexistent")
        assert result is None
        
        result = self.vfs.resolve_path("/home/user/nonexistent")
        assert result is None
    
    def test_list_directory_root(self):
        """Тест списка корневой директории vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        items, error = self.vfs.list_directory("/")
        assert error is None
        assert len(items) == 2
        
        dir_names = [name for name, item_type in items]
        assert "root" in dir_names
        assert "home" in dir_names
        assert all(item_type == "dir" for name, item_type in items) 
    
    def test_list_directory_home(self):
        """Тест списка директории /home в vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        items, error = self.vfs.list_directory("/home")
        assert error is None
        assert len(items) == 1
        
        dir_name, dir_type = items[0]
        assert dir_name == "user"
        assert dir_type == "dir"
    
    def test_list_directory_user(self):
        """Тест списка директории /home/user в vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        items, error = self.vfs.list_directory("/home/user")
        assert error is None
        assert len(items) == 2
        
        # Проверяем сортировку
        names = [name for name, item_type in items]
        types = [item_type for name, item_type in items]
        
        assert "projects" in names
        assert "document.txt" in names
        assert types[0] == "dir"
        assert types[1] == "file"
    
    def test_list_directory_projects(self):
        """Тест списка директории /home/user/projects в vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        items, error = self.vfs.list_directory("/home/user/projects")
        assert error is None
        assert len(items) == 2
        
        names = [name for name, item_type in items]
        assert "project1.py" in names
        assert "readme.md" in names
        assert all(item_type == "file" for name, item_type in items)
    
    def test_list_directory_errors(self):
        """Тест ошибок при получении списка директории"""
        self.vfs.load_from_xml("vfs2.xml")
        
        # Несуществующая директория
        items, error = self.vfs.list_directory("/nonexistent")
        assert items is None
        assert "не найдена" in error.lower()
        
        # Путь к файлу вместо директории
        items, error = self.vfs.list_directory("/home/user/document.txt")
        assert items is None
        assert "файл" in error.lower()
    
    def test_get_file_content_success(self):
        """Тест успешного получения содержимого файлов из vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        # Тестируем file1.txt
        content, error = self.vfs.get_file_content("/root/file1.txt")
        assert error is None
        assert content is not None
        assert "Строка 1" in content
        assert "Строка 11" in content
        assert content.count('\n') >= 10
        
        # Тестируем document.txt
        content, error = self.vfs.get_file_content("/home/user/document.txt")
        assert error is None
        assert "содержимое документа" in content
        
        # Тестируем project1.py
        content, error = self.vfs.get_file_content("/home/user/projects/project1.py")
        assert error is None
        assert "print(" in content
        assert "Hello World" in content
        
        # Тестируем readme.md
        content, error = self.vfs.get_file_content("/home/user/projects/readme.md")
        assert error is None
        assert "# Проект 1" in content
        assert "## Описание" in content
    
    def test_get_file_content_errors(self):
        """Тест ошибок при получении содержимого файлов"""
        self.vfs.load_from_xml("vfs2.xml")
        
        # Несуществующий файл
        content, error = self.vfs.get_file_content("/nonexistent.txt")
        assert content is None
        assert "не найден" in error.lower()
        
        # Путь к директории вместо файла
        content, error = self.vfs.get_file_content("/home")
        assert content is None
        assert "директория" in error.lower()
    
    def test_get_file_tail(self):
        """Тест получения конца файла"""
        self.vfs.load_from_xml("vfs2.xml")
        
        # Тест file1.txt с последними 5 строками
        content, error = self.vfs.get_file_tail("/root/file1.txt", 5)
        assert error is None
        assert content is not None
        lines = content.split('\n')
        assert len(lines) <= 5
        assert any("Строка 7" in line or "Строка 8" in line or 
                  "Строка 9" in line or "Строка 10" in line or 
                  "Строка 11" in line for line in lines)
    
    def test_create_file_success(self):
        """Тест успешного создания файла в vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        success, message = self.vfs.create_file("/home/user/new_file.txt", "новое содержимое")
        assert success == True
        assert "создан" in message.lower()
        
        # Проверяем, что файл действительно создан
        file_node = self.vfs.resolve_path("/home/user/new_file.txt")
        assert file_node is not None
        assert file_node.is_file == True
        assert file_node.content == "новое содержимое"
        
        # Проверяем, что файл появился в списке
        items, error = self.vfs.list_directory("/home/user")
        assert error is None
        names = [name for name, item_type in items]
        assert "new_file.txt" in names
    
    def test_create_file_errors(self):
        """Тест ошибок при создании файла в vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        # Несуществующая родительская директория
        success, message = self.vfs.create_file("/nonexistent/file.txt")
        assert success == False
        assert "не найдена" in message.lower()
        
        # Файл уже существует
        self.vfs.create_file("/home/user/existing.txt")
        success, message = self.vfs.create_file("/home/user/existing.txt")
        assert success == False
        assert "существует" in message.lower()
    
    def test_copy_file_success(self):
        """Тест успешного копирования файла в vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        success, message = self.vfs.copy_file(
            "/home/user/document.txt", 
            "/home/user/document_copy.txt"
        )
        assert success == True
        assert "скопирован" in message.lower()
        
        # Проверяем исходный и скопированный файлы
        original = self.vfs.resolve_path("/home/user/document.txt")
        copy = self.vfs.resolve_path("/home/user/document_copy.txt")
        
        assert original is not None
        assert copy is not None
        assert original.content == copy.content
        assert original.name != copy.name
        
        # Проверяем, что копия появилась в списке
        items, error = self.vfs.list_directory("/home/user")
        assert error is None
        names = [name for name, item_type in items]
        assert "document_copy.txt" in names
    
    def test_copy_file_errors(self):
        """Тест ошибок при копировании файла в vfs2.xml"""
        self.vfs.load_from_xml("vfs2.xml")
        
        # Несуществующий исходный файл
        success, message = self.vfs.copy_file("/nonexistent.txt", "/copy.txt")
        assert success == False
        assert "не найден" in message.lower()
        
        # Копирование директории
        success, message = self.vfs.copy_file("/home", "/home_copy")
        assert success == False
        assert "директории" in message.lower()
        
        # Несуществующая директория назначения
        success, message = self.vfs.copy_file(
            "/home/user/document.txt", 
            "/nonexistent/copy.txt"
        )
        assert success == False
        assert "назначения" in message.lower()