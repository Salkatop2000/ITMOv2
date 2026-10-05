# Отчёт: локальные модели

Отчёт ведёт OpenCode по фактическим результатам команд и вашим сообщениям в чате. Поручите агенту заполнить разделы и показать diff. Выводы студента он записывает после обсуждения; отсутствующие измерения отмечает как невыполненные.

## Окружение

ОС / CPU / GPU / RAM / VRAM / свободный диск:
Linux salkaatop2000-X-Treme-Typhoon-Series 6.8.0-138-generic #138-Ubuntu SMP PREEMPT_DYNAMIC Fri Jul 31 22:41:49 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux
Distributor ID:\tUbuntu
Description:\tUbuntu 24.04.5 LTS
Release:\t24.04
Codename:\tnoble
model name\t: AMD Ryzen 7 7435H
               всего        занят        своб      общая  буф/врем.   доступно
Память:         15Gi       6,4Gi       631Mi        57Mi       8,3Gi       9,0Gi
Подкачка:      2,0Gi          0B       2,0Gi
Файл.система   Размер Использовано  Дост Использовано% Cмонтировано в
/dev/nvme0n1p3    96G          64G   28G           70% /
Mon Oct  5 00:33:04 2026      
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 595.91.07              Driver Version: 595.91.07      CUDA Version: 13.2     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 3050 ...    Off |   00000000:01:00.0  On |                  N/A |
| N/A   41C    P8              4W /   60W |     819MiB /   4096MiB |     12%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

Ollama или LM Studio / OpenCode / Python, версии:
ollama version is 0.34.4
1.18.34
Python 3.12.3
Модель, разработчик, семейство, тег и ID:
Формат, квантизация, лицензия, источник:
Фактический контекст, размещение CPU/GPU:
Почему выбрана эта конфигурация:
Выбрана qwen3.5:4b (Q4_K_M) как баланс точности/скорости на 15 GiB RAM и 4 GiB VRAM; уже скачана. Альтернативы: 2b быстрее с потерей качества; 0.8b слишком слабая; 9b риск нехватки памяти и низкая скорость на CPU.

## Сравнение семейств

| Разработчик / модель | Задача | Параметры / формат | Лицензия | Язык / tools | Источник |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |

## Воспроизведение

Команды и файлы конфигурации:
make install:
Standard library only: ready
make test (demo):
test_duplicate (test_service.SubscribeTest.test_duplicate) ... ok
test_empty (test_service.SubscribeTest.test_empty) ... ok
test_subscribe (test_service.SubscribeTest.test_subscribe) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
Подтверждение локального endpoint и скачанных весов:
curl --fail http://localhost:11434/api/tags:
{"models": [{"name": "itmo-local:latest", "model": "itmo-local:latest", "modified_at": "2026-10-04T23:49:48.916527519+03:00", "size": 3324174314, "digest": "94ff63f781e31970944ffce78c1fa86a8e06c70d386a071e176e6af6ed999517", "details": {"parent_model": "qwen3.5:4b", "format": "gguf", "family": "qwen35", "families": ["qwen35"], "parameter_size": "4.2B", "quantization_level": "Q4_K_M", "context_length": 262144, "embedding_length": 2560}, "capabilities": ["completion", "vision", "tools", "thinking"]}, {"name": "qwen3.5:4b", "model": "qwen3.5:4b", "modified_at": "2026-10-04T23:18:48.925672256+03:00", "size": 3324173934, "digest": "d8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04", "details": {"parent_model": "model.gguf", "format": "gguf", "family": "qwen35", "families": ["qwen35"], "parameter_size": "4.2B", "quantization_level": "Q4_K_M", "context_length": 262144, "embedding_length": 2560}, "capabilities": ["completion", "vision", "tools", "thinking"]}]}
ollama list:
NAME                 ID              SIZE      MODIFIED          
itmo-local:latest    94ff63f781e3    3.3 GB    46 minutes ago       
qwen3.5:4b           d8b0f5e9760c    3.3 GB    About an hour ago    
ollama show qwen3.5:4b (фрагмент):
architecture        qwen35
parameters          4.2B
context length      262144
quantization        Q4_K_M
License             Apache License 2.0
Проверка без сети после подготовки:
Если работали в паре, чей компьютер и почему:

## Эксперимент

Фактор A/B:
Неизменные условия:
| Вопрос | Эталон и file:line | Ответ A | Ответ B | Верно A/B | Наблюдение инструментов |
|---|---|---|---|---|---|

Базовый запуск (baseline), модель qwen3.5:4b, temperature=0.2, seed=42:
Ответ: "В предоставленном описании задачи не указана конкретная CI-система..." (признание отсутствия данных, формат близок к требованию)
Метрики: wall_seconds=16.57; load_seconds=0.00; total_seconds=16.54; decode_tokens_per_second≈11.60

System prompt (system.txt), тот же вопрос, модель qwen3.5:4b, temperature=0.2, seed=42:
Ответ: "В предоставленных материалах нет ответа. Основание: ... CI-система не упомянута" (короткий ответ + основание из контекста).
Метрики: wall_seconds=17.10; load_seconds=9.76; total_seconds=17.07; decode_tokens_per_second≈12.77

Сравнение temperature (system.txt), одна и та же модель и вопрос, think=false:
seed 42/43/44 при temperature=0.2 и 0.8 — во всех шести ответах выдуманных сведений о CI нет; модель признаёт отсутствие данных и даёт основание; формат соблюдён. При одинаковом seed различаются формулировки основания, смысл совпадает.

## Скорость

Холодный старт отдельно:
system (первый запуск): load_seconds≈9.76 (results/system.json)
Три прогретых повтора и медиана:
temperature=0.8, seed=42: wall=4.9587; load≈0.0011; total=4.9417; decode_tps=12.3013
temperature=0.8, seed=43: wall=5.0509; load≈0.0012; total=5.0292; decode_tps=11.6719
temperature=0.8, seed=44: wall=6.0142; load≈0.0011; total=5.9842; decode_tps=12.1991
temperature=0.2, seed=42: wall=7.2045; load≈0.0012; total=7.1876; decode_tps=12.3605
temperature=0.2, seed=43: wall=5.1787; load≈0.0011; total=5.1623; decode_tps=11.9660
temperature=0.2, seed=44: wall=6.3906; load≈0.0011; total=6.3637; decode_tps=11.0223
Единицы и метод замера:
секунды; decode_tokens_per_second — токенов/сек; по 3 прогретых повтора на конфигурацию, медиана из трёх значений.
TTFT измерен или не измерен:
не измерен (ответ не потоковый)

## Вывод

Ошибка или обнаруженное ограничение:
в эксперименте увеличение temperature с 0.2 до 0.8 не привело к фактическим ошибкам или нарушению формата; наблюдается небольшая вариативность формулировок.
Как проверили:
шесть запусков (0.2/0.8 × seed 42/43/44) в режиме system; сравнение ответов и метрик; скорости — медиана трёх прогретых повторов.
Какой конфигурацией будете пользоваться:
оставляем temperature=0.2 как дефолт для воспроизводимости; допускаем 0.8 по задаче.
Что осталось непроверенным:
влияние temperature на более сложные вопросы и в других моделях; TTFT на потоковых ответах.
