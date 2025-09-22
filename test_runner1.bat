@echo off
chcp 65001 > nul
echo === Тест 1: Запуск с VFS и скриптом 1 ===
python Main.py --vfs C:\Users\%USERNAME%\my_vfs --script test_script1.sh

echo.
echo === Тестирование завершено ===
pause