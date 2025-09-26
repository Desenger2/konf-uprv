@echo off
chcp 65001 > nul

echo === Тест 6: Загрузка VFS с ошибкой ===
echo exit | python Main.py --vfs vfs3.xml

echo.
echo === Тестирование завершено ===
pause