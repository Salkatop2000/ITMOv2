# Implementation Plan: Task Search (v1)

Branch: 001-task-search-by-title | Date: 2026-10-29 | Spec: specs/001-task-search-by-title/spec.md

Input: Feature specification from specs/001-task-search-by-title/spec.md and Common Contract specs/001-task-search-by-name/COMMON_CONTRACT.md

## Summary

Добавить поддержку поиска задач по подстроке названия (регистронезависимый) без изменения текущего поведения листинга и существующих команд. UI вызывает новый контракт поиска только для непустых запросов; пустой query очищает поиск и восстанавливает список. Максимальная длина — 256; превышение валидируется.

## Technical Context

- Language/Version: Python 3 (CLI и Tkinter GUI)
- Primary Dependencies: стандартная библиотека (argparse, json, tkinter, subprocess)
- Storage: JSON-файл data/tasks.json с элементами {id, title, status}
- Testing: pytest; существующие тесты покрывают add/list/done/reopen/clear
- Target Platform: Linux (CLI), Tkinter desktop GUI
- Project Type: CLI с минимальным GUI-обёрткой
- Constraints: не менять формат хранилища; не ломать существующие команды/вывод
- Scale/Scope: учебный проект; список задач до тысяч элементов

## Constitution Check

Constitution в проекте представлен шаблоном без явных ворот; нарушений не выявлено. Следуем принципам простоты и совместимости.

## Project Structure

### Documentation (this feature)

```text
specs/001-task-search-by-title/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/
    └── cli-search.md    # CLI contract for search
```

### Source Code (repository root)

```text
src/
├── task_cli.py          # добавить search команду (без изменения существующих)
└── task_gui.py          # интеграция поля поиска с debounce и очисткой

tests/
├── contract/
│   └── test_search_cli.py      # контрактные тесты CLI поиска
└── integration/
    └── test_gui_search.py      # интеграционные сценарии GUI (опционально)
```

Structure Decision: Single-project CLI + GUI. Добавляется команда search в CLI и минимальные изменения GUI для ввода/очистки/ретрая.

## Architecture

- Где будет находиться search logic: в src/task_cli.py как новая команда search, использующая существующие функции загрузки/фильтрации. Сопоставление: trim, case-insensitive substring; валидация длины 1..256.
- Где будет UI integration: в src/task_gui.py добавить поле поиска, debounce, вызов CLI search при непустом query, обработку empty/loading/error, кнопку «Очистить» и Esc для сброса к list.
- Как UI будет вызывать search: через subprocess, аналогично существующим вызовам, команда вида: python3 src/task_cli.py --data <file> search --query <q> [--status <filter>]. Пустой query не вызывает search.
- Как будет работать debounce: через Tkinter after таймер (например, 250–300 мс) с сбросом предыдущего таймера при новом вводе.
- Как будет выполняться фильтрация: на стороне CLI по подстроке названия с учётом активных фильтров списка (минимально — status, который уже поддерживается UI/CLI).
- Как сохраняется существующая сортировка: CLI search использует тот же порядок, что list (на текущий момент id asc в CLI). Для GUI сортировка берётся из списка — search не меняет порядок.
- Как сохраняются существующие фильтры: UI передаёт текущие фильтры (минимально — status) в вызов search; поиск накладывается поверх и не сбрасывает их.
- Как обрабатываются empty/loading/error states: GUI показывает спиннер/скелетон при поиске; пустой результат — «Нет задач по запросу …» + «Очистить поиск»; ошибки — компактный блок «Не удалось выполнить поиск» + «Повторить», ретрай повторяет последний запрос.
- Как выполняется clear/Esc: очистка поля/нажатие Esc вызывает list и восстанавливает исходный список; фильтры и сортировка сохраняются; search с пустым query не вызывается.

## Data/API contract

- query: строка после trim длиной 1..256; пустой query не вызывает search.
- trim: обязательный; пустые/пробельные значения не отправляются.
- case-insensitive contains: единственный режим сопоставления в v1.
- max 256: >256 — валидационная ошибка (CLI возвращает ненулевой код и сообщение на stderr; GUI показывает как валидационную ошибку).
- активные фильтры: search применяется поверх активных фильтров (в текущем UI — status); дополнительные фильтры отсутствуют.
- существующая сортировка: search не изменяет текущую сортировку (в CLI — id asc; в GUI — сохраняется порядок списка).
- result id/title/status: вывод совместим с list для переиспользования существующего рендера GUI.
- validation error для query > 256: отдельный путь обработки.
- отсутствие search API call для empty query: UI предотвращает вызов.

## Backward compatibility

- Нельзя менять: команды add, list, done, reopen, clear; формат вывода list; формат хранилища data/tasks.json.
- Сценарии, которые должны продолжить работать: добавление задач; листинг; изменение статусов; очистка; все существующие GUI операции без поля поиска.
- Storage format: не меняется; новые поля не добавляются.

## Testing strategy

1. Happy path: запрос "login" возвращает подходящие задачи.
2. Case-insensitive: "LOGIN" == "login".
3. Substring search: подстрока в середине названия находит задачу.
4. Trimming: "  login  " эквивалентно "login".
5. Query > 256: CLI выдаёт валидационную ошибку; GUI показывает валидационное сообщение и не вызывает поиск.
6. No results: пустой результат отображается корректно.
7. Error/retry: симулировать ошибку CLI (например, недоступный файл) — показать сообщение и повтор по кнопке.
8. Clear/Esc: очистка и Esc восстанавливают список без вызова search; фильтры/сортировка сохраняются.
9. Сохранение фильтров: активный статус-фильтр учитывается в search.
10. Сохранение сортировки: порядок результатов не меняется относительно текущего списка.
11. Существующее поведение Task Tracker: все текущие тесты проходят без изменений.

## Implementation boundaries

- Что меняется: src/task_cli.py (добавить команду search); src/task_gui.py (добавить поле поиска, debounce, clear, error/retry); добавить новые тесты.
- Что НЕ меняется: существующие команды и их поведение; формат хранения; вывод list; отсутствие новых продуктовых требований.
- Вероятно потребуют изменения: tests/test_task_cli.py (опционально — лучше создать отдельный файл для поиска); GUI тесты опциональны.
- Новые файлы: tests/contract/test_search_cli.py; при необходимости tests/integration/test_gui_search.py; specs/001-task-search-by-title/contracts/cli-search.md; specs/001-task-search-by-title/data-model.md; specs/001-task-search-by-title/quickstart.md; specs/001-task-search-by-title/research.md.

## Risk / compatibility

- Риск: изменение CLI может повлиять на существующий вывод — снижается тем, что добавляется новая команда search, list не меняется.
- Риск: несогласованность сортировки между list и search — проверяется тестами; search должен использовать тот же порядок, что list.
- Риск: производительность при больших списках — приемлемо для учебного объёма; при необходимости оптимизация (предвычисление lowercased).
- Проверки: прогон существующих тестов; контрактные тесты на search; ручная проверка GUI сценариев из quickstart.

## Complexity Tracking

Нет дополнительных усложнений по архитектуре; добавляется одна CLI-команда и минимальная GUI-интеграция.
