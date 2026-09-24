"""Harbor installed-agent adapter for FEDOT.LLM.

FEDOT.LLM is a fixed pipeline: it takes a task directory with train.csv,
test.csv, a description file and a sample submission, infers the columns and
the problem type with the LLM, fits the FEDOT backend and writes one CSV. This
adapter runs that CLI inside the task container, where ``fedotllm`` is baked
into the image (see make_cases.py), and points its output at the file the
verifier scores.

Runs in the harbor host process; imports ``harbor`` only.
"""

from __future__ import annotations

import shlex
from pathlib import PurePosixPath
from typing import Any, override

from harbor.agents.installed.base import BaseInstalledAgent, with_prompt_template
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trial.paths import EnvironmentPaths

WORKSPACE = "/workspace"
SUBMISSION = f"{WORKSPACE}/submission.csv"
DESCRIPTION = f"{WORKSPACE}/description.md"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
# Seconds FEDOT.LLM gets for inference + fit + predict; the Harbor task ceiling
# is 3600 s and the image build and verifier sit outside it.
DEFAULT_TIME_LIMIT = "2400"


class FedotLLMAgent(BaseInstalledAgent):
    """Run the FEDOT.LLM CLI as a Harbor agent."""

    @staticmethod
    @override
    def name() -> str:
        return "fedotllm"

    @override
    def get_version_command(self) -> str | None:
        return "fedotllm --help >/dev/null 2>&1 && echo fedotllm"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        # fedotllm is baked into the task image; fail loudly if it is not.
        await self.exec_as_agent(environment, command="command -v fedotllm >/dev/null 2>&1")

    def _model(self) -> str:
        m = self._get_env("FEDOTLLM_MODEL") or self.model_name or ""
        if m.startswith("openrouter/"):
            m = m[len("openrouter/"):]
        if not m:
            raise RuntimeError("no model: pass -m openrouter/<model> or FEDOTLLM_MODEL")
        return m

    @with_prompt_template
    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        # The task text is the description FEDOT.LLM reads to infer columns,
        # problem type and metric. Nothing is appended to it.
        instruction_path = self.logs_dir / "instruction.md"
        instruction_path.write_text(instruction, encoding="utf-8")
        await environment.upload_file(instruction_path, PurePosixPath(DESCRIPTION).as_posix())

        # FEDOT.LLM's output contract is a sample submission: id column plus
        # target column. Both names are the constants prepare.py staged the
        # task with, so the file is derived from the task, not from the text.
        stage = (
            "cd /workspace && python - <<'PY'\n"
            "import sys, pandas as pd\n"
            "sys.path.insert(0, '/opt/mlab')\n"
            "import prepare\n"
            "t = pd.read_csv('/workspace/test.csv')\n"
            "pd.DataFrame({prepare.ID: t[prepare.ID], prepare.TARGET: 0}).to_csv('/workspace/sample_submission.csv', index=False)\n"
            "print('sample_submission.csv', prepare.ID, prepare.TARGET, len(t))\n"
            "PY"
        )
        await self.exec_as_agent(environment, command=stage)
        await self._run_fedotllm(environment)

    async def _run_fedotllm(self, environment: BaseEnvironment) -> None:
        """Run the CLI on /workspace with the model, key, proxy and budget."""
        key = self._get_env("FEDOTLLM_LLM_API_KEY", "OPENROUTER_API_KEY", "AUTODS_API_KEY")
        if not key:
            raise RuntimeError("no API key: FEDOTLLM_LLM_API_KEY, OPENROUTER_API_KEY or AUTODS_API_KEY")
        env = {
            "FEDOTLLM_LLM_API_KEY": key,
            "PYTHONUNBUFFERED": "1",
        }
        # The LLM client runs inside the container, so the host's proxy settings
        # must travel with it (Terminus-2 talks to the API from the host and
        # never needed this; AutoDS forwards the same variables).
        for var in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "ALL_PROXY",
                    "http_proxy", "https_proxy", "no_proxy", "all_proxy"):
            val = self._get_env(var)
            if val:
                env[var] = val
        base_url = self._get_env("FEDOTLLM_BASE_URL") or DEFAULT_BASE_URL
        time_limit = self._get_env("FEDOTLLM_TIME_LIMIT") or DEFAULT_TIME_LIMIT
        # FEDOT evaluates candidate pipelines in parallel on every core
        # (n_jobs=-1), each worker holding its own copy of the data. Unset, the
        # snapshot default stands; set, it caps the workers, which is a resource
        # setting and leaves presets, tuning and the budget untouched.
        n_jobs = self._get_env("FEDOTLLM_N_JOBS")
        extra = f" -o automl.fedot.predictor_init_kwargs.n_jobs={int(n_jobs)}" if n_jobs else ""
        # FEDOT validates by 5-fold CV. Its tuner scores the initial pipeline
        # that way before checking the clock, so on a large table the first
        # evaluation alone can outlast the budget (weather, 21.09: 48 min for
        # one 5-fold score of scaling -> rfr). "none" switches FEDOT to a
        # holdout split; an integer sets the number of folds. fedotllm turns -o
        # values into Python with eval(), so the literal must be None: YAML's
        # "null" would arrive as a string (smoke 22.09: TypeError in FEDOT).
        cv = self._get_env("FEDOTLLM_CV_FOLDS")
        if cv:
            cv_val = "None" if cv.lower() in ("none", "null", "holdout") else str(int(cv))
            extra += f" -o automl.fedot.predictor_init_kwargs.cv_folds={cv_val}"
        # Column types from outside (fedot_patch.py, change 4): a JSON list of
        # categorical columns that a subclass writes during staging.
        types_file = getattr(self, "_categorical_columns_file", None)
        if types_file:
            extra += f" -o automl.fedot.categorical_columns={types_file}"
        log_out = (EnvironmentPaths.agent_dir / "fedotllm.log").as_posix()
        command = (
            f"cd {WORKSPACE} && fedotllm {WORKSPACE}"
            f" -o llm.provider=openai"
            f" -o llm.base_url={shlex.quote(base_url)}"
            f" -o llm.model={shlex.quote(self._model())}"
            f" -o automl.enabled=fedot"
            f" -o time_limit={shlex.quote(time_limit)}"
            f"{extra}"
            f" -o save_artifacts.enabled=False"
            f" --output-filename {SUBMISSION}"
            f" 2>&1 | tee {log_out}"
        )
        self.logger.info("fedotllm: model=%s base_url=%s time_limit=%s n_jobs=%s cv_folds=%s",
                         self._model(), base_url, time_limit, n_jobs or "default", cv or "default")
        await self.exec_as_agent(environment, command=command, env=env)


class FedotLLMTabredAgent(FedotLLMAgent):
    """FEDOT.LLM on the TabReD tasks of harbor-tabred-adapter.

    Same CLI, same config, same budget as the case runs; only the file layout
    differs. TabReD ships /app/data/{train,val,test}.csv with a ``target``
    column and scores /app/predictions.csv, a single ``target`` column in the
    row order of test.csv. FEDOT.LLM wants a task directory with train.csv,
    test.csv and a sample submission, and writes an id column plus the target.

    The training table is train.csv plus val.csv: the other two systems see the
    labelled validation split too, and FEDOT holds out its own validation. No
    id column is added to the data. With ``detect_and_drop_id_column`` off,
    FEDOT.LLM fills the sample submission's ``id`` with row numbers, so the
    output keeps the order of test.csv and no row index becomes a feature.
    """

    @staticmethod
    @override
    def name() -> str:
        return "fedotllm-tabred"

    @with_prompt_template
    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        instruction_path = self.logs_dir / "instruction.md"
        instruction_path.write_text(instruction, encoding="utf-8")
        await environment.upload_file(instruction_path, PurePosixPath(DESCRIPTION).as_posix())

        stage = (
            "cd /workspace && python - <<'PY'\n"
            "import pandas as pd\n"
            "tr = pd.read_csv('/app/data/train.csv')\n"
            "va = pd.read_csv('/app/data/val.csv')\n"
            "te = pd.read_csv('/app/data/test.csv')\n"
            "assert 'target' in tr.columns and 'target' in va.columns and 'target' not in te.columns\n"
            "pd.concat([tr, va], ignore_index=True).to_csv('/workspace/train.csv', index=False)\n"
            "te.to_csv('/workspace/test.csv', index=False)\n"
            "pd.DataFrame({'id': range(len(te)), 'target': 0}).to_csv('/workspace/sample_submission.csv', index=False)\n"
            "print('staged: train', len(tr), '+ val', len(va), '| test', len(te), '| features', te.shape[1])\n"
            "PY"
        )
        await self.exec_as_agent(environment, command=stage)

        # FEDOTLLM_TYPES=schema: give FEDOT the categorical columns the way the
        # task states them (the cat_ prefix in the instruction and schema.json),
        # so FEDOT does not guess types by the number of distinct values.
        if (self._get_env("FEDOTLLM_TYPES") or "").lower() == "schema":
            self._categorical_columns_file = f"{WORKSPACE}/categorical_columns.json"
            types = (
                "cd /workspace && python - <<'PY'\n"
                "import json, pandas as pd\n"
                "cols = [c for c in pd.read_csv('/workspace/test.csv', nrows=0).columns if c.startswith('cat_')]\n"
                f"json.dump(cols, open('{self._categorical_columns_file}', 'w'))\n"
                "print('categorical columns from schema:', len(cols))\n"
                "PY"
            )
            await self.exec_as_agent(environment, command=types)

        await self._run_fedotllm(environment)

        # The verifier reads one column named target, in the order of test.csv.
        finish = (
            "cd /workspace && python - <<'PY'\n"
            "import pandas as pd\n"
            f"s = pd.read_csv('{SUBMISSION}')\n"
            "n = sum(1 for _ in open('/workspace/test.csv')) - 1\n"
            "assert 'target' in s.columns, f'no target column in submission: {list(s.columns)}'\n"
            "assert len(s) == n, f'submission has {len(s)} rows, test has {n}'\n"
            "s[['target']].to_csv('/app/predictions.csv', index=False)\n"
            "print('predictions.csv', len(s), 'rows')\n"
            "PY"
        )
        await self.exec_as_agent(environment, command=finish)
