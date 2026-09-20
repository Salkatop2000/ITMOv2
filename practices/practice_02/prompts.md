# Журнал экспериментов Практики 2

Файл ведёт OpenCode по вашим запросам. Агент записывает фактические результаты экспериментов и вносит изменения в связанные файлы. Свою оценку сообщайте ему в чате; вручную заполнять шаблон не нужно.

- Выбранный слабый артефакт Практики 1:
- Что в нём нужно улучшить:
- Как поймём, что изменение полезно:

| Техника | Файл эксперимента | Изменённый файл Практики 1 | Конкретное изменение | Проверка | Что отклонили |
|---|---|---|---|---|---|
| Few-shot | [`few_shot/experiment.md`](few_shot/experiment.md) | `practices/practice_01/problem.md` | Уточнён раздел «## Проблема»: оставлены факты из TRAINING_PR.diff, удалены непроверяемые утверждения | Статическая проверка по TRAINING_PR.diff:35–37 и 19–22 | Утверждения про 500, неверный тип тела, задержки, безопасность и роль пользователя без источника |
| R.C.T.F. | [`rctf/experiment.md`](rctf/experiment.md) |  |  |  |  |
| Chain of Verification | [`chain_of_verification/experiment.md`](chain_of_verification/experiment.md) |  |  |  |  |
| Tree of Thoughts | [`tree_of_thoughts/experiment.md`](tree_of_thoughts/experiment.md) |  |  |  |  |
| RAG | [`rag/experiment.md`](rag/experiment.md) |  |  |  |  |
| ReAct | [`react/experiment.md`](react/experiment.md) |  |  |  |  |
