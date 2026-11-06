# SPEC: settings

## 1. Cell Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Cell ID** | `settings` |
| **Cell Classification** | `domain` |
| **Contract Path** | `contracts/settings_contract.py` |
| **Transitive Contract Deps** | none |
| **Committed Artifact Path** | `dist/settings/` |
| **Max Implementation Size** | 350 LOC / 4,500 tokens |
| **Permitted External Deps** | `pydantic` |

## 2. Responsibility & Boundary Scope
- **Primary Function:** Convert an injected environment mapping into a validated, immutable `Settings`.
- **Inbound Boundary:** `Mapping[str, str]`.
- **Outbound Boundary:** `Settings`, or `ValueError` for malformed integers.

## 3. Core Invariants
1. Same mapping produces equal `Settings`.
2. The input mapping is never mutated.
3. No `os.environ`, `os.getenv`, file I/O, or network I/O.
4. `gcs_bucket` never starts with `gs://`.
5. `port` is 1..65535; `idle_timeout_seconds` is 1..1200.

## 4. Edge-Case & Failure Resolution Matrix
| Condition | Behavior | Emitted |
| :--- | :--- | :--- |
| Empty mapping | Apply defaults | `Settings()` |
| `GCS_BUCKET=gs://x` | Reject at validation | `ValidationError` |
| `COMFYUI_PORT=abc` | Reject before model construction | `ValueError` |
| `COMFYUI_PORT=0` | Reject at validation | `ValidationError` |
| `require_bucket()` on empty | Reject | `ValueError` |

## 5. Performance & Complexity Ceilings
- O(1) time and space; < 1 ms p99.

## 6. Explicit Anti-Goals
- **DO NOT** read environment variables.
- **DO NOT** import `dist.*`.
- **DO NOT** catch generic exceptions silently.
