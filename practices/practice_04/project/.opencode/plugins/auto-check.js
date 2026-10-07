// Auto-check plugin: after successful edit tool runs, execute scripts/check.sh
// and post a concise success/failure summary back to the chat.

export default async ({ client, project, directory, $ }) => {
  const log = (...args) => {
    try {
      if (typeof $.log === "function") $.log("auto-check", ...args);
    } catch (_) { /* no-op */ }
  };
  async function runCheck() {
    // Guard: ensure bash exists
    const hasBash = typeof $.which === "function" ? await $.which("bash") : true;
    if (!hasBash) { log("bash not found; skipping auto-check"); return { skipped: true }; }
    const scriptPath = `${directory}/scripts/check.sh`;
    try {
      const res = await $.bash({
        command: `bash "${scriptPath}"`,
        workdir: directory,
        timeout: 180000
      });
      return { ok: true, stdout: res.stdout?.slice(-1000) || "", stderr: res.stderr?.slice(-1000) || "" };
    } catch (err) {
      const msg = err && typeof err === "object" ? (err.message || String(err)) : String(err);
      return { ok: false, error: msg, stdout: err?.stdout || "", stderr: err?.stderr || "" };
    }
  }

  return {
    async "tool.execute.after"(input, output) {
      try {
        if (input?.tool !== "edit") return;
        // Only run after a successful edit application
        const success = output?.result?.ok !== false && !output?.error;
        if (!success) return;
        const res = await runCheck();
        // Post a concise chat message
        const lines = [];
        if (res.skipped) {
          lines.push("auto-check: skipped (bash not available)");
        } else if (res.ok) {
          lines.push("auto-check: scripts/check.sh succeeded");
          const tail = (res.stdout || "").split(/\r?\n/).filter(Boolean).slice(-5).join("\n");
          if (tail) lines.push(tail);
        } else {
          lines.push("auto-check: scripts/check.sh FAILED");
          const errTail = (res.stderr || res.stdout || res.error || "").split(/\r?\n/).filter(Boolean).slice(-5).join("\n");
          if (errTail) lines.push(errTail);
        }
        const content = lines.join("\n");
        if (client && client.chat && typeof client.chat.postMessage === "function") {
          await client.chat.postMessage({ role: "assistant", content });
        } else {
          log(content);
        }
      } catch (e) {
        log("auto-check hook error", e?.message || String(e));
      }
    }
  };
};
