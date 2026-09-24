#!/usr/bin/env python3
"""Backport the two half-flags into the installed autods_harbor.

Why not just reinstall the newer checkout: the prescribed-knowledge layer is
composed on the host by whatever copy of autods_harbor sits in the harbor tool
venv, and the upstream branch has since changed the discipline text and the
graph library block.  Reinstalling would silently swap the treatment and make
new runs incomparable with the `full` arm already measured.

So we add only the mechanism, never the text: `augment` gains tool= and
discipline= keywords, the agent reads AUTODS_K_TOOL_DISABLED and
AUTODS_K_DISC_DISABLED, and the separators are kept exactly as the single-flag
version wrote them so the both-halves-on path stays byte-identical.  That is
checked here, not assumed: the patch reverts itself if the SHA moves.

    python3 enable_halves.py            apply and verify
    python3 enable_halves.py --revert   restore the backups
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

BOTH_ON_SHA = "a58b4d40678ff1aa"   # tabular layer as it shipped in every paper run
BOTH_ON_LEN = 4971


def venv() -> Path:
    d = subprocess.run(["uv", "tool", "dir"], capture_output=True, text=True, check=True)
    base = Path(d.stdout.strip()) / "harbor/lib"
    for lib in sorted(base.glob("python3.*")):
        p = lib / "site-packages/autods_harbor"
        if p.is_dir():
            return p
    raise SystemExit(f"не найден установленный autods_harbor под {base}")


NEW_AUGMENT = '''def augment(
    instruction: str,
    family: str | None,
    *,
    tool: bool = True,
    discipline: bool = True,
) -> str:
    """Append the C1 layer, either half selectable so their effects separate.

    Separators are written exactly as the original single-flag version wrote
    them, so ``tool=True, discipline=True`` stays byte-identical to the runs
    already measured; that is what makes the earlier arm reusable as the
    both-on cell of the design.
    """
    base = instruction.rstrip()
    if not (tool or discipline):
        return base
    fam = normalize_family(family)
    if tool and discipline:
        return f"{base}\\n\\n{_LIBRARY[fam]}\\n{_DISCIPLINE}"
    if tool:
        return f"{base}\\n\\n{_LIBRARY[fam]}"
    return f"{base}\\n\\n{_DISCIPLINE}"


def layer_sizes() -> dict[str, int]:
    return {"discipline": len(_DISCIPLINE), **{f: len(_LIBRARY[f]) for f in FAMILIES}}
'''

OLD_AUGMENT_HEAD = "def augment(instruction: str, family: str | None) -> str:"

OLD_CALL = '''        if not self._get_env("AUTODS_C1_DISABLED"):'''
NEW_CALL = '''        _use_tool = not self._get_env("AUTODS_K_TOOL_DISABLED")
        _use_disc = not self._get_env("AUTODS_K_DISC_DISABLED")
        if not self._get_env("AUTODS_C1_DISABLED") and (_use_tool or _use_disc):'''


def apply(v: Path) -> None:
    for f in ("c1_prompt.py", "agent.py"):
        src, bak = v / f, v / (f + ".single-flag")
        if not bak.exists():
            shutil.copy2(src, bak)

    c1 = v / "c1_prompt.py"
    s = c1.read_text()
    if "tool: bool = True" not in s:
        i = s.index(OLD_AUGMENT_HEAD)
        j = s.index("__all__", i)
        s = s[:i] + NEW_AUGMENT + "\n\n" + s[j:]
        s = s.replace('__all__ = ["FAMILIES", "augment", "normalize_family"]',
                      '__all__ = ["FAMILIES", "augment", "layer_sizes", "normalize_family"]')
        c1.write_text(s)

    ag = v / "agent.py"
    a = ag.read_text()
    if "AUTODS_K_TOOL_DISABLED" not in a:
        if OLD_CALL not in a:
            raise SystemExit("не найдено место вызова слоя в agent.py")
        a = a.replace(OLD_CALL, NEW_CALL, 1)
        a = a.replace(
            "instruction = c1_prompt.augment(instruction, family)",
            "instruction = c1_prompt.augment(\n"
            "                instruction, family, tool=_use_tool, discipline=_use_disc\n"
            "            )", 1)
        a = a.replace(
            'self.logger.info("AutoDS C1 layer applied (family=%s)", family)',
            'self.logger.info(\n'
            '                "AutoDS C1 layer applied (family=%s, tool=%s, discipline=%s)",\n'
            '                family, _use_tool, _use_disc,\n'
            '            )', 1)
        ag.write_text(a)


def revert(v: Path) -> None:
    n = 0
    for f in ("c1_prompt.py", "agent.py"):
        bak = v / (f + ".single-flag")
        if bak.exists():
            shutil.copy2(bak, v / f)
            n += 1
    shutil.rmtree(v / "__pycache__", ignore_errors=True)
    print(f"восстановлено файлов: {n}")


def check(v: Path) -> bool:
    code = (
        "import hashlib,sys;sys.path.insert(0,%r);import c1_prompt as c;"
        "L=c.augment('','tabular');"
        "print(len(L.rstrip()));print(hashlib.sha256(L.encode()).hexdigest()[:16])"
        % str(v)
    )
    out = subprocess.run([sys.executable, "-c", code],
                         capture_output=True, text=True)
    if out.returncode:
        print(out.stderr.strip(), file=sys.stderr)
        return False
    n, sha = out.stdout.split()
    ok = sha == BOTH_ON_SHA and int(n) == BOTH_ON_LEN
    print(f"оба включены: {n} символов, sha {sha} "
          f"({'совпало' if ok else 'РАСХОЖДЕНИЕ'})")
    return ok


def sizes(v: Path) -> None:
    code = (
        "import sys;sys.path.insert(0,%r);import c1_prompt as c\n"
        "for kw,label in (({},'оба'),({'discipline':False},'только library'),"
        "({'tool':False},'только discipline'),"
        "({'tool':False,'discipline':False},'ничего')):\n"
        "    print(f'  {label:<20}{len(c.augment(chr(120), \"tabular\", **kw).rstrip()):>6}')"
        % str(v)
    )
    subprocess.run([sys.executable, "-c", code], check=False)


def main() -> int:
    v = venv()
    if "--revert" in sys.argv:
        revert(v)
        return 0 if check(v) else 1
    apply(v)
    shutil.rmtree(v / "__pycache__", ignore_errors=True)
    if not check(v):
        print("слой изменился — откатываю, экспериментировать с таким нельзя",
              file=sys.stderr)
        revert(v)
        return 1
    # agent.py is a package module and does not import standalone; compiling it
    # is the check that actually applies here.
    subprocess.run([sys.executable, "-m", "py_compile",
                    str(v / "agent.py"), str(v / "c1_prompt.py")], check=True)
    print("длина инструкции по ячейкам (база 1 символ):")
    sizes(v)
    print("готово: код компилируется, текст слоя не тронут")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
