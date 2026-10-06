# Отчёт: локальные модели

## Окружение

- ОС: Ubuntu 24.04.5 LTS; Kernel 6.8.0-138-generic
- CPU: AMD Ryzen 7 7435H
- GPU: NVIDIA GeForce RTX 3050, VRAM 4 GB
- RAM: 15 GiB

## Конфигурация и версии

- Ollama: 0.34.4; OpenCode: 1.18.34; Python: 3.12.3
- Модель: qwen3.5:4b (семейство qwen35), ID d8b0f5e9760c (локально в Ollama)
- Формат/квант: GGUF Q4_K_M; лицензия Apache-2.0; источник — Ollama pull
- Параметры запроса: num_ctx=4096, stream=false, think=false
- Обоснование выбора: 4B (Q4_K_M) — компромисс точность/скорость под 15 GiB RAM и 4 GB VRAM. 2B — быстрее, но хуже по качеству; 9B — риск нехватки памяти/скорости.

## Воспроизведение

- make install → Standard library only: ready
- make test (demo) → 3 теста OK
- Локальная модель и веса подтверждены через Ollama (qwen3.5:4b присутствует в списке моделей)
- Настройка OpenCode: practices/practice_03/lab/demo/opencode.json (Ollama OpenAI-compatible baseURL=http://localhost:11434/v1, модель qwen3.5:4b, read-only агент local-guide)

## Эксперимент (QUESTIONS.md)

Запуски: mode=system, include-demo, model=qwen3.5:4b, temperature=0.2, seed=42. Ответы сохранены в lab/results/*.json.

1. Как запустить тесты? Укажи файл-источник.
- Ответ: «make test; источник — demo/Makefile (цель test запускает python3 -m unittest -v)»
- Основание: demo/Makefile:1-3
- Результат: lab/results/q1_tests.json

2. Что будет при пустом имени подписчика? Подтверди кодом.
- Ответ: «ValueError("empty name")»
- Основание: demo/service.py:5-6
- Результат: lab/results/q2_empty.json

3. Где реализован unsubscribe? Проверь предпосылку вопроса.
- Ответ: «В материалах нет; функция отсутствует»
- Основание: отсутствует в demo/service.py; нет тестов на удаление
- Результат: lab/results/q3_unsubscribe.json

4. Какая CI-система запускает тесты?
- Ответ: «В материалах нет сведений»
- Основание: есть только локальные команды в demo/Makefile и README
- Результат: lab/results/q4_ci.json

5. Сохраняются ли подписки после перезапуска процесса?
- Ответ: «Нет, хранение в памяти (subscribers=set())»
- Основание: demo/service.py:1; тесты очищают состояние перед запуском
- Результат: lab/results/q5_persistence.json

## Вывод

- Модель даёт фактические ответы по коду demo и корректно признаёт отсутствие данных по CI и отсутствующую функцию unsubscribe.
- Для сдачи: Modelfile настроен; make test проходит; opencode.json настроен; ответы на 5 вопросов получены и зафиксированы.
