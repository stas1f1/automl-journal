"""Ячейка AutoDS-Tools на glm-4.7 после допрогона 07.10.2026: 24 запуска, три на задачу.

Проход 1 — август; проходы 2 и 3 — допрогон.  Запуски, упавшие на glob_search
или не стартовавшие из-за таймаута установки, заменены перезапуском после правки
адаптера (fix_chain.sh).  Печатает средние по задачам, отказы, таймауты, токены и
стоимость в том виде, в каком их берёт paper/make_tables.py.
"""
import json, glob, os, statistics as st

J = os.path.join(os.path.dirname(__file__), "..", "jobs")
TASKS = ["homesite-insurance", "ecom-offers", "homecredit-default", "sberbank-housing",
         "cooking-time", "delivery-eta", "maps-routing", "weather"]
P1, P2, P3 = ("autods-tabred-Mlarge-20260830-003247", "autods-tabred-Mlarge-20261007-164920",
              "autods-tabred-Mlarge-20261007-182416")
F1, F2 = "autods-tabred-Mlarge-fix-20261007-202855", "autods-tabred-Mlarge-fix-20261007-214037"
REPLACE = {  # (проход, задача) -> задание с заменой
    (2, "cooking-time"): F1, (2, "homecredit-default"): F1, (2, "sberbank-housing"): F1,
    (3, "ecom-offers"): F1, (3, "cooking-time"): F2, (3, "homecredit-default"): F2,
}


def trial(job, task):
    d = glob.glob(f"{J}/{job}/{task}__*/")
    assert len(d) == 1, (job, task, d)
    return d[0]


def read(d):
    r = json.load(open(d + "result.json"))
    rw = d + "verifier/reward.json"
    rew = json.load(open(rw)) if os.path.exists(rw) else {}
    metric = rew.get("rmse", rew.get("roc_auc"))
    ex = (r.get("exception_info") or {}).get("exception_type")
    ar = r.get("agent_result") or {}
    return dict(metric=metric, ex=ex, tin=ar.get("n_input_tokens") or 0,
                tout=ar.get("n_output_tokens") or 0, cost=ar.get("cost_usd") or 0.0)


def cell(passes):
    rows = []
    for p, job in passes:
        for t in TASKS:
            d = trial(REPLACE.get((p, t), job), t)
            rows.append((p, t, d.split("/")[-3], read(d)))
    return rows


if __name__ == "__main__":
    for label, passes in [("август, 8", [(1, P1)]), ("итог, 24", [(1, P1), (2, P2), (3, P3)])]:
        rows = cell(passes)
        print(f"== {label}")
        means = []
        for t in TASKS:
            v = [x["metric"] for _, tt, _, x in rows if tt == t and x["metric"] is not None]
            means.append(round(st.mean(v), 6) if v else None)
            print(f"  {t:20s} n={len(v)} {['%.4f' % a for a in v]}")
        lost = sum(x["metric"] is None for *_, x in rows)
        cut = sum(x["ex"] == "AgentTimeoutError" for *_, x in rows)
        other = [(p, t, x["ex"]) for p, t, _, x in rows if x["ex"] not in (None, "AgentTimeoutError")]
        print("  средние:", means)
        print(f"  без результата {lost}/{len(rows)}, таймаутов {cut}, иные исключения {other}")
        print(f"  вх. токенов на запуск {round(st.mean(x['tin'] for *_, x in rows)):,}, "
              f"стоимость всего ${sum(x['cost'] for *_, x in rows):.4f}, "
              f"на проход из 8 ${sum(x['cost'] for *_, x in rows) / (len(rows) / 8):.4f}")
