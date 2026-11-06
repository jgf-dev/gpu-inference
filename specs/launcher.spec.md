# SPEC: launcher

## 1. Cell Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Cell ID** | `launcher` |
| **Cell Classification** | `adapter (--adapter)` |
| **Contract Path** | `contracts/launcher_contract.py` |
| **Transitive Contract Deps** | `contracts/argv_contract.py`, `contracts/settings_contract.py` |
| **Committed Artifact Path** | `dist/launcher/` |
| **Max Implementation Size** | 150 LOC / 2,000 tokens |
| **Permitted External Deps** | stdlib only |

## 2. Responsibility & Boundary Scope
- **Primary Function:** Change directory and replace the current process with ComfyUI.
- **Inbound Boundary:** `LaunchPlan`, injected `exec_fn: ExecFn`, `chdir_fn: ChdirFn`.
- **Outbound Boundary:** Never returns on success; propagates `OSError`/`FileNotFoundError`.

## 3. Core Invariants
1. `chdir_fn` is called exactly once before `exec_fn`.
2. `exec_fn` receives `sys.executable` and `["<python>", "main.py", *plan.argv]`.
3. The argv list is forwarded without reordering or rewriting.
4. No environment reads, no policy, no sibling `dist.*` imports.

## 4. Edge-Case & Failure Resolution Matrix
| Condition | Behavior | Emitted |
| :--- | :--- | :--- |
| `chdir` fails | Abort before exec | `OSError` |
| `exec` fails | Abort | `OSError` |
| Empty argv | Contract rejects at construction | `ValidationError` |

## 5. Performance & Complexity Ceilings
- O(1); no buffering; < 1 ms before exec.

## 6. Explicit Anti-Goals
- **DO NOT** inspect `os.environ`.
- **DO NOT** decide GPU, paths, or flags.
- **DO NOT** swallow `OSError`.
