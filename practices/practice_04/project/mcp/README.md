# MCP-сервер Task CLI

Реальный MCP-сервер на официальной Python-библиотеке `mcp`, предоставляющий один инструмент: `task_count`.

Назначение

- Безопасный подсчет задач из JSON-файла по статусу, доступный любой MCP-хост-среде через стандартный протокол.

Установка

- Требуется Python 3.10+.
- Установите SDK: `pip install mcp` или изолированно через `pipx install mcp`.

Запуск

- Opencode запускает сервер как локный MCP `stdio`-процесс, согласно `opencode.json`:
  - `mcp.task-cli.type: "local"`
  - `mcp.task-cli.command: ["python3", "mcp/task_cli_mcp.py"]`
- Транспорт: JSON-RPC 2.0 по stdio. Вывод stdout используется как канал протокола, лог пишите в stderr (управляется SDK).

Инструменты

- `task_count(status?: "open"|"done"|"all" = "all", path?: string = "data/tasks.json")`
  - Возвращает JSON: `{ count, status }` при успехе.
  - Ошибки:
    - Неверный статус -> протокольная ошибка (`INVALID_PARAMS`).
    - Отсутствующий/некорректный файл -> протокольная ошибка с сообщением.

Примеры

Успех:

```
Content-Length: 118

{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"task_count","arguments":{"status":"done"}}}

Content-Length: 67

{"jsonrpc":"2.0","id":1,"result":{"count":2,"status":"done"}}
```

Ошибка (невалидный статус):

```
Content-Length: 120

{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"task_count","arguments":{"status":"foo"}}}

Content-Length: 91

{"jsonrpc":"2.0","id":2,"error":{"code":-32602,"message":"Invalid status: foo"}}
```

Изменения

- Документ переведен на русский язык и обновлен под реальный MCP на Python (`mcp`).
