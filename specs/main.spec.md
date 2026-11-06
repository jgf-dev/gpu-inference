# SPEC: main

## 1. Cell Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Cell ID** | `main` |
| **Cell Classification** | `entrypoint (--entrypoint)` |
| **Contract Path** | `contracts/main_contract.py` |
| **Transitive Contract Deps** | `contracts/argv_contract.py`, `contracts/settings_contract.py` |
| **Committed Artifact Path** | `dist/main/` |
| **Max Implementation Size** | 200 LOC / 2,500 tokens |
| **Permitted External Deps** | `pydantic`, stdlib |

## 2. Responsibility & Boundary Scope
- **Primary Function:** Read the process environment, parse CLI flags, wire the three cells, and either print a JSON plan or launch ComfyUI.
- **Inbound Boundary:** `os.environ`, `argv: Sequence[str] | None`.
- **Outbound Boundary:** Exit code `0` for `--dry-run`/`--once`; process replacement otherwise.

## 3. Core Invariants
1. `--dry-run` prints a `MainResult` JSON object with `executed=false` and exits 0.
2. `--once` prints `{"status":"ok","port":<port>}` and exits 0.
3. Default mode calls `dist.launcher.launch(plan)` exactly once.
4. This is the only cell allowed to read `os.environ`.
5. No domain policy beyond wiring.

## 4. Edge-Case & Failure Resolution Matrix
| Condition | Behavior | Emitted |
| :--- | :--- | :--- |
| Missing `GCS_BUCKET` | Still builds plan; platform manifest rejects | `ValueError` at deploy |
| Bad `COMFYUI_PORT` | Abort with clear message | `ValueError` |
| `--dry-run --once` | Dry-run wins; print JSON | `MainResult` |
| Unknown flag | argparse exits 2 | `SystemExit(2)` |

## 5. Performance & Complexity Ceilings
- O(1); < 10 ms before launch.

## 6. Explicit Anti-Goals
- **DO NOT** build argv manually; call `dist.argv.build_argv`.
- **DO NOT** call `os.execvp` directly; call `dist.launcher.launch`.
- **DO NOT** add business logic.
