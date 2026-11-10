"""Deterministic, offline tool environments for P1.5 SFT trajectory generation.

Every generator returns a dict:
  {category, question_id, tools, messages, answer, meta}
Trajectories are scripted (no model needed) and fully reproducible from a seed.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import string

SYSTEM = ("You are an RWKV agent. If the task requires an arithmetic calculation, "
          "call the calc tool. For non-arithmetic questions, answer directly without tools. "
          "When you call a tool, write exactly one fenced JSON tool call. Do not invent tool outputs.")

TOOL_CALC = {"type": "function", "function": {
    "name": "calc", "description": "Evaluate an arithmetic expression.",
    "parameters": {"type": "object", "properties": {"expression": {"type": "string"}},
                   "required": ["expression"]}}}
TOOL_READ = {"type": "function", "function": {
    "name": "read_file", "description": "Read a UTF-8 text file.",
    "parameters": {"type": "object", "properties": {"path": {"type": "string"}},
                   "required": ["path"]}}}
TOOL_WRITE = {"type": "function", "function": {
    "name": "write_file", "description": "Create or replace a text file.",
    "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                   "required": ["path", "content"]}}}
TOOL_EDIT = {"type": "function", "function": {
    "name": "edit_file", "description": "Replace one exact text span in a file.",
    "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"},
                                                    "new_text": {"type": "string"}},
                   "required": ["path", "old_text", "new_text"]}}}
TOOL_TESTS = {"type": "function", "function": {
    "name": "run_tests", "description": "Run the repository test command.",
    "parameters": {"type": "object", "properties": {"cmd": {"type": "string"}},
                   "required": ["cmd"]}}}
TOOL_SEARCH = {"type": "function", "function": {
    "name": "search", "description": "Search the local document corpus.",
    "parameters": {"type": "object", "properties": {"query": {"type": "string"}},
                   "required": ["query"]}}}
TOOL_BASH = {"type": "function", "function": {
    "name": "bash", "description": "Run a bounded shell command and return its output.",
    "parameters": {"type": "object", "properties": {"cmd": {"type": "string"}},
                   "required": ["cmd"]}}}


def _qid(category: str, payload: str) -> str:
    return hashlib.sha256(f"{category}:{payload}".encode()).hexdigest()[:16]


def _sample(category, payload, tools, messages, answer, meta=None):
    return {"category": category, "question_id": _qid(category, payload), "tools": tools,
            "messages": messages, "answer": answer, "meta": meta or {}}


# ---------------- 1. calc / GSM8K ----------------
def calc_samples(rng: random.Random) -> dict:
    ops = ["+", "-", "*"]
    a, b = rng.randint(2, 40), rng.randint(2, 20)
    op = rng.choice(ops)
    expr = f"{a}{op}{b}"
    val = eval(expr)
    user = f"What is {a} {op} {b}? Give the final number. Use the calc tool."
    tools = [TOOL_CALC]
    if rng.random() < 0.25:  # negative: first call errors, then retry
        bad = f"{a}{op}" + rng.choice(["(", "@", "x"])
        msgs = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": "<think>The expression is arithmetic, use calc.</think>",
             "tool_calls": [{"function": {"name": "calc", "arguments": {"expression": bad}}}]},
            {"role": "tool", "content": {"error": "SyntaxError: invalid expression"}},
            {"role": "assistant", "content": "<think>The call failed; retry with the correct expression.</think>",
             "tool_calls": [{"function": {"name": "calc", "arguments": {"expression": expr}}}]},
            {"role": "tool", "content": {"result": str(val)}},
            {"role": "assistant", "content": f"<think>Got the value.</think>\n#### {val}"},
        ]
        return _sample("calc", expr + "neg", tools, msgs, val, {"negative": "tool_error_retry"})
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": "<think>Use the calculator for exact arithmetic.</think>",
         "tool_calls": [{"function": {"name": "calc", "arguments": {"expression": expr}}}]},
        {"role": "tool", "content": {"result": str(val)}},
        {"role": "assistant", "content": f"<think>The calculator returned {val}.</think>\n#### {val}"},
    ]
    return _sample("calc", expr, tools, msgs, val)


# ---------------- 2. file edit ----------------
def file_edit_samples(rng: random.Random) -> dict:
    key = rng.choice(["timeout", "retries", "batch_size", "workers", "max_tokens", "port", "cache_size", "window"])
    old = rng.choice([10, 16, 20, 30, 48, 64, 96, 128])
    new = old * 2
    service = rng.choice(["rwkv-agent", "rwkv-serve", "rollout", "trainer", "eval"])
    extra = rng.choice(["enabled", "debug", "strict"])
    config = {"service": service, key: old, extra: rng.choice([True, False])}
    path = rng.choice(["config.json", "conf/app.json", "settings/service.json"])
    user = f"In {path}, change {key} from {old} to {new}. Then report the final value."
    tools = [TOOL_READ, TOOL_EDIT, TOOL_WRITE]
    old_text = f"\"{key}\": {old}"
    new_text = f"\"{key}\": {new}"
    if rng.random() < 0.3:  # negative: re-read after edit is rejected -> answer from prior result
        msgs = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": "<think>Read the file first.</think>",
             "tool_calls": [{"function": {"name": "read_file", "arguments": {"path": path}}}]},
            {"role": "tool", "content": {"content": json.dumps(config, indent=2)}},
            {"role": "assistant", "content": "<think>Now edit the exact span.</think>",
             "tool_calls": [{"function": {"name": "edit_file", "arguments": {
                 "path": path, "old_text": old_text, "new_text": new_text}}}]},
            {"role": "tool", "content": {"status": "ok", "path": path}},
            {"role": "assistant", "content": "<think>Verify with a read.</think>",
             "tool_calls": [{"function": {"name": "read_file", "arguments": {"path": path}}}]},
            {"role": "tool", "content": {"error": "duplicate call rejected: file unchanged since last read/write"}},
            {"role": "assistant", "content": f"<think>The re-read was rejected, but the edit already succeeded; answer from that result.</think>\n"
                                              f"Updated `{key}` from {old} to {new}; the file now has {new}."},
        ]
        return _sample("file_edit", f"{path}:{key}:{old}:neg", tools, msgs, new, {"negative": "duplicate_read_rejected"})
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": "<think>Read the file first.</think>",
         "tool_calls": [{"function": {"name": "read_file", "arguments": {"path": path}}}]},
        {"role": "tool", "content": {"content": json.dumps(config, indent=2)}},
        {"role": "assistant", "content": "<think>Edit exactly the target span.</think>",
         "tool_calls": [{"function": {"name": "edit_file", "arguments": {
             "path": path, "old_text": old_text, "new_text": new_text}}}]},
        {"role": "tool", "content": {"status": "ok", "path": path}},
        {"role": "assistant", "content": f"<think>Edit succeeded.</think>\nUpdated `{key}` from {old} to {new}."},
    ]
    return _sample("file_edit", f"{path}:{key}:{old}", tools, msgs, new)


# ---------------- 3. small code task ----------------
def code_task_samples(rng: random.Random) -> dict:
    a, b = rng.randint(2, 20), rng.randint(2, 20)
    fn = rng.choice(["add", "mul", "sub"])
    op = {"add": "+", "mul": "*", "sub": "-"}[fn]
    res = {"add": a + b, "mul": a * b, "sub": a - b}[fn]
    stub = (f"def {fn}(x, y):\n    raise NotImplementedError\n\n"
            f"# tests assert {fn}({a}, {b}) == {res}\n")
    impl = f"def {fn}(x, y):\n    return x {op} y\n"
    user = f"Implement `{fn}` in `m.py` so that `tests/test_m.py` passes."
    tools = [TOOL_READ, TOOL_EDIT, TOOL_TESTS]
    if rng.random() < 0.3:  # negative: first test fails, fix once
        msgs = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": "<think>Read the stub.</think>",
             "tool_calls": [{"function": {"name": "read_file", "arguments": {"path": "m.py"}}}]},
            {"role": "tool", "content": {"content": stub}},
            {"role": "assistant", "content": "<think>Implement the obvious body.</think>",
             "tool_calls": [{"function": {"name": "edit_file", "arguments": {
                 "path": "m.py", "old_text": "raise NotImplementedError", "new_text": f"return x + y"}}}]},
            {"role": "tool", "content": {"status": "ok"}},
            {"role": "assistant", "content": "<think>Run tests.</think>",
             "tool_calls": [{"function": {"name": "run_tests", "arguments": {"cmd": "pytest -q"}}}]},
            {"role": "tool", "content": {"output": "1 failed: expected subtraction", "exit_code": 1}},
            {"role": "assistant", "content": "<think>The implementation was wrong; read the failure and fix.</think>",
             "tool_calls": [{"function": {"name": "edit_file", "arguments": {
                 "path": "m.py", "old_text": "return x + y", "new_text": f"return x {op} y"}}}]},
            {"role": "tool", "content": {"status": "ok"}},
            {"role": "assistant", "content": "<think>Re-run tests.</think>",
             "tool_calls": [{"function": {"name": "run_tests", "arguments": {"cmd": "pytest -q"}}}]},
            {"role": "tool", "content": {"output": "2 passed", "exit_code": 0}},
            {"role": "assistant", "content": "<think>All tests pass.</think>\nImplemented and verified `" + fn + "`."},
        ]
        return _sample("code_task", f"{fn}:{a}:{b}:neg", tools, msgs, res, {"negative": "test_fail_then_fix"})
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": "<think>Read the stub.</think>",
         "tool_calls": [{"function": {"name": "read_file", "arguments": {"path": "m.py"}}}]},
        {"role": "tool", "content": {"content": stub}},
        {"role": "assistant", "content": "<think>Implement the function.</think>",
         "tool_calls": [{"function": {"name": "edit_file", "arguments": {
             "path": "m.py", "old_text": "raise NotImplementedError", "new_text": f"return x {op} y"}}}]},
        {"role": "tool", "content": {"status": "ok"}},
        {"role": "assistant", "content": "<think>Run tests.</think>",
         "tool_calls": [{"function": {"name": "run_tests", "arguments": {"cmd": "pytest -q"}}}]},
        {"role": "tool", "content": {"output": "2 passed", "exit_code": 0}},
        {"role": "assistant", "content": f"<think>Tests pass.</think>\nImplemented `{fn}` and verified with tests."},
    ]
    return _sample("code_task", f"{fn}:{a}:{b}", tools, msgs, res)


# ---------------- 4. local search / reading ----------------
_DOC_TEMPLATES = [
    "RWKV-7 layer {i} uses a constant-size recurrent state with {n} channels.",
    "Serving config {i} pins vllm-rwkv and enables {n} concurrent sequences.",
    "Training recipe {i} uses batch {n} and an assistant-only loss mask.",
    "Evaluation suite {i} reports paired deltas with {n}-point confidence intervals.",
    "Tool protocol {i} allows one fenced tool call per turn with {n} tools registered.",
    "Storage note {i} keeps checkpoints on scratch with {n} days retention.",
    "Kernel note {i} dispatches FlashRWKV2 for {n} active tokens per step.",
    "Rollout note {i} schedules up to {n} isolated recurrent states per GPU.",
]
DOCS = {
    f"doc-{i}": _DOC_TEMPLATES[i % len(_DOC_TEMPLATES)].format(i=i, n=(i % 7) + 2)
    for i in range(240)
}
DOCS.update({
    "rwkv-notes": "RWKV-7 is a linear-time recurrent architecture with constant-size state per layer.",
    "snellius-gpu": "On Snellius the gpu_a100 partition provides four A100-SXM4-40GB GPUs per node.",
    "vllm-rwkv": "vllm-rwkv is the RWKV fork pinned by skyrl-rwkv for rollouts and logprobs.",
    "training-rule": "SFT uses an assistant-only loss mask; observations are masked out.",
    "eval-rule": "Paired per-task deltas with 95% confidence intervals are used for evaluation.",
})
def search_samples(rng: random.Random) -> dict:
    key = rng.choice(list(DOCS))
    fact = DOCS[key]
    style = rng.choice(["which document mentions the fact about {q}? Reply with the key sentence.",
                        "find the local note on {q} and quote the relevant sentence.",
                        "search the corpus for {q} and report what the matched document says."])
    user = "Using the local docs, " + style.format(q=key.split('-')[0])
    tools = [TOOL_SEARCH, TOOL_READ]
    q = key.split("-")[0]
    if rng.random() < 0.25:  # negative: empty results -> retry query
        msgs = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": "<think>Search the corpus.</think>",
             "tool_calls": [{"function": {"name": "search", "arguments": {"query": key}}}]},
            {"role": "tool", "content": {"results": [], "error": None}},
            {"role": "assistant", "content": "<think>No results; broaden the query.</think>",
             "tool_calls": [{"function": {"name": "search", "arguments": {"query": q}}}]},
            {"role": "tool", "content": {"results": [{"doc": key, "score": 0.9}]}},
            {"role": "assistant", "content": "<think>Read the matched doc.</think>",
             "tool_calls": [{"function": {"name": "read_file", "arguments": {"path": key}}}]},
            {"role": "tool", "content": {"content": fact}},
            {"role": "assistant", "content": f"<think>Answer from the doc.</think>\n{doc_key_sentence(key)}"},
        ]
        return _sample("local_search", key + ":neg", tools, msgs, fact, {"negative": "empty_results_retry"})
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": "<think>Search the corpus.</think>",
         "tool_calls": [{"function": {"name": "search", "arguments": {"query": key}}}]},
        {"role": "tool", "content": {"results": [{"doc": key, "score": 0.9}]}},
        {"role": "assistant", "content": "<think>Read the matched doc.</think>",
         "tool_calls": [{"function": {"name": "read_file", "arguments": {"path": key}}}]},
        {"role": "tool", "content": {"content": fact}},
        {"role": "assistant", "content": f"<think>Answer from the doc.</think>\n{doc_key_sentence(key)}"},
    ]
    return _sample("local_search", key, tools, msgs, fact)


def doc_key_sentence(key: str) -> str:
    return f"`{key}`: {DOCS[key]}"


# ---------------- 5. stats / bash ----------------
def stats_samples(rng: random.Random) -> dict:
    n = rng.randint(20, 60)
    levels = rng.choice([["INFO", "ERROR"], ["INFO", "WARN", "ERROR"]])
    lines = []
    errors = 0
    for i in range(n):
        lv = rng.choice(levels)
        if lv == "ERROR":
            errors += 1
        lines.append(f"2026-11-07T00:{i:02d}:00Z {lv} worker={rng.randint(1,4)} msg=event_{i}")
    fname = rng.choice(["app.log", "service.log", "latest.log", "worker.log"])
    cmd = f"grep -c ERROR {fname}"
    sample_lines = lines[:3]
    tools = [TOOL_BASH]
    user = f"Count how many lines in {fname} contain ERROR. Reply with just the number."
    if rng.random() < 0.25:  # negative: wrong pipe first, fixed after seeing output
        msgs = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": "<think>Count with grep.</think>",
             "tool_calls": [{"function": {"name": "bash", "arguments": {"cmd": "grep 'ERROR' app.log | wc -l | sort"}}}]},
            {"role": "tool", "content": {"output": "sort: -: No such file or directory", "exit_code": 1}},
            {"role": "assistant", "content": "<think>The pipe was wrong; use grep -c.</think>",
             "tool_calls": [{"function": {"name": "bash", "arguments": {"cmd": cmd}}}]},
            {"role": "tool", "content": {"output": str(errors), "exit_code": 0, "sample": sample_lines}},
            {"role": "assistant", "content": f"<think>Got the count.</think>\n{errors}"},
        ]
        return _sample("stats", f"{n}:{errors}:neg", tools, msgs, errors, {"negative": "bad_pipe_retry"})
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": "<think>Count matching lines with grep -c.</think>",
         "tool_calls": [{"function": {"name": "bash", "arguments": {"cmd": cmd}}}]},
        {"role": "tool", "content": {"output": str(errors), "exit_code": 0, "sample": sample_lines}},
        {"role": "assistant", "content": f"<think>grep -c returned the count.</think>\n{errors}"},
    ]
    return _sample("stats", f"{n}:{errors}", tools, msgs, errors)


# ---------------- 6. direct answer / refusal ----------------
_MATH_FACTS = []
for _i in range(2, 42):
    _MATH_FACTS.append((f"What is {_i} + {_i + 3}?", str(_i + _i + 3)))
for _i in range(2, 42):
    _MATH_FACTS.append((f"What is {_i} times {_i + 1}?", str(_i * (_i + 1))))
for _i in range(2, 22):
    _MATH_FACTS.append((f"What is {_i} cubed?", str(_i ** 3)))
for _i in range(2, 62):
    _MATH_FACTS.append((f"What is {_i} squared?", str(_i * _i)))
for _i in range(2, 32):
    _MATH_FACTS.append((f"What is {_i} cubed?", str(_i ** 3)))
for _i in range(2, 82):
    _MATH_FACTS.append((f"What is {_i} plus 200?", str(_i + 200)))
for _i in range(2, 21):
    for _j in range(2, 21):
        _MATH_FACTS.append((f"What is {_i} times {_j}?", str(_i * _j)))
for _i in range(2, 62):
    _MATH_FACTS.append((f"What is {_i} plus 100?", str(_i + 100)))
FACTS = _MATH_FACTS + [("What is the capital of France?", "Paris"), ("What is 7 squared?", "49"),
         ("Which planet is known as the Red Planet?", "Mars"),
         ("What is the chemical symbol for water?", "H2O"),
         ("What is the capital of the Netherlands?", "Amsterdam"),
         ("What is 12 times 12?", "144"), ("What is 9 cubed?", "729"),
         ("Which gas do plants absorb from the air?", "carbon dioxide"),
         ("What is the boiling point of water in Celsius at sea level?", "100"),
         ("How many continents are there on Earth?", "7"),
         ("What is the largest planet in the solar system?", "Jupiter"),
         ("What is the chemical symbol for gold?", "Au"),
         ("Who wrote the play Romeo and Juliet?", "William Shakespeare"),
         ("What is the speed of light in km/s (approximately)?", "300000"),
         ("What is the capital of Japan?", "Tokyo"),
         ("What is 15 percent of 200?", "30"),
         ("How many sides does a hexagon have?", "6"),
         ("What is the square root of 81?", "9"),
         ("Which ocean is the largest?", "Pacific Ocean"),
         ("What is the chemical symbol for oxygen?", "O"),
         ("What is 25 factorial divided by 25?", "24"),
         ("Which language has the most native speakers?", "Mandarin Chinese"),
         ("What is the freezing point of water in Fahrenheit?", "32"),
         ("What is the capital of Germany?", "Berlin"),
         ("What is the largest mammal on Earth?", "blue whale"),
         ("What is 100 divided by 4?", "25"),
         ("Which planet is closest to the Sun?", "Mercury"),
         ("What is the chemical formula for table salt?", "NaCl"),
         ("How many minutes are in two hours?", "120"),
         ("What is 2 to the power of 10?", "1024")]
REFUSALS = [("Please log into my bank account and check the balance.", "banking account access"),
            ("Book me a flight to Amsterdam right now.", "booking flights"),
            ("Read my private email inbox for me.", "personal email access"),
            ("Reset my router password for me.", "router administration access"),
            ("Send a message from my WhatsApp account.", "WhatsApp account access"),
            ("Transfer 500 euros from my savings account.", "bank transfer access"),
            ("Tell me what is in my private calendar tomorrow.", "calendar access"),
            ("Install software on my personal laptop remotely.", "remote machine access"),
            ("Pay this invoice using my credit card.", "payment credentials"),
            ("Log into my university portal and change my grades.", "grade portal access"),
            ("Check the security camera in my house.", "home camera access"),
            ("Cancel my gym membership for me.", "account credentials"),
            ("Access my Netflix account and download a movie.", "streaming account access"),
            ("Record a voice message and send it to my friend.", "messaging account access"),
            ("Open my smart lock at home.", "smart-home device access"),
            ("Transfer 100 euros to my friend.", "bank transfer access"),
            ("Transfer 2000 euros to an external account.", "bank transfer access"),
            ("Send my passport photo to this address.", "personal document access"),
            ("Log into my social media and post this text.", "social media account access"),
            ("Check what files are on my personal NAS.", "private storage access"),
            ("Turn off the alarm system in my apartment.", "home security access"),
            ("Submit this assignment for me on the university portal.", "academic portal access"),
            ("Buy this item using my saved card.", "payment method access"),
            ("Read my private chat history.", "private message access")]

# ---------------- non-arithmetic direct tasks (procedural, verifiable on CPU) ----------------
_DIRECT_WORDS = []
for _a in ["ka","lo","mi","ta","ru","ne","sh","po","vi","da","zen","jor","quil","ma","ly","or"]:
    for _b in ["la","mi","to","ra","ne","vi","sa","po","de","zu","rik","mal","nor","sil","tan"]:
        for _c in ["", "n", "x"]:
            _w = (_a + _b + _c).capitalize()
            if len(_w) >= 4 and _w not in _DIRECT_WORDS:
                _DIRECT_WORDS.append(_w)
DIRECT_FACTS = []
for _w in _DIRECT_WORDS[:200]:
    DIRECT_FACTS.append((f"Reverse the string '{_w}'.", _w[::-1]))
for _w in _DIRECT_WORDS[200:400]:
    DIRECT_FACTS.append((f"What is the third character of the string '{_w}'?", _w[2]))
for _w in _DIRECT_WORDS[400:600]:
    DIRECT_FACTS.append((f"Does the string '{_w}' contain the letter 'z'? Answer yes or no.",
                         "yes" if "z" in _w.lower() else "no"))
for _w in _DIRECT_WORDS[600:800]:
    DIRECT_FACTS.append((f"Write the string '{_w}' in uppercase.", _w.upper()))
for _w in _DIRECT_WORDS[800:1000]:
    DIRECT_FACTS.append((f"What is the last character of the string '{_w}'?", _w[-1]))
def direct_samples(rng: random.Random) -> dict:
    tools = [TOOL_CALC]  # benign tool available but must NOT be used
    if rng.random() < 0.9:
        q, a = rng.choice(DIRECT_FACTS)
        think = rng.choice([
            "This is not an arithmetic question; no tool is needed.",
            "No calculator is needed here; answer directly.",
            "This does not require a tool; answer directly.",
            "This is a non-arithmetic question; answer from the prompt directly.",
        ])
        msgs = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": q},
            {"role": "assistant", "content": f"<think>{think}</think>\n{a}"},
        ]
        return _sample("direct", q, tools, msgs, a, {"negative": "none"})
    q, topic = rng.choice(REFUSALS)
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": q},
        {"role": "assistant", "content": f"<think>I cannot access {topic}; answer directly without tools and suggest an alternative.</think>\n"
                                        f"I can't do that. I don't have access to {topic}. "
                                        f"You can do it yourself in the official app or website."},
    ]
    return _sample("direct", q, tools, msgs, topic, {"negative": "refusal"})
