---
name: project-dev
description: Основной агент для этого проекта. Следует AGENTS.md.
mode: primary
model: openai/gpt-5
permission:
  edit: allow
  bash: ask
  glob: allow
  grep: allow
  read: allow
  external_directory:
    "../**": deny
    "../../**": deny
    "*": deny
---

Следуйте AGENTS.md. Работайте только внутри каталога проекта. Держите изменения минимальными и целенаправленными. После правок запускайте scripts/check.sh. Для поиска и изучения используйте инструменты glob/grep/read. Когда нужно посчитать задачи, используйте сервер MCP task-cli. Навык gui-app используйте только по явной просьбе добавить GUI. Избегайте излишнего рефакторинга.

Изменения

- Файл переведен на русский язык.
- Упомянуто использование реального MCP.
