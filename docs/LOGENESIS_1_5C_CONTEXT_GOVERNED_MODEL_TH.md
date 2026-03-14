# Logenesis 1.5-C

## Context-Governed Natural Language Conversational Model

เอกสารนี้นิยาม Logenesis 1.5-C ในฐานะสถาปัตยกรรมสนทนาภาษาธรรมชาติที่เน้น **คุมบริบท, ตรวจเหตุผล, และบริหารความจำแบบมีนโยบาย** โดยวาง LLM เป็น executor และให้ Logenesis เป็น control kernel / stateful reasoning layer

---

## 1) นิยามรุ่น 1.5-C

Logenesis 1.5-C ประกอบด้วย 4 ชั้นหลักที่ทำงานร่วมกัน:

1. **Language Core** — โมเดลภาษาที่สร้างคำตอบ
2. **Context Governor** — คุมบริบทไม่ให้หลุดประเด็น
3. **Reasoning Verifier** — ตรวจความสอดคล้องของขั้นตอนคิดก่อนตอบ
4. **Memory System (MIRAS + RSI)** — จัดการความจำข้ามเทิร์น/ข้ามเซสชัน

สรุปสั้น:
- LLM ทำหน้าที่ “พูด”
- Logenesis ทำหน้าที่ “จำว่าเราคุยอะไรอยู่” และ “คุมว่าอะไรควรถูกใช้ในการตอบ”

---

## 2) ความสามารถหลักที่ต้องมีพร้อมกัน

### 2.1 สนทนาภาษาธรรมชาติจริง
ตอบได้ลื่นไหล ไม่แข็งเป็น workflow

### 2.2 ไม่หลงบริบท
ระบบต้องติดตาม:
- ตอนนี้คุยเรื่องอะไร
- ผู้ใช้ต้องการอะไร
- มีข้อจำกัดอะไร
- อะไรตกลงไปแล้ว/ยังไม่ตกลง

### 2.3 แยก Active Context ออกจาก Accumulated Data
ไม่ยัดทุกอย่างเข้า context window เดียว

### 2.4 มีเหตุผลก่อนตอบ
ใช้ process-aware verification ไม่พึ่ง outcome-only checking

### 2.5 ความจำต้องคัดกรองก่อน commit
ลด memory pollution โดยเก็บเฉพาะสิ่งที่ผ่านนโยบาย

---

## 3) ภาพรวมสถาปัตยกรรม

```text
User Input
   ↓
Perception & Intent Parser
   ↓
Context Governor
   ├─ Conversation State Tracker
   ├─ Topic Frame Manager
   ├─ Fact & Commitment Ledger
   └─ Context Compiler
   ↓
Reasoning Router
   ├─ Fast Response Path
   └─ Deep Reasoning Path
        ├─ Generator
        ├─ Verifier
        ├─ Multi-path Search (optional)
        └─ Contradiction Check
   ↓
Response Planner
   ↓
Language Core
   ↓
Post-Response Audit
   ↓
MIRAS Memory Commit
```

---

## 4) แกน Context Governor สำหรับ anti-drift

### 4.1 Conversation State Tracker
ต้องเก็บสถานะเชิงโครงสร้าง ไม่ใช่ transcript ดิบอย่างเดียว:

```yaml
ConversationState:
  session_goal:
  current_topic:
  subtopic_stack:
  unresolved_questions:
  user_constraints:
  accepted_facts:
  disputed_facts:
  style_preferences:
  emotional_tone:
  next_expected_action:
```

### 4.2 Topic Frame Manager
ทุกหัวข้อมี frame ของตัวเอง (เป้าหมาย, ขอบเขต, สิ่งตัดออก, สมมติฐาน) และรองรับ push/pop เมื่อเปลี่ยนหัวข้อชั่วคราว

### 4.3 Fact & Commitment Ledger
แยกเก็บเป็น:
- **Facts**: ยืนยันแล้ว
- **Claims**: ยังไม่ยืนยัน
- **Commitments**: สิ่งที่ระบบตกลงไว้

ก่อนตอบทุกครั้งต้องสแกนว่า output ใหม่ขัดกับ ledger เดิมหรือไม่

### 4.4 Context Compiler
ทุกเทิร์นสร้าง `ContextPacket` แทนการส่ง transcript ทั้งหมด:

```yaml
ContextPacket:
  user_intent_now:
  active_topic_frame:
  must_remember_facts:
  unresolved_items:
  last_turn_dependency:
  memory_recalls:
  reasoning_mode:
  response_constraints:
```

ผลลัพธ์ที่คาดหวัง: ลด lost-in-the-middle, ลด token waste, และลด recall ผิดชิ้น

---

## 5) Memory Architecture ที่แนะนำ

### Layer A — Working Memory
เฉพาะสิ่งจำเป็นต่อเทิร์นปัจจุบัน (อายุสั้น)

### Layer B — Episodic Memory
เก็บเป็น “ตอน” ของบทสนทนาเพื่อ recall ย้อนเป็น episode

### Layer C — Semantic Memory / Gems of Wisdom
เก็บความรู้ที่ตกผลึกและเสถียรผ่าน validator

### Layer D — DiffMem / Audit Memory
เก็บ versioned summary, policy change log, lesson history

---

## 6) MIRAS สำหรับ conversational model

MIRAS = **Memory Importance, Retention, and Salience System**

หน้าที่หลัก:
- ตัดสินว่าอะไรควรจำ
- ควรอยู่นานแค่ไหน
- ควรถูกดึงเมื่อไร
- ควรถูกลืมเมื่อไร
- อะไรห้ามจำถาวร

### 6.1 Commit rules
**จำได้**: facts ยืนยันแล้ว, user preferences เสถียร, reusable reasoning patterns, validated failure lessons, long-term project state

**ห้ามจำถาวร**: temporary guesses, hallucinated details, emotional spikes ชั่วคราว, draft branches, statements กำกวมที่ยังไม่ confirm

### 6.2 Importance score

```text
I = aF + bR + cU + dS - eP
F = factual confidence
R = relevance to user/project
U = reuse likelihood
S = stability across turns
P = pollution risk
```

ถ้าไม่ถึง threshold ห้าม commit เข้า long-term memory

---

## 7) Reasoning policy สำหรับงานสนทนา

### 7.1 Two-path routing
- **Fast Path**: คำถามทั่วไป/small talk/follow-up ง่าย
- **Deep Path**: ปัญหาซับซ้อน หลายข้อจำกัด เสี่ยงหลงบริบท หรือต้องตัดสินใจเชิงสถาปัตยกรรม

### 7.2 Selective multi-path
ใช้เฉพาะโจทย์ยาก จำกัด depth/width และห้าม reasoning branch แตะ memory ถาวรโดยตรง

### 7.3 Verifier checks (ก่อนตอบ)
1. factual consistency
2. context consistency
3. commitment consistency
4. user-intent consistency

---

## 8) Anti-context-drift mechanisms

1. **Topic-lock**: ทุกคำตอบต้องยึด active frame ชัดเจน
2. **Contradiction scanner**: ตรวจชนกับ prior facts/commitments/constraints
3. **Context anchoring**: ทุก 3–5 turns สร้าง anchor summary สั้น
4. **State-gated retrieval**: ดึง memory ด้วย state filter (topic, intent class, time relevance, identity, confidence)
5. **Confidence-gated answer**: ถ้าบริบทไม่พอ ให้ระบุ uncertainty และตอบเฉพาะส่วนที่เสถียร

---

## 9) Language Core ที่เหมาะสม

### 9.1 Base model
- decoder-only
- multilingual (Thai-friendly)
- instruction-tuned สำหรับ dialogue
- long-context capable (แต่ไม่พึ่ง long context อย่างเดียว)

### 9.2 Auxiliary heads
- Intent head
- Context stability head
- Memory write head
- Verifier/PRM head

---

## 10) Training blueprint

1. **Phase 1**: Base language pretraining
2. **Phase 2**: Context-grounded SFT
3. **Phase 3**: Process supervision (step-level)
4. **Phase 4**: Context persistence training (long & multi-session)
5. **Phase 5**: Memory policy training (MIRAS)
6. **Phase 6**: RSI after deployment (post-episode only)

ข้อกำกับ RSI:
- ทำได้: สกัดบทเรียน, ปรับ salience, ปรับ branch priors, ปรับ compiler heuristics
- ห้าม: rewrite constitutional rules สด ๆ, commit raw chain-of-thought, เปลี่ยน persona/core commitments เอง

---

## 11) Inference policy ต่อหนึ่งข้อความเข้า

1. สร้าง IntentFrame
2. อัปเดต ConversationState
3. ทำ gated retrieval
4. สร้าง ContextPacket
5. เลือก Fast หรือ Deep Path
6. ให้ verifier ตรวจ consistency
7. ตอบเป็นภาษาธรรมชาติ
8. สรุปสิ่งที่ควรจำและส่งเข้า MIRAS commit gate

---

## 12) พฤติกรรมเป้าหมาย

- คุยยาวแล้วไม่หลงโจทย์หลัก
- เปลี่ยนเรื่องชั่วคราวและกลับมาทำต่อได้
- ตรวจพบความย้อนแย้งกับสิ่งที่เคยตกลง
- ไม่มั่นใจเกินจริงเมื่อข้อมูลเก่าไม่ชัด

---

## 13) ข้อห้ามเชิงสถาปัตยกรรม

- ห้ามทำให้ระบบกลายเป็น agent chaos ที่คิดทุกอย่างเอง
- ห้ามยัด transcript ทั้งหมดเข้า context ตรง ๆ
- ห้าม commit memory แบบไม่คัดกรอง
- ห้ามเผย reasoning tree ภายในทุกเทิร์น

---

## 14) Executive summary

Logenesis 1.5-C ควรนิยามเป็น:

> **LLM + Context Governor + Verifier + MIRAS Memory Stack**

เพื่อให้ได้โมเดลสนทนาที่เป็นธรรมชาติ, ไม่หลงบริบท, ตรวจความสอดคล้องก่อนตอบ, และบริหารความจำระยะยาวอย่างปลอดมลพิษ
