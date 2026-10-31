#!/usr/bin/env python3
"""Timed benign generation test for a Gradio space. Params as JSON list."""
import os, sys, time, json

_np = os.environ.get("NO_PROXY", "")
_np = ",".join(p for p in _np.split(",") if not (p.startswith("[") and p.endswith("]")))
os.environ["NO_PROXY"] = _np
os.environ["no_proxy"] = _np

import httpx
from gradio_client import Client

sid, api, params_json = sys.argv[1], sys.argv[2], sys.argv[3]
params = json.loads(params_json)
t0 = time.time()
try:
    c = Client(sid, httpx_kwargs={"timeout": httpx.Timeout(600.0, connect=30.0)})
    r = c.predict(*params, api_name=api)
    dt = time.time() - t0
    s = json.dumps(r, default=str)
    print(f"{sid} OK gen_time={dt:.1f}s")
    print("result:", s[:400])

    def find(o):
        if isinstance(o, str) and os.path.exists(o):
            return o
        if isinstance(o, dict):
            for v in o.values():
                f = find(v)
                if f:
                    return f
        if isinstance(o, (list, tuple)):
            for v in o:
                f = find(v)
                if f:
                    return f
        return None

    f = find(r)
    print("file:", f, ("size=" + str(os.path.getsize(f)) if f else ""))
except Exception as e:
    print(f"{sid} GEN_FAIL {time.time()-t0:.1f}s | {type(e).__name__}: {str(e)[:250]}")
