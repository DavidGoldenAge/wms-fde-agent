# WMS Incident Triage Agent — synthetic demo

A small local prototype for investigating a synthetic cross-border warehouse inventory incident. It reads a SQLite snapshot, event logs and Python source, asks a local Ollama model for a proposed patch, then optionally runs fixed contract tests in a restricted Docker container. It prints a reviewable report and never applies its proposed patch.

[中文快速说明](#中文快速说明) · [Results and limitations](#results-and-limitations)

## Quick start

Requirements: Python 3.10+, Ollama with a local model for AI triage, and Docker for sandbox tests. The Python code uses the standard library; no pip packages are needed.

```bash
git clone https://github.com/DavidGoldenAge/wms-fde-agent.git
cd wms-fde-agent
python3 setup_incident.py
python3 fde.py evidence --ticket 'Customer reports SKU-8821 is out of stock'
python3 -m unittest -v test_fde
```

The setup creates a synthetic database and log. It refuses to overwrite an existing database. The ticket parser extracts a SKU; this is not an autonomous natural-language tool-selection agent.

For a local model report, install/start Ollama and make `qwen2.5:7b` available (or set `OLLAMA_MODEL` to another installed model). The default server is `http://localhost:11434`; override with `OLLAMA_URL` if needed.

```bash
python3 fde.py triage --ticket 'SKU-8821 cancellation failed' > report.json
```

To run candidate code against fixed tests, start Docker and run:

```bash
docker build -t wms-fde-sandbox:local .
python3 benchmark.py
python3 demonstrate_retry.py > retry_report.json
python3 fde.py triage --ticket 'SKU-8821 cancellation failed' --verify --retries 1 > verified_report.json
```

`benchmark.py` compares the original function with a hand-written reference across 10 contract checks; it is not a 10-ticket benchmark. The AI command records each attempt, model token counts when available, test feedback, elapsed time and a proposed diff. It retries a failing patch at most twice if configured. Generated tests are included in the report for review; the sandbox runs the project's independent fixed checks, not the model's tests. Inspect `attempts` and `applied` in the output. A successful command does not mean the proposed patch passed: inspect `verification.passed`.

## Results and limitations

The simulated incident contains conflicting snapshots: the ledger shows 120 reserved, while the error log says 10 at the time of failure. The evidence does not prove why they differ or determine the right current inventory. A clamp-to-zero policy is a **demo contract**, not a generally safe warehouse accounting policy. Real operations need idempotency, audit trails, reconciliation, event replay rules and human approval.

A local Docker run on 2026-11-20 produced 6/10 passing checks for the original function and 10/10 for the hand-written reference. This assesses a single function and designed contract, not a business resolution rate. There is no 10-independent-incident dataset, Pass@1 estimate, or validated claim of saving 40 minutes. One local qwen2.5:7b run produced a patch passing all 10 checks in 32.11 seconds (587 prompt and 454 completion tokens); its explanation omitted the requested event citation and made an unsupported physical-stock claim. This is one observation, not an estimate of reliability. Model output can be wrong even when valid JSON; review its reasoning and code independently. The retry demonstration starts with deliberately buggy hand-written code, sends its failures to the model and tests the resulting candidate; it is not evidence of a model failing and correcting its own first attempt.

SQLite is opened read-only with an authorizer and bounded query execution. Log output is bounded; Python's AST locates the relevant function. The generated code executes only inside a container with no network, a read-only root, dropped capabilities, a non-root user and limits on memory, CPUs, processes and runtime. Docker isolation reduces risk but is not a security guarantee. Do not run this demo on sensitive data or use its patch in production without proper review. The local model receives the evidence; if `OLLAMA_URL` points to a remote server, the evidence is sent there.

This is a deliberately small prototype: it does not use LangGraph, MCP, Pydantic, Tree-sitter, hybrid retrieval or automatic deployment. It cannot guarantee model-generated tests or root-cause claims are correct. `setup_incident.py` creates reproducible synthetic data, and `results/` and generated databases/logs are ignored by Git.

## 中文快速说明

这是一套**合成数据演示**：先取证，再让本地模型提出补丁，最后在 Docker 中执行固定测试，输出报告供人审核；不会自动改数据库或应用补丁。首次使用请先执行上面的 `python3 setup_incident.py`。查看证据用 `python3 fde.py evidence`，模型报告用 `python3 fde.py triage`，沙盒验证则加 `--verify`。

当前只有一个事故场景，10 项检查是这个场景中函数的不同输入，不是 10 张不同工单。日志里的预占 10 和数据库里的预占 120 不一致，不能直接推断真实库存或保证根因正确。
