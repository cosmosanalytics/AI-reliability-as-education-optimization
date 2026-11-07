"""OpenAI-compatible client for the local llama.cpp server used by the SWE-2 experiments."""

import json
import os
import random
import time
import urllib.request

BASE_URL = os.environ.get("SWE2_BASE_URL", "http://127.0.0.1:8080")
MODEL_ID = os.environ.get("SWE2_MODEL_ID", "Qwen3.6-35B-A3B-UD-Q4_K_M")

# Qwen3.6 recommended sampling for instruct (non-thinking) mode.
SAMPLING = {"temperature": 0.7, "top_p": 0.8, "top_k": 20, "min_p": 0.0, "presence_penalty": 1.5}


def chat(messages, max_tokens=4096, thinking=False, temperature=None, seed=None, retries=6, **extra):
    """messages: list of {"role", "content"}. Returns dict(text, prompt_tokens, completion_tokens,
    finish, latency_sec)."""
    body = {
        "model": MODEL_ID, "messages": messages, "max_tokens": max_tokens,
        "seed": seed if seed is not None else random.randint(0, 2**31 - 1),
        "chat_template_kwargs": {"enable_thinking": thinking},
        **SAMPLING, **extra,
    }
    if temperature is not None:
        body["temperature"] = temperature
    data = json.dumps(body).encode()
    delay, last = 5.0, None
    for _ in range(retries):
        try:
            t0 = time.time()
            req = urllib.request.Request(f"{BASE_URL}/v1/chat/completions", data=data,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=7200) as resp:
                res = json.loads(resp.read())
            ch = res["choices"][0]
            usage = res.get("usage", {})
            return {
                "text": ch["message"].get("content") or "",
                "reasoning": ch["message"].get("reasoning_content") or "",
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "finish": ch.get("finish_reason") or "none",
                "latency_sec": round(time.time() - t0, 2),
            }
        except Exception as e:  # noqa: BLE001
            last = str(e)[:300]
            time.sleep(delay + random.random())
            delay = min(delay * 2, 60)
    raise RuntimeError(f"local server failure: {last}")
