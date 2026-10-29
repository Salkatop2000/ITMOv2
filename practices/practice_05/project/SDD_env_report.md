# Подготовка окружения для SDD: OpenSpec и GitHub Spec Kit

Этот отчёт фиксирует проверку окружения, установку CLI-инструментов и их проверку, без изменения проекта и без выполнения `init`.

## Шаг 1. Проверка окружения

- ОС: Linux (Ubuntu) x86_64, kernel 6.8.0-138-generic
- shell: /bin/bash
- Node.js: v22.23.3
- npm: 10.9.9
- Git: git version 2.43.0
- npx: доступен (/usr/bin/npx), версия 10.9.9
- Менеджеры пакетов для Node:
  - corepack: установлен, 0.36.0
  - yarn: не установлен
  - pnpm: не установлен
- Python:
  - python3: 3.12.3
  - python: команда отсутствует
- uv: отсутствовал до установки Spec Kit; установлен в Шаге 3 (см. ниже)
- До установки:
  - openspec: не установлен
  - specify (Spec Kit CLI): не установлен

## Шаг 2. Установка OpenSpec

- Официальные источники:
  - Сайт: https://openspec.dev (Docs → Installation)
  - Репозиторий: https://github.com/Fission-AI/OpenSpec
  - npm пакет: @fission-ai/openspec
- Совместимость: требуется Node >= 20.19.0; установлена Node v22.23.3 (совместимо)
- Установка (в соответствии с учебной версией): `npm install -g @fission-ai/openspec@1.14.1`
- Результат:
  - CLI путь: `/home/salkaatop2000/.npm-global/bin/openspec`
  - Установленная версия: `1.14.1`
  - Проверки:
    - `openspec --version` → PASS (1.14.1)
    - `openspec --help` → PASS
    - `openspec list --help` → PASS
  - Предупреждения: npm сообщил о пакетах "looking for funding" — не влияет на работу CLI

## Шаг 3. Установка GitHub Spec Kit (Spec Kit)

- Официальные источники:
  - Документация: https://github.github.io/spec-kit/ (Installation Guide)
  - Репозиторий: https://github.com/github/spec-kit
  - Имя CLI: `specify` (пакет `specify-cli` на PyPI)
- Требования: Python 3.11+ (имеется 3.12.3), uv (рекомендовано)
- Установка по инструкции:
  1. Установка uv (официальный скрипт): `curl -LsSf https://astral.sh/uv/install.sh | sh`
  2. Установка CLI: `uv tool install specify-cli`
- Результат:
  - CLI путь: `/home/salkaatop2000/.local/bin/specify`
  - Установленная версия CLI: `1.2.3`
  - Проверки:
    - `specify version` → PASS (печатает версию и сведения о среде)
    - `specify --help` → PASS
  - Доп. зависимости: установлен `uv` (0.13.6); Python 3.12.3 уже был
  - Предупреждения: отсутствуют

## Шаг 4. Итоговая проверка

| Инструмент | Версия | CLI | Команда проверки | Результат |
|---|---|---|---|---|
| OpenSpec | 1.14.1 | openspec | `openspec --version` | PASS |
| Spec Kit | 1.2.3 | specify | `specify version` | PASS |

Дополнительно:
- OpenSpec: установлен; `--version` PASS; `--help` PASS; зависимости — Node.js >= 20.19.0; предупреждений, влияющих на работу, нет.
- Spec Kit: установлен; `--version` PASS; `--help` PASS; зависимости — Python 3.11+ и uv; проблем нет.

## Шаг 5. Различия установки

### OpenSpec
- установка: глобально через npm `npm install -g @fission-ai/openspec@1.14.1` (официально также поддерживаются бинарный инсталлер и Homebrew)
- CLI: `openspec`
- runtime: Node.js (>= 20.19.0)
- версия: 1.14.1
- способ проверки: `openspec --version`, `openspec --help`, `openspec list --help`

### Spec Kit
- установка: через `uv tool install specify-cli` (рекомендовано документацией); предварительно установлен `uv`
- CLI: `specify`
- runtime: Python 3.11+ (используется 3.12.3) с управлением через uv
- версия: 1.2.3
- способ проверки: `specify version`, `specify --help`

## Шаг 6. Краткий отчёт

1. Установлено:
   - OpenSpec CLI (@fission-ai/openspec) глобально через npm (1.14.1)
   - uv (0.13.6) через официальный инсталлер
   - GitHub Spec Kit CLI (specify-cli) через uv
2. Версии:
   - openspec: 1.14.1
   - specify: 1.2.3
   - uv: 0.13.6
3. Успешные команды:
   - `openspec --version`, `openspec --help`, `openspec list --help`
   - `specify version`, `specify --help`
4. Дополнительно установлено:
   - uv для Spec Kit
   - specify-cli (Spec Kit)
   - OpenSpec CLI через npm
5. Проблемы:
   - Существенных проблем нет. Алиас `python` отсутствует, но `python3` есть (достаточно). Сообщение npm о "funding" — не ошибка.
6. Статус готовности:
   - Оба фреймворка готовы для следующего этапа сравнения; `init` внутри проекта не выполнялся.

## Примечания

- Путь к `openspec`: `/home/salkaatop2000/.npm-global/bin/openspec`
- Путь к `specify`: `/home/salkaatop2000/.local/bin/specify`
- Глобальный npm prefix: `/home/salkaatop2000/.npm-global`
- Yarn и pnpm не установлены (не требуются для текущего этапа)
