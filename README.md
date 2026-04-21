# Logenesis 1.5

Logenesis 1.5 คือ reference implementation ของสถาปัตยกรรม conversational reasoning ตาม RFC-LGN-1.5-001 โดยเน้นการแยก public response ออกจาก reasoning ภายใน และมี memory commit gate สำหรับความปลอดภัยเชิงระบบ

## Core Pipeline

`User Input -> Constitution -> Context Governor -> Dialogue Ledger -> Reasoning Router -> (Fast|Deliberative) -> Response Planner -> MIRAS Memory Stack`

## โครงสร้างโค้ด (Codebase Structure)

```text
.
├── src/logenesis/
│   ├── api/                 # FastAPI contract + server endpoint
│   ├── runtime/             # Turn orchestrator
│   ├── constitution/        # Policy/rule checking
│   ├── context_governor/    # Drift detection + retrieval gating
│   ├── router/              # Reasoning route selection
│   ├── reasoning/           # Deliberative reasoning components
│   ├── response/            # Public response planner
│   ├── memory/              # MIRAS/episodic/semantic memory logic
│   ├── ledger/              # Dialogue ledger state
│   ├── verifier/            # Verification modules
│   ├── platform/            # Storage/analytics/commit gate infra
│   ├── agents/              # Agent modules
│   └── schemas/             # Pydantic models
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration scenarios
│   └── benchmark/           # Throughput benchmarking scripts
├── config/                  # Runtime policy/routing/memory configs
├── docs/                    # Architecture, flows, RFC, decisions
├── examples/                # Example usage flows
└── .github/workflows/       # CI/CD workflows
```

## เริ่มต้นใช้งาน (Quick Start)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## คำสั่งหลักที่ใช้กับโปรเจกต์

### Run tests

```bash
pytest -q
```

### Run API server

```bash
uvicorn logenesis.api.server:app --reload
```

จากนั้นเรียก endpoint:

- `POST /v1/conversation/turn`

## CI/CD Workflows ที่ปรับปรุงแล้ว

มีการจัดโครงสร้าง workflow ใหม่ให้สอดคล้องกับฐานโค้ด Python ปัจจุบัน:

1. **CI (`.github/workflows/ci.yml`)**
   - ทดสอบบน Python 3.10 / 3.11 / 3.12
   - ติดตั้งแพ็กเกจแบบ editable พร้อม dev dependencies
   - รัน `pytest -q`

2. **Package Validation (`.github/workflows/package.yml`)**
   - ตรวจสอบว่าสามารถ build distribution ได้จริงด้วย `python -m build`

3. **Runtime Smoke Check (`.github/workflows/smoke.yml`)**
   - ตรวจสอบ import สำคัญและ run `TurnOrchestrator` แบบ lightweight

## ขอบเขตและข้อจำกัด

- โปรเจกต์นี้เป็น reference implementation และมี mock/stub provider บางส่วน
- ยังไม่ได้รวม training pipeline ขนาด production cluster
- เหมาะสำหรับใช้เป็นฐานต่อยอดด้านสถาปัตยกรรม, governance, และ deterministic testing
