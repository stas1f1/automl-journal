#!/usr/bin/env python3
"""Let the in-container agent reach the model API through an HTTP proxy.

On the compute server everything the run needs is reachable directly except the
model endpoint itself, which answers 403 without a proxy and 200 with one.  The
agent makes its API calls from inside the task container, and the container gets
only the variables named in ``FORWARDED_ENV_VARS``; no proxy variable is among
them, so setting one on the host does nothing.  This adds them.

``NO_PROXY`` is forwarded too and matters: without it every package install the
agent performs inside the container would also be tunnelled, which is slower and
puts avoidable load on a shared proxy.

The layer text is untouched, so runs made after this patch stay comparable with
runs made before it.  That is checked rather than assumed.

    python3 enable_proxy.py            apply and verify
    python3 enable_proxy.py --revert   restore the backup
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROXY_VARS = ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY",
              "http_proxy", "https_proxy", "no_proxy")
BOTH_ON_SHA = "a58b4d40678ff1aa"   # tabular layer, must not move
BOTH_ON_LEN = 4971

BLOCK = (
    "    # Reaching the model endpoint from inside the container: on a network\n"
    "    # that blocks it directly, the proxy has to travel with the call.\n"
    "    # NO_PROXY keeps package installs off the proxy.\n"
    + "".join(f'    "{v}",\n' for v in PROXY_VARS)
)


def venv() -> Path:
    d = subprocess.run(["uv", "tool", "dir"], capture_output=True, text=True, check=True)
    base = Path(d.stdout.strip()) / "harbor/lib"
    for lib in sorted(base.glob("python3.*")):
        p = lib / "site-packages/autods_harbor"
        if p.is_dir():
            return p
    raise SystemExit(f"не найден установленный autods_harbor под {base}")


def apply(v: Path) -> None:
    f = v / "constants.py"
    bak = v / "constants.py.noproxy"
    if not bak.exists():
        shutil.copy2(f, bak)
    s = f.read_text()
    if "HTTPS_PROXY" in s:
        print("уже применено")
        return
    key = 'FORWARDED_ENV_VARS = ('
    i = s.index(key)
    j = s.index("\n)", i)
    f.write_text(s[:j + 1] + BLOCK + s[j + 1:])
    print(f"добавлено переменных: {len(PROXY_VARS)}")


def revert(v: Path) -> None:
    bak = v / "constants.py.noproxy"
    if bak.exists():
        shutil.copy2(bak, v / "constants.py")
        print("восстановлено")
    else:
        print("бэкапа нет, нечего восстанавливать")
    shutil.rmtree(v / "__pycache__", ignore_errors=True)


def check(v: Path) -> bool:
    code = (
        "import hashlib,sys;sys.path.insert(0,%r);"
        "import constants as c, c1_prompt as p;"
        "L=p.augment('','tabular');"
        "print(len([x for x in c.FORWARDED_ENV_VARS if 'PROXY' in x.upper()]));"
        "print(len(L.rstrip()));"
        "print(hashlib.sha256(L.encode()).hexdigest()[:16])" % str(v)
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    if out.returncode:
        print(out.stderr.strip(), file=sys.stderr)
        return False
    nproxy, n, sha = out.stdout.split()
    ok_layer = sha == BOTH_ON_SHA and int(n) == BOTH_ON_LEN
    print(f"переменных прокси в списке: {nproxy}")
    print(f"слой: {n} символов, sha {sha} "
          f"({'не сдвинулся' if ok_layer else 'РАСХОЖДЕНИЕ'})")
    return ok_layer and int(nproxy) >= len(PROXY_VARS)


def main() -> int:
    v = venv()
    if "--revert" in sys.argv:
        revert(v)
        return 0
    apply(v)
    shutil.rmtree(v / "__pycache__", ignore_errors=True)
    if not check(v):
        print("проверка не прошла — откатываю", file=sys.stderr)
        revert(v)
        return 1
    subprocess.run([sys.executable, "-m", "py_compile", str(v / "constants.py")], check=True)
    print("готово")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
