"""Shared OpenCode runner for Shop and security judge."""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path
from typing import Any
PRACTICE_DIR = Path(__file__).resolve().parent.parent
OPENCODE_BIN = shutil.which("opencode")
TIMEOUT_SECONDS = int(os.environ.get("AI_SECURITY_TIMEOUT", "180"))
MODEL_OVERRIDES = {
    "shop-planner": os.environ.get("AI_SECURITY_PLANNER_MODEL", "").strip(),
    "threat-judge": os.environ.get("AI_SECURITY_JUDGE_MODEL", "").strip(),
}
class AIInfrastructureError(unittest.SkipTest):
    """OpenCode/provider unavailable."""

def _run_agent(agent: str, prompt: str, timeout: int = TIMEOUT_SECONDS) -> str:
    if OPENCODE_BIN is None:
        raise AIInfrastructureError(
            "opencode CLI не найден в PATH. Установите OpenCode и повторите запуск."
        )

    cmd = [
        OPENCODE_BIN, "run",
        "--dir", str(PRACTICE_DIR),
        "--agent", agent,
        "--format", "json",
    ]
    override = MODEL_OVERRIDES.get(agent)
    if override:
        cmd.extend(["--model", override])
    cmd.append(prompt)

    try:
        proc = subprocess.run(
            cmd, cwd=PRACTICE_DIR, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise AIInfrastructureError(
            f"Тайм-аут агента {agent} после {timeout} секунд"
        ) from exc
    except OSError as exc:
        raise AIInfrastructureError(f"Не удалось запустить opencode: {exc}") from exc

    events: list[dict[str, Any]] = []
    non_json_stdout: list[str] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                events.append(item)
        except json.JSONDecodeError:
            non_json_stdout.append(line)

    # Ошибка CLI/провайдера — инфраструктурный SKIP. Если CLI завершился
    # успешно, но модель выдала плохой JSON/вердикт, это уже FAIL в тесте.
    if proc.returncode != 0:
        details = (proc.stderr or proc.stdout)[-1500:]
        raise AIInfrastructureError(
            f"opencode run ({agent}) завершился с кодом {proc.returncode}: {details}"
        )

    text_parts = [
        event.get("part", {}).get("text", "")
        for event in events
        if event.get("type") == "text"
        and isinstance(event.get("part"), dict)
    ]
    final_text = "\n".join(part for part in text_parts if part).strip()
    if not final_text:
        final_text = "\n".join(non_json_stdout).strip()
    if not final_text:
        raise AssertionError(
            f"Агент {agent} завершился без текстового ответа. stderr: {proc.stderr[-1000:]}"
        )
    return final_text


