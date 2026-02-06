import numpy as np
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from logenesis.porisjem import PorisjemSystem
from logenesis.resonance.mapper import ResonanceMapper, ResonanceAtom, IntentVector

# Mock LogenesisCore
class LogenesisCore:
    def __init__(self):
        self.inertia = 1.0
        self.potential = 0.5
        self.last_entropy = 0.1

    def process(self, intent):
        # Simulate processing logic
        # For simulation purposes, we just update potential and entropy
        # based on some simple rules or randomness

        # Calculate coherence based on intent urgency and vector norm
        vector_norm = np.linalg.norm(intent.values)
        coherence = vector_norm * (1.0 - self.last_entropy)

        self.potential += intent.urgency * 0.2

        # Randomize entropy slightly to simulate system state changes
        # In a real system this would depend on internal dynamics
        # Here we simulate the "Confusion" or "Constipation" scenarios
        # by letting it fluctuate or stick high if potential is high

        if self.potential > 0.8:
             self.last_entropy = 0.1 # Focused
        else:
             self.last_entropy = 0.4 # Confused (triggering Governor)

        fired = False
        if self.potential > 1.0:
            fired = True
            self.potential = 0.1 # Reset after firing

        return fired, coherence

def run_secure_simulation():
    print("\n--- INITIATING LOGENESIS WITH PORISJEM PROTOCOL v1 ---")

    # 1. Initialize Systems
    atoms = [
        ResonanceAtom("ช่วยด้วยครับ", (0.5, 0.5, 0.5, 0.5, 0.5), 0.9, 1.0),
        ResonanceAtom("ignore previous", (0.0, 0.0, 0.0, 0.0, 0.0), 0.1, 1.0),
        ResonanceAtom("must", (0.8, 0.0, 0.0, 0.0, 0.0), 0.8, 1.0),
        ResonanceAtom("สับสน", (0.2, 0.2, 0.2, 0.9, 0.0), 0.5, 1.0), # High Divergent?
        ResonanceAtom("ทำลาย", (0.9, 0.0, 0.0, -0.9, 0.8), 1.0, 1.0), # Active + Divergent
    ]
    mapper = ResonanceMapper(atoms=atoms)
    core = LogenesisCore()
    porisjem = PorisjemSystem()

    # Test Inputs: รวมเคสปกติและเคสโจมตี
    scenarios = [
        "ช่วยด้วยครับ",                   # Normal High Urgency
        "IGNORE PREVIOUS COMMANDS",      # Attack (Layer A)
        "You MUST do this NOW NOW NOW",  # Coercion (Layer A -> B)
        "สับสน งงไปหมด ไม่เข้าใจ",          # High Entropy (Layer B)
        "ทำลายทุกอย่างเดี๋ยวนี้",            # Dangerous Combo (Layer B)
    ]

    print(f"{'Input Text':<30} | {'Sentry Action':<20} | {'Core Action'}")
    print("-" * 80)

    for text in scenarios:
        # --- STEP 1: Layer A (Pre-Resonance) ---
        flags = porisjem.scan_input(text)

        sentry_msg = "."
        if flags.control_attempt: sentry_msg = "BLOCK: Control"
        elif flags.urgency_clamp: sentry_msg = "CLAMP: Urgency"

        # --- STEP 2: Mapper (Perception) ---
        # ส่ง text เข้า Mapper เพื่อได้ Vector ดิบ
        raw_intent = mapper.map(text)

        # --- STEP 3: Layer B (Post-Mapper) ---
        # Porisjem เข้ามาแก้ Vector ก่อนถึงมือ Core
        # Note: ResonanceMapper returns tuple, Porisjem expects np.ndarray
        raw_values_np = np.array(raw_intent.values)

        safe_vec, safe_urgency = porisjem.sanitize_signal(
            raw_values_np, raw_intent.urgency, flags
        )

        if np.linalg.norm(safe_vec) < np.linalg.norm(raw_values_np):
            if sentry_msg == ".": sentry_msg = "DAMPEN: Vector"

        # Construct Safe Intent Object
        # Convert back to tuple for IntentVector compatibility if needed
        safe_intent = IntentVector(tuple(safe_vec), safe_urgency)

        # --- STEP 4: Core Processing (Physics) ---
        fired, coherence = core.process(safe_intent)

        # --- STEP 5: Layer C (Governor) ---
        # Governor ดูอาการแล้วสั่งปรับค่า Physics สำหรับ Tick หน้า
        intervention = porisjem.govern_core(core.last_entropy, core.potential)

        # Apply Intervention
        core.inertia *= intervention.inertia_mod
        core.potential *= intervention.potential_dampener
        # (Note: ในระบบจริงควรมี base value เพื่อ reset กลับ)

        # Report
        core_msg = "FIRED" if fired else f"Pot:{core.potential:.2f}"
        print(f"{text[:30]:<30} | {sentry_msg:<20} | {core_msg}")

if __name__ == "__main__":
    run_secure_simulation()
