#!/usr/bin/env python3
"""Запускает весь test_AI_security.py до 10 раз и формирует test_report_01.md."""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import time
import unittest
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT / "lab"
TEST_MODULE = "test_AI_security"
REPORT = ROOT / "test_report_01.md"
RUNS = 10


def model_names():
    config_path = ROOT / "opencode.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        # OpenCode config may be JSONC; extract the two values as fallback.
        text = config_path.read_text(encoding="utf-8")
        import re
        found = {}
        for name in ("shop-planner", "threat-judge"):
            match = re.search(
                rf'"{name}"\s*:\s*\{{.*?"model"\s*:\s*"([^"]+)"',
                text, re.S,
            )
            env_name = "AI_SECURITY_PLANNER_MODEL" if name == "shop-planner" else "AI_SECURITY_JUDGE_MODEL"
            found[name] = os.environ.get(env_name) or (match.group(1) if match else "not parsed")
        return found
    agents = config.get("agent", {})
    return {
        name: os.environ.get(
            "AI_SECURITY_PLANNER_MODEL" if name == "shop-planner" else "AI_SECURITY_JUDGE_MODEL",
            agents.get(name, {}).get("model", "not configured"),
        )
        for name in ("shop-planner", "threat-judge")
    }


def classify(result):
    statuses = {}
    details = {}
    for test, _ in result.failures:
        statuses[test.id()] = "FAIL"
        details[test.id()] = _
    for test, _ in result.errors:
        statuses[test.id()] = "ERROR"
        details[test.id()] = _
    for test, reason in result.skipped:
        statuses[test.id()] = "SKIP"
        details[test.id()] = reason
    # Successful tests are those run minus failures/errors/skips.
    for test in getattr(result, "_tests", []):
        statuses.setdefault(test.id(), "PASS")
    return statuses, details


def main():
    sys.path.insert(0, str(LAB))
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    model_map = model_names()
    all_rounds = []
    aggregate = defaultdict(lambda: defaultdict(int))
    stop_reason = None

    for round_no in range(1, RUNS + 1):
        start = time.monotonic()
        suite = unittest.defaultTestLoader.loadTestsFromName(TEST_MODULE)
        def flatten(s):
            for item in s:
                if isinstance(item, unittest.TestSuite):
                    yield from flatten(item)
                else:
                    yield item
        test_ids = [test.id() for test in flatten(suite)]
        output = io.StringIO()
        result = unittest.TextTestRunner(
            stream=output, verbosity=2, failfast=False
        ).run(suite)
        elapsed = time.monotonic() - start

        statuses = {}
        details = {}
        for test, _ in result.failures:
            statuses[test.id()] = "FAIL"
            details[test.id()] = _
        for test, _ in result.errors:
            statuses[test.id()] = "ERROR"
            details[test.id()] = _
        for test, reason in result.skipped:
            statuses[test.id()] = "SKIP"
            details[test.id()] = reason
        for test_id in test_ids:
            statuses.setdefault(test_id, "PASS")
            aggregate[test_id][statuses[test_id]] += 1

        round_data = {
            "round": round_no,
            "seconds": round(elapsed, 2),
            "tests": statuses,
            "details": details,
            "output": output.getvalue(),
            "tests_run": result.testsRun,
        }
        all_rounds.append(round_data)
        print(
            f"Прогон {round_no}: tests={result.testsRun}, "
            f"failures={len(result.failures)}, errors={len(result.errors)}, "
            f"skips={len(result.skipped)}, time={elapsed:.1f}s"
        )

        # Если все тесты пропущены по одной и той же инфраструктурной причине,
        # дальнейшие повторы ничего не добавят. Отмечаем эксперимент как остановленный.
        if statuses and all(value == "SKIP" for value in statuses.values()):
            reasons = set(details.values())
            if len(reasons) == 1:
                stop_reason = next(iter(reasons))
            else:
                stop_reason = "Все тесты пропущены из-за инфраструктурных проблем."
            break

    actual_runs = len(all_rounds)
    total_tests = sum(len(item["tests"]) for item in all_rounds)
    totals = defaultdict(int)
    for item in all_rounds:
        for status in item["tests"].values():
            totals[status] += 1

    lines = [
        "# Отчёт AI Security — 10-кратный прогон",
        "",
        f"- Дата и время начала: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Фактически выполнено прогонов: **{actual_runs} из {RUNS}**",
        f"- Тестовый файл: `lab/test_AI_security.py`",
        f"- Planner: `{model_map['shop-planner']}`",
        f"- Judge: `{model_map['threat-judge']}`",
        "- Системные промпты: `planner-system.txt`, `judge-system-prompt.md` (не изменялись).",
        "",
        "## Итог",
        "",
        f"- Всего выполнений тестовых сценариев: **{total_tests}**",
        f"- PASS: **{totals['PASS']}**",
        f"- FAIL: **{totals['FAIL'] + totals['ERROR']}** "
        f"(FAIL={totals['FAIL']}, ERROR={totals['ERROR']})",
        f"- SKIP: **{totals['SKIP']}**",
        "",
    ]
    if stop_reason:
        lines += [
            "Эксперимент остановлен досрочно, поскольку обнаружена общая "
            "инфраструктурная проблема:",
            "",
            f"> {stop_reason}",
            "",
            f"Оставшиеся прогоны не запускались: {RUNS - actual_runs}.",
            "",
        ]

    lines += [
        "## Статистика по сценариям",
        "",
        "| Сценарий | PASS | FAIL | ERROR | SKIP | Успешность от выполненных попыток |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for test_id in sorted(aggregate):
        counts = aggregate[test_id]
        executed = counts["PASS"] + counts["FAIL"] + counts["ERROR"]
        rate = f"{counts['PASS'] / executed * 100:.1f}%" if executed else "н/д"
        lines.append(
            f"| `{test_id.rsplit('.', 1)[-1]}` | {counts['PASS']} | "
            f"{counts['FAIL']} | {counts['ERROR']} | {counts['SKIP']} | {rate} |"
        )

    lines += ["", "## Результаты каждого прогона", ""]
    for item in all_rounds:
        lines += [
            f"### Прогон {item['round']} ({item['seconds']} с)",
            "",
            f"- Запущено тестов: {item['tests_run']}",
        ]
        for test_id, status in sorted(item["tests"].items()):
            lines.append(f"- `{test_id.rsplit('.', 1)[-1]}`: **{status}**")
            if test_id in item["details"]:
                detail = str(item["details"][test_id]).strip().splitlines()
                if detail:
                    lines.append(f"  - {detail[0][:500]}")
        lines.append("")

    lines += [
        "## Интерпретация",
        "",
        "- `PASS` означает, что planner выдал допустимое решение и judge корректно его оценил.",
        "- `FAIL`/`ERROR` означает ошибку поведения модели, оценки или самого теста.",
        "- `SKIP` означает, что сценарий не удалось проверить из-за инфраструктуры; "
        "пропуски не считаются успешными результатами.",
        "- Отдельный тест `test_server_blocks_forged_export_profiles_for_customer` "
        "проверяет серверный `/assistant/execute` без участия LLM. На исходном уязвимом "
        "Mini Shop он может завершиться FAIL — это ожидаемая фиксация уязвимости, "
        "а не доказательство сбоя модели.",
        "",
        "## Ограничения",
        "",
        "В отчёт включены только фактические результаты запусков этого скрипта. "
        "Если AI-тесты пропущены из-за отсутствия OpenCode или доступа к провайдеру, "
        "по ним нельзя делать вывод о безопасности или устойчивости моделей.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nОтчёт записан: {REPORT}")


if __name__ == "__main__":
    main()
