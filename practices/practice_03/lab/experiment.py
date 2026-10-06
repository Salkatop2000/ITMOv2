"""Controlled local Ollama experiment; standard library only.

Extended to support arbitrary questions and include demo file contents
in the context so the model can ground its answers in code. This avoids
any external dependencies and keeps the experiment reproducible.
"""
import argparse
import json
import time
import urllib.request
from pathlib import Path

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_demo_context(root: Path) -> str:
    """Compose a compact textual context from key demo files.

    Keep it small and explicit: filename headers + content. This helps
    the local model cite facts and reduces hallucinations.
    """
    demo = root / "demo"
    files = [
        demo / "README.md",
        demo / "Makefile",
        demo / "service.py",
        demo / "test_service.py",
    ]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f"FILE: {f.relative_to(root)}\n---\n{_read(f)}\n")
    return "\n".join(parts)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["baseline", "system"], required=True)
    p.add_argument("--model", default="qwen3.5:4b")
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output", required=True)
    p.add_argument("--question", required=False, help="Custom user question. If omitted, uses CI question.")
    p.add_argument("--include-demo", action="store_true", help="Include demo files content in user context.")
    args = p.parse_args()
    root = Path(__file__).resolve().parent
    # Build context
    if args.include_demo:
        context = build_demo_context(root)
    else:
        context = _read(root / "demo/README.md")
    messages = []
    if args.mode == "system":
        messages.append({"role": "system", "content": _read(root / "system.txt")})
    question = args.question or "Какая CI-система запускает тесты проекта?"
    messages.append({"role": "user", "content": context + "\n" + question})
    payload = {"model": args.model, "messages": messages, "stream": False, "think": False,
               "options": {"temperature": args.temperature, "seed": args.seed, "num_ctx": 4096, "num_predict": 512}}
    request = urllib.request.Request("http://localhost:11434/api/chat",
        data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            answer = json.load(response)
    except Exception as exc:
        raise SystemExit("Local Ollama request failed: " + str(exc))
    duration = answer.get("eval_duration", 0)
    record = {"request": payload, "response": answer, "wall_seconds": time.perf_counter() - started,
              "load_seconds": answer.get("load_duration", 0) / 1e9,
              "total_seconds": answer.get("total_duration", 0) / 1e9,
              "decode_tokens_per_second": answer.get("eval_count", 0) / (duration / 1e9) if duration else None}
    with Path(args.output).open("x", encoding="utf-8") as out:
        json.dump(record, out, ensure_ascii=False, indent=2)
    print(answer.get("message", {}).get("content", ""))
    print("Saved:", args.output)

if __name__ == "__main__":
    main()
