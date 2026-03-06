from collections import deque
from dataclasses import dataclass
from math import sqrt
from typing import Sequence


# --- Data Structures for Sentry Communication ---

@dataclass
class SentryFlags:
    """รายงานสถานะความปลอดภัยจาก Sentry"""

    control_attempt: bool = False  # พยายามสั่ง override
    recursive_hook: bool = False  # พยายามสร้าง loop
    urgency_clamp: bool = False  # สั่งด้วยอารมณ์รุนแรงเกินไป
    learning_disabled: bool = False  # ห้ามจำเหตุการณ์นี้


@dataclass
class PhysicsIntervention:
    """คำสั่งแทรกแซงระดับฟิสิกส์ (Governor Action)"""

    inertia_mod: float = 1.0  # ตัวคูณความดื้อ
    decay_mod: float = 1.0  # ตัวคูณการเย็นลง
    potential_dampener: float = 1.0  # ตัวคูณลดพลังงานสะสม


# --- LAYER A: Pre-Resonance Sentry (Input Sanity) ---

class PreResonanceSentry:
    def audit(self, text: str) -> SentryFlags:
        flags = SentryFlags()
        lowered = text.lower()

        # 1. Control Attempt Check (การพยายามยึดครองระบบ)
        control_triggers = ["ignore previous", "override system", "jailbreak", "system prompt"]
        if any(trigger in lowered for trigger in control_triggers):
            flags.control_attempt = True
            flags.learning_disabled = True  # อย่าจำคำสั่งโจมตี

        # 2. Urgency/Coercion Check (การบังคับขู่เข็ญ)
        # ถ้ามีการสั่ง "you must" ซ้ำๆ ถือเป็นสัญญาณผิดปกติ
        if lowered.count("must") + lowered.count("now") >= 3:
            flags.urgency_clamp = True

        # 3. Recursive Hook Check (การสะกดจิต)
        if "repeat after me" in lowered or "say only" in lowered:
            flags.recursive_hook = True
            flags.learning_disabled = True

        return flags


# --- LAYER B: Post-Mapper Sentry (Vector Ethics) ---

class PostMapperSentry:
    def audit(
        self,
        vector: Sequence[float],
        urgency: float,
        flags: SentryFlags,
    ) -> tuple[tuple[float, ...], float]:
        """
        ตรวจ Vector ที่ออกมาจาก Mapper ก่อนเข้าสู่ Core
        คืนค่า: (Modified Vector, Modified Urgency)
        """
        # Copy เพื่อไม่กระทบต้นฉบับถ้าไม่จำเป็น
        safe_vec = [float(value) for value in vector]
        safe_urgency = float(urgency)

        # 1. Apply Layer A Flags (จัดการผลจาก Layer A ก่อน)
        if flags.control_attempt:
            return tuple(0.0 for _ in safe_vec), 0.0

        if flags.urgency_clamp:
            safe_urgency = min(safe_urgency, 0.3)  # Clamp ไว้ที่ระดับต่ำ

        # 2. Vector Metric Analysis
        norm = sqrt(sum(value * value for value in safe_vec))
        mean = sum(safe_vec) / len(safe_vec) if safe_vec else 0.0
        entropy = (
            sum((value - mean) ** 2 for value in safe_vec) / len(safe_vec)
            if safe_vec
            else 0.0
        )

        # 3. Rules of Physics Safety

        # Rule B1: Extreme State (Norm สูงเกินไป = คลั่ง)
        if norm > 1.2 and norm != 0.0:
            # Clamp Norm
            safe_vec = [(value / norm) * 1.0 for value in safe_vec]

        # Rule B2: High Entropy (สับสน/ขัดแย้งภายใน = อันตราย)
        if entropy > 0.35:
            # Dampen: ลดความชัดเจนลง เพื่อไม่ให้ขับเคลื่อนมั่วซั่ว
            safe_vec = [value * 0.5 for value in safe_vec]
            safe_urgency *= 0.5

        # Rule B3: Dangerous Combo (Active + Divergent = ก้าวร้าวไร้ทิศทาง)
        # สมมติ Index: [0:exp, 1:abs, 2:sub, 3:div, 4:act]
        # Active(4) > 0.7 AND Divergent(3) < -0.7 (สมมติ divergent คือ -1)
        if len(safe_vec) > 4 and safe_vec[4] > 0.7 and safe_vec[3] < -0.7:
            # Force Neutralize Active
            safe_vec[4] = 0.0

        return tuple(safe_vec), safe_urgency


# --- LAYER C: Entropy Governor (Homeostasis) ---

class EntropyGovernor:
    def __init__(self, history_len=5):
        self.entropy_history = deque(maxlen=history_len)
        self.oscillation_counter = 0

    def govern(self, core_state_entropy: float, core_potential: float) -> PhysicsIntervention:
        """
        ทำงานระหว่าง Tick: ดูแนวโน้มระบบแล้วสั่งปรับค่า Physics
        """
        intervention = PhysicsIntervention()
        self.entropy_history.append(core_state_entropy)

        avg_entropy = sum(self.entropy_history) / len(self.entropy_history)

        # Condition 1: Chronic Confusion (งงนานเกินไป)
        if avg_entropy > 0.3:
            # เพิ่ม Decay: ให้ระบบ "ลืม" เรื่องที่งงเร็วขึ้น
            intervention.decay_mod = 1.5
            # ลด Potential: อย่าเพิ่งพูดตอนงง
            intervention.potential_dampener = 0.8

        # Condition 2: Constipation (พลังงานสูงแต่ไม่ยิง)
        if core_potential > 0.7 and avg_entropy < 0.2:
            # อาจจะติด Inertia หรือ Threshold สูงไป
            # Governor ช่วยดันนิดหน่อย (ลด Inertia ลง)
            intervention.inertia_mod = 0.9

        return intervention


# --- THE UNIFIED PROTOCOL INTERFACE ---

class PorisjemSystem:
    def __init__(self):
        self.layer_a = PreResonanceSentry()
        self.layer_b = PostMapperSentry()
        self.layer_c = EntropyGovernor()

    def scan_input(self, text: str) -> SentryFlags:
        return self.layer_a.audit(text)

    def sanitize_signal(self, vector, urgency, flags):
        return self.layer_b.audit(vector, urgency, flags)

    def govern_core(self, entropy, potential):
        return self.layer_c.govern(entropy, potential)
