import json, pathlib, sys, datetime
j = pathlib.Path(sys.argv[1])
def parse(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
rows = []
for d in sorted(p for p in j.iterdir() if p.is_dir()):
    r = d / "result.json"
    if not r.is_file(): continue
    data = json.loads(r.read_text())
    try:
        mins = (parse(data["finished_at"]) - parse(data["started_at"])).total_seconds() / 60
    except Exception:
        continue
    exc = (d / "exception.txt").is_file()
    rew = None
    rj = d / "verifier" / "reward.json"
    if rj.is_file():
        try: rew = json.loads(rj.read_text()).get("reward")
        except Exception: pass
    rows.append((mins, d.name.split("__")[0], exc, rew))
rows.sort(reverse=True)
print(f"{'мин':>6}  {'задача':<20} {'таймаут':<8} награда")
for mins, task, exc, rew in rows:
    print(f"{mins:6.1f}  {task:<20} {'да' if exc else '':<8} {rew if rew is not None else '—'}")
ok = [m for m, _, e, _ in rows if not e]
to = [m for m, _, e, _ in rows if e]
print(f"\nбез таймаута: {len(ok)}, медиана {sorted(ok)[len(ok)//2]:.1f} мин, максимум {max(ok):.1f}" if ok else "")
print(f"с таймаутом: {len(to)}")
