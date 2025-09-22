@echo off
chcp 65001 > nul

echo === Тест 3: Запуск только с VFS ===
echo exit | python Main.py --vfs C:\Temp\custom_vfs

echo.
echo === Тестирование завершено ===
pause