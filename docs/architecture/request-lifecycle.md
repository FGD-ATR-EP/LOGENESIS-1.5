# Request Lifecycle (Per Turn)

1. **Receive Input**
   - API receives `ConversationTurnRequest`.
2. **Constitution Gate**
   - `ConstitutionEngine` evaluates blocked content and execution permissions.
3. **Intent + Topic Update**
   - Intent normalization and topic frame update (switch/return + contradiction-aware safety).
4. **Retrieval Gate Query**
   - Retrieval is filtered by topic/time/confidence/session scope.
5. **Context Compilation**
   - Compile bounded `ContextPacket` from ledger, topic, anchor summary, and approved retrieval.
6. **Ledger Update**
   - Register claims/commitments/unresolved items and contradiction cues.
7. **Routing Decision**
   - Router selects fast or deliberative path via policy thresholds.
8. **Reasoning Path Execution**
   - Fast path: direct model call + verification.
   - Deliberative path: model + optional bounded multi-path search controller.
9. **Verification Aggregate**
   - Weighted scoring with hard-fail/soft-fail and uncertainty factors.
10. **Response Planning**
   - Build user-facing answer from verified state only; strip internal-trace markers.
11. **Memory Candidate + Commit Evaluation**
   - MIRAS candidate generation + commit gate checks verification/stability/policy.
12. **MIRAS Updates**
   - Working + episodic updates each turn, semantic commit only when approved, DiffMem lineage record.
13. **RSI Timing**
   - RSI summaries are post-episode only and skipped during active turns.
14. **Emit Response**
   - Return answer, route, confidence, abstain, and uncertainty metadata.
