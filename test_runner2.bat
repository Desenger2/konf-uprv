@echo off
chcp 65001 > nul

echo === Тест 2: Запуск только со скриптом 2 ===
python Main.py --script test_script2.sh

echo.
echo === Тестирование завершено ===
pause