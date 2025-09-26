@echo off
chcp 65001 > nul

echo === Тест 5: Загрузка VFS ===
echo exit | python Main.py --vfs vfs1.xml

echo.
echo === Тестирование завершено ===
pause