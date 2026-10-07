---
name: gui-app
description: Используйте ТОЛЬКО при явной просьбе добавить GUI для CLI-приложения задач (ключевые слова: Tkinter, PySimpleGUI, Qt). Минимально оберните src/task_cli.py.
---

# Навык GUI App

Цель: добавить минимальный интерфейс Tkinter вокруг src/task_cli.py.

Когда использовать: только по явной просьбе (или при упоминании Tkinter/PySimpleGUI/Qt).

Ограничения реализации:

- Один файл под src/, например src/task_gui.py (только ASCII).
- Только Tkinter, без внешних зависимостей.
- Вызывать существующий модуль CLI (импорт функций или запуск с аргументами) для операций:
  list, add <title>, done <id>, clear [--status open|done|all].
- Файл данных по умолчанию: data/tasks.json. Разрешить выбор пути через Entry.
- Валидация: непустой title; id — положительное число; status ∈ {open, done, all}.
- Логику держать маленькой; переиспользовать поведение src/task_cli.py. Рефакторинг task_cli.py — только при необходимости.

Эскиз UI (компактно):

- Верх: путь к файлу [Entry], кнопки: Refresh, Save Path.
- Центр: Listbox задач со статусом; выпадающий фильтр (open/done/all).
- Низ: Add [Entry] + Add; Done [Entry id] + Done; Clear by status.

Примеры (псевдокод):

```python
# listing
out = subprocess.run(["python3", "src/task_cli.py", "--data", path, "list", "--status", status], capture_output=True, text=True)
tasks_text = out.stdout

# add
subprocess.check_call(["python3", "src/task_cli.py", "--data", path, "add", title])

# done
subprocess.check_call(["python3", "src/task_cli.py", "--data", path, "done", str(task_id)])
```

Проверка:

1. Запустить scripts/check.sh для регрессионной проверки.
2. Ручной запуск GUI (нужно не-headless окружение):
   python3 src/task_gui.py
3. Добавить задачу, отметить done, обновить список, очистить done — без сбоев.

Держите файл GUI ~до 150 строк; не трогайте тесты.

Перевод выполнен на русский.
