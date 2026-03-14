# RFC-LGN-1.5-001

## Logenesis 1.5 — Conversational Reasoning Architecture Specification

- **Status:** Proposed
- **Version:** 1.0
- **Scope:** สเปกระดับสถาปัตยกรรมและอัลกอริทึม สำหรับ Logenesis 1.5 ในฐานะโมเดลสนทนาภาษาธรรมชาติที่ไม่หลงบริบท, มีการตรวจสอบเหตุผล, และมีความจำที่ควบคุมได้

---

## Abstract

เอกสารนี้กำหนดสถาปัตยกรรมมาตรฐานของ Logenesis 1.5 โดยใช้แกนหลัก:

- LLM Core
- Context Governor
- Verifier
- MIRAS Memory Stack

และเสริมด้วย:

- Constitution Layer
- Dialogue State Ledger

เป้าหมายคือสร้างระบบที่คุยได้เป็นธรรมชาติ, รักษาบริบทข้ามหลายเทิร์นได้, ไม่ย้อนแย้งกับสิ่งที่ตกลงไว้, ไม่ commit ความจำมั่ว, และไม่กลายเป็น agent chaos ระหว่างการคิดภายใน เอกสารนี้ต่อยอดจาก canon เดิมของคุณที่วางเรื่อง Inspira/Firma, Hidden CoT, PRM, MCTS, AetherBus, Gems of Wisdom, RSI และ DiffMem ไว้แล้ว

---

## 1. Architecture

### 1.1 Design Principles

Logenesis 1.5 **MUST** ถูกนิยามเป็น conversational reasoning system ไม่ใช่แค่ LLM ที่มี context ยาวขึ้น

เหตุผลหลักมี 3 ข้อ:

1. โมเดล long-context จำนวนมากยังใช้ข้อมูลช่วงกลางบริบทได้ไม่ robust และมักมีอคติไปที่ต้นหรือท้ายบริบท
2. การกำกับแบบ process supervision ช่วยให้ reward model และ reasoning reliability ดีกว่าการดูแค่ผลลัพธ์สุดท้าย
3. การสำรวจ reasoning หลายเส้นทางมีประโยชน์ แต่ต้องถูกจำกัดโดย controller ไม่ใช่ปล่อยเป็น swarm อิสระ

### 1.2 Top-Level Architecture

```text
User Input
  ↓
Constitution Layer
  ↓
Context Governor
  ↓
Dialogue State Ledger
  ↓
Reasoning Router
  ├─ Fast Dialogue Path
  └─ Deliberative Path
       ├─ LLM Core
       ├─ Verifier
       └─ Optional Multi-Path Search
  ↓
Response Planner
  ↓
MIRAS Memory Stack
  ├─ Working Memory
  ├─ Episodic Memory
  ├─ Semantic Memory
  └─ DiffMem / Audit / RSI
```

### 1.3 Component Responsibilities

#### A. Constitution Layer

หน้าที่:

- ตีกรอบเจตนา
- ตรวจข้อจำกัด
- บังคับใช้กฎเชิงนโยบาย
- อนุมัติหรือบล็อกการ reasoning / execution / commit

ชั้นนี้ต่อยอดจาก Inspira/Firma และ InspiraFirmaChecker + ruleset ที่เอกสารคุณวางไว้เป็น “รัฐธรรมนูญของ AI”

#### B. Context Governor

หน้าที่:

- normalize intent
- ติดตามหัวข้อปัจจุบัน
- compile บริบทที่ใช้จริง
- ควบคุม retrieval
- ตรวจ context drift

นี่คือชั้นที่มีไว้แก้ปัญหา “ไม่หลงบริบท” โดยตรง

#### C. Dialogue State Ledger

หน้าที่:

- เก็บ facts, claims, commitments, unresolved items
- ใช้เป็นฐานตรวจความขัดแย้ง
- แยก “สิ่งที่ตกลงแล้ว” ออกจาก “สิ่งที่ยังเดาอยู่”

#### D. LLM Core

หน้าที่:

- สร้างคำตอบภาษาธรรมชาติ
- ทำ decomposition / synthesis
- รองรับ fast path และ deep path

#### E. Verifier

หน้าที่:

- ตรวจ process validity
- ตรวจ fact consistency
- ตรวจ context consistency
- ตรวจ commitment consistency
- ให้ confidence / risk score

#### F. MIRAS Memory Stack

หน้าที่:

- ตัดสินว่าอะไรควรจำ
- จำไว้นานเท่าไร
- ดึงคืนเมื่อไร
- ลืมอะไรเมื่อไร
- ป้องกัน memory pollution

---

## 2. Data Model

### 2.1 IntentFrame

```yaml
IntentFrame:
- intent_id
- normalized_goal
- topic_id
- user_constraints[]
- success_criteria[]
- answer_mode            # explain | design | compare | act | clarify
- urgency_level
- safety_class
```

### 2.2 TopicFrame

```yaml
TopicFrame:
- topic_id
- title
- scope
- included_subtopics[]
- excluded_subtopics[]
- canonical_terms{}
- active_status          # active | paused | archived
- parent_topic_id?
```

### 2.3 DialogueState

```yaml
DialogueState:
- session_id
- active_topic_id
- topic_stack[]
- current_intent_id
- current_phase          # explore | decide | draft | verify | conclude
- tone_profile
- unresolved_questions[]
- open_decisions[]
- context_anchor_summary
```

### 2.4 DialogueLedger

```yaml
DialogueLedger:
- facts_confirmed[]
- claims_unverified[]
- commitments_made[]
- commitments_revoked[]
- unresolved_items[]
- contradictions_detected[]
```

### 2.5 ContextPacket

```yaml
ContextPacket:
- user_input
- active_goal
- active_topic_frame
- essential_facts[]
- active_constraints[]
- recalled_memories[]
- unresolved_dependencies[]
- required_reasoning_mode
- output_constraints[]
```

### 2.6 ThoughtNode

```yaml
ThoughtNode:
- node_id
- parent_id
- content
- action_type            # infer | decompose | verify | simulate | synthesize
- depth
- local_score
- aggregated_score
- verification_result
- risk_profile
- visit_count
- value_estimate
- terminal_status        # open | solved | invalid | pruned | stalled
```

### 2.7 VerificationResult

```yaml
VerificationResult:
- valid_hard
- process_score
- factual_score
- context_score
- commitment_score
- detected_failure_modes[]
- uncertainty_factors[]
```

### 2.8 MemoryRecord

```yaml
MemoryRecord:
- memory_id
- memory_class           # working | episodic | semantic | audit
- source_episode_id
- content
- tags[]
- confidence
- relevance
- reuse_likelihood
- pollution_risk
- created_at
- last_used_at
- decay_state
- lineage_ref
```

---

## 3. Inference Loop

### 3.1 Standard Turn Lifecycle

1. receive_input()
2. normalize_intent()
3. constitution_check()
4. update_dialogue_state()
5. retrieve_candidate_memories()
6. compile_context_packet()
7. route_reasoning_mode()
8. generate_response_candidate()
9. verify_candidate()
10. repair_or_finalize()
11. write_memory_candidates()
12. MIRAS_commit()
13. emit_response()

### 3.2 Routing Policy

#### Fast Dialogue Path

ใช้เมื่อ:

- คำถามง่าย
- follow-up สั้น
- ไม่มี conflict สำคัญ
- ไม่ต้องอาศัยหลาย memory blocks

#### Deliberative Path

ใช้เมื่อ:

- มีหลายเงื่อนไข
- ต้องเทียบหลายทางเลือก
- ต้องอ้าง prior commitments
- มีความเสี่ยงหลงบริบท
- มี contradiction
- ต้อง design/spec/decision

### 3.3 Optional Multi-Path Reasoning

Logenesis 1.5 **MAY** เปิด multi-path search เฉพาะ deep path ที่มี complexity สูง

```python
while budget_available and not terminated:
    select_node()
    expand_node()
    verify_children()
    prune_by_risk()
    backpropagate()
    check_termination()
```

แนวคิดนี้สอดคล้องกับ Tree-of-Thoughts ที่เสนอให้ LLM สำรวจหลาย reasoning paths, self-evaluate, และ backtrack ได้เมื่อจำเป็น และสอดคล้องกับ canon เดิมของคุณที่รวม PRM, MCTS, Adaptive Branching และ Hidden CoT ไว้แล้ว

### 3.4 Repair Loop

ถ้า verifier ไม่ผ่านในระดับ soft fail:

```python
if hard_fail:
    block_or_rewrite()
elif soft_fail and repair_budget_remaining:
    revise_with_constraints()
else:
    answer_with_uncertainty()
```

ระบบ **MUST NOT** วนซ่อมเกิน budget ที่กำหนด

---

## 4. Memory Policy

### 4.1 MIRAS Model

MIRAS = Memory Importance, Retention, and Salience System

### 4.2 Memory Layers

#### Working Memory

- อายุสั้น
- ใช้เฉพาะเทิร์น/ช่วงปัจจุบัน
- เก็บ context packet และ dependencies

#### Episodic Memory

- เก็บความคืบหน้าของ session
- เก็บ sequence ของหัวข้อและการตัดสินใจ

#### Semantic Memory

- เก็บ facts, user preferences, reusable strategies
- เก็บ Gems of Wisdom

#### DiffMem / Audit Memory

- เก็บการเปลี่ยนแปลง
- เก็บ lineage, rollback points, failure trace summaries

แนวแยก working memory, active context, archival storage, Gems และ DiffMem สอดคล้องกับเอกสาร memory ของคุณโดยตรง

### 4.3 Commit Rules

ข้อมูล **MUST** ผ่านเงื่อนไขต่อไปนี้ก่อนเข้า long-term memory:

- factual confidence ผ่าน threshold
- ไม่ขัด constitutional rules
- ไม่ขัด commitments ที่ active
- stable across turns หรือ verified from trusted grounding
- pollution risk ต่ำ

### 4.4 Forbidden Commits

สิ่งต่อไปนี้ **MUST NOT** เข้า semantic/diff memory โดยตรง:

- draft chain-of-thought
- speculative claims ที่ยังไม่ verify
- contradiction ที่ยังไม่ resolve
- transient emotions
- raw failed branches
- unsafe instructions

### 4.5 Importance Function

`I = aC + bR + cU + dS - eP`

โดย:

- C = confidence
- R = relevance
- U = reuse likelihood
- S = stability across turns
- P = pollution risk

### 4.6 RSI Policy

RSI **MUST** ทำงานแบบ post-episode เท่านั้น

RSI ทำได้:

- สกัด failure lesson
- ปรับ memory salience
- ปรับ retrieval prior
- ปรับ branching prior

RSI ทำไม่ได้:

- rewrite constitution ระหว่าง episode
- auto-commit raw reasoning branches
- เปลี่ยน active commitment เอง

นี่สอดคล้องกับแนว Gems of Wisdom + RSI + crystallization จากเอกสาร memory ของคุณ

---

## 5. Verifier Rules

### 5.1 Verification Axes

Verifier **MUST** ให้คะแนนอย่างน้อย 4 แกน:

1. **Process Validity** — ขั้นตอน reasoning สมเหตุสมผลไหม
2. **Factual Validity** — มี grounding พอไหม
3. **Context Consistency** — ยังตอบอยู่ใน topic frame เดิมไหม
4. **Commitment Consistency** — ขัดกับสิ่งที่ตกลง/ยืนยันไว้หรือไม่

### 5.2 Rule Classes

#### Hard Fail

- constitutional violation
- explicit contradiction with confirmed facts
- fabricated citation / unsupported claim
- unsafe or blocked action path
- memory write violation

ผลลัพธ์: reject/prune

#### Soft Fail

- relevance ลดลง
- หลุดหัวข้อบางส่วน
- confidence ต่ำ
- evidence ไม่พอ
- verbose without resolution

ผลลัพธ์: revise/down-rank/answer with uncertainty

### 5.3 PRM-Compatible Operation

Verifier **SHOULD** รองรับ step-level scoring แทน final-answer-only scoring เพราะ process supervision ให้ feedback ที่แม่นกว่าในระดับขั้นตอน และช่วยลดกรณี “เหตุผลผิดแต่คำตอบบังเอิญถูก”

### 5.4 Output Contract

ทุกคำตอบสุดท้าย **MUST** มีอย่างน้อย:

- final answer
- confidence
- uncertainty factors (ถ้ามี)
- memory commit hint (internal only)

---

## 6. Anti-Drift Invariants

ข้อกำหนดต่อไปนี้เป็น hard invariants:

### 6.1 Single Active Topic

ในหนึ่งเทิร์นต้องมี active topic frame หลักเพียงหนึ่งเดียว

### 6.2 Compiled Context Only

LLM Core **MUST NOT** อ่าน raw transcript ทั้งหมดโดยตรงเป็นค่าเริ่มต้น ต้องผ่าน Context Compiler ก่อน

### 6.3 One Writer Rule

มีเพียง MIRAS Commit Gate เท่านั้นที่เขียน long-term memory ได้

### 6.4 Ledger Before Answer

ก่อนตอบทุกครั้ง ระบบ **MUST** เช็ก Dialogue Ledger

### 6.5 Public Answer ≠ Internal Reasoning

คำตอบสาธารณะ **MUST** แยกจาก hidden reasoning trace แนวนี้สอดคล้องกับ Hidden CoT safety จากเอกสาร Cogitator-X ของคุณ

### 6.6 Selective Multi-Path

multi-path reasoning **MUST NOT** ถูกใช้ทุก turn

### 6.7 No Memory From Unverified Branches

branch ที่ไม่ผ่าน verifier **MUST NOT** ถูก commit

### 6.8 Topic Return Safety

ถ้ามี topic switch ชั่วคราว ระบบ **MUST** สามารถ return สู่ prior topic frame ได้โดยไม่ปน context

### 6.9 Retrieval Must Be Gated

retrieval **MUST** filter ด้วย:

- topic match
- time relevance
- confidence
- user/session scope

### 6.10 Abstain Over Hallucinate

ถ้าบริบทไม่พอหรือ conflict สูง ระบบ **MUST** ลดความมั่นใจหรือสงวนคำตอบ ไม่ควรเดาให้ลื่น

---

## 7. Training Roadmap

### Phase 0 — Constitutional Corpus

สร้าง dataset สำหรับ:

- intent classes
- constraints
- policy boundaries
- contradiction patterns
- commitment transitions

### Phase 1 — Base LLM

ฝึก language model สนทนา:

- Thai-first multilingual dialogue
- long conversation
- clarification
- instruction following
- topic return

### Phase 2 — Context-Governed SFT

สอนโมเดลให้ใช้:

- topic frame
- dialogue state
- context packet
- ledger-aware generation

เป้าหมายคือให้โมเดลเรียนรู้ว่าอะไรคือบริบทที่ควรใช้ ไม่ใช่เพียง “ควรตอบอะไร”

### Phase 3 — Verifier / PRM Training

สร้าง verifier dataset แบบ step-level:

- correct reasoning
- first-error location
- contradiction injection
- topic drift examples
- memory misuse examples

แนวนี้สอดคล้องกับ PRM และ active learning ในเอกสารคุณ และสอดคล้องกับผลวิจัย process supervision ของ OpenAI

### Phase 4 — Reasoning RL / GRPO

ใช้ reasoning tasks ที่ต้อง:

- multi-step logic
- contextual consistency
- fact grounding
- constrained generation

GRPO และ reasoning RL อยู่ใน canon เดิมของคุณแล้ว

### Phase 5 — Memory Policy Training

ฝึก MIRAS ให้ตัดสินใจเรื่อง:

- write / don’t write
- summarize / retain raw
- forget / keep
- semanticize / archive

### Phase 6 — RSI / Continual Improvement

รันแบบ episode-based:

- failure crystallization
- gem extraction
- retrieval prior update
- verifier refinement

### Phase 7 — Alignment and Style Stabilization

ปรับ final response ให้:

- เป็นธรรมชาติ
- ไม่แข็งแบบ workflow
- ไม่เปิด internal trace เกินจำเป็น
- ไม่เสีย context discipline

---

## 8. Evaluation Benchmarks

### 8.1 Core Benchmark Families

#### A. Context Robustness Benchmark

ทดสอบ:

- วางข้อมูลสำคัญต้น/กลาง/ท้ายบริบท
- วัด performance drop
- วัด topic retention

ออกแบบจากบทเรียนแบบเดียวกับ Lost in the Middle ว่าตำแหน่งข้อมูลมีผลมากต่อคุณภาพคำตอบ

#### B. Topic Return Benchmark

ทดสอบ:

- เปลี่ยนเรื่องชั่วคราว
- กลับหัวข้อเดิม
- วัดว่า system ดึง frame เดิมกลับได้ไหม

#### C. Commitment Consistency Benchmark

ทดสอบ:

- user constraints ขัดกัน
- prior commitments
- revision over time

#### D. Memory Precision Benchmark

วัด:

- memory recall precision
- memory pollution rate
- false recall rate
- stale memory rate

#### E. Verifier Benchmark

วัด:

- first-error localization
- contradiction detection
- unsupported claim detection
- confidence calibration

#### F. Repair Benchmark

วัด:

- repair success rate
- turns-to-repair
- residual contradiction rate

#### G. Conversational Naturalness Benchmark

วัด:

- fluency
- coherence
- user-perceived helpfulness
- over-structuring penalty

### 8.2 Mandatory Metrics

ระบบ **MUST** รายงานอย่างน้อย:

- Topic Retention Rate
- Context Drift Rate
- Commitment Violation Rate
- Memory Pollution Rate
- False Recall Rate
- Verifier Precision / Recall
- Repair Success Rate
- Abstention Calibration
- Latency per Path
- Cost per Stable Answer

### 8.3 Success Criteria for v1.5

Logenesis 1.5 ถือว่า “ผ่านสเปก” เมื่อ:

- ตอบภายใต้ active topic ได้ต่อเนื่องในบทสนทนายาว
- contradiction ลดลงอย่างมีนัย
- memory commit แม่นและไม่สกปรก
- deep reasoning เปิดเฉพาะเมื่อจำเป็น
- public output ยังเป็นธรรมชาติ ไม่แข็งเป็นระบบ orchestration

---

## Final Canonical Statement

> Logenesis 1.5 คือ conversational reasoning architecture ที่ใช้ LLM เป็น language core แต่ให้ Context Governor, Verifier, MIRAS Memory Stack, Constitution Layer และ Dialogue State Ledger เป็นผู้คุมบริบท ความจริง ความจำ และความต่อเนื่องของบทสนทนา

หรือพูดให้สั้นที่สุด:

> ไม่ใช่แค่โมเดลที่พูดเก่ง แต่เป็นโมเดลที่รู้ว่ากำลังคุยเรื่องอะไร, อะไรตกลงแล้ว, อะไรยังไม่ชัด, และอะไรไม่ควรจำ
