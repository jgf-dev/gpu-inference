# SPEC: argv

## 1. Cell Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Cell ID** | `argv` |
| **Cell Classification** | `domain` |
| **Contract Path** | `contracts/argv_contract.py` |
| **Transitive Contract Deps** | `contracts/settings_contract.py` |
| **Committed Artifact Path** | `dist/argv/` |
| **Max Implementation Size** | 350 LOC / 4,500 tokens |
| **Permitted External Deps** | `pydantic` |

## 2. Responsibility & Boundary Scope
- **Primary Function:** Render the exact ComfyUI command-line arguments from a `Settings`.
- **Inbound Boundary:** `Settings`, optional `port`, optional `output_dir`.
- **Outbound Boundary:** `list[str]` suitable for `python main.py <argv>`.

## 3. Core Invariants
1. `--disable-mmap` is always present.
2. `--listen 0.0.0.0` is always present.
3. `--port` is followed by the decimal port.
4. `--output-directory` is followed by the resolved output path.
5. No environment reads and no process execution.

## 4. Edge-Case & Failure Resolution Matrix
| Condition | Behavior | Emitted |
| :--- | :--- | :--- |
| `port=None` | Use `settings.port` | argv |
| `output_dir=None` | Use `settings.output_dir` | argv |
| `port` outside 1..65535 | `Settings` validation rejects first | `ValidationError` |
| `Path` output | Stringify with `str()` | argv |

## 5. Performance & Complexity Ceilings
- O(1); < 1 ms p99.

## 6. Explicit Anti-Goals
- **DO NOT** launch a process.
- **DO NOT** read environment variables.
- **DO NOT** duplicate defaults from `Settings`.
