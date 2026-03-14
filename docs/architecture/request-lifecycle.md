# Request Lifecycle (Per Turn)

1. **Receive Input**
   - API receives `ConversationTurnRequest`.
2. **Constitution Gate**
   - `ConstitutionEngine` evaluates blocked content and execution permissions.
3. **Intent + Topic Update**
   - Intent normalization and topic frame update (switch/return supported).
4. **Context Compilation**
   - Compile bounded `ContextPacket` from ledger, topic, and approved memory retrieval.
5. **Ledger Update**
   - Register claims/commitments/unresolved items from user turn.
6. **Routing Decision**
   - Router selects fast or deliberative path via policy thresholds.
7. **Reasoning Path Execution**
   - Fast path: direct model call + minimal verification.
   - Deliberative path: model, verifiers, optional bounded multi-path search.
8. **Verification Aggregate**
   - Scoring aggregator computes confidence + abstain trigger.
9. **Response Planning**
   - Build user-facing answer; strip/withhold hidden internal traces.
10. **Memory Commit Evaluation**
   - MIRAS commit gate checks verification + constitution + policy.
11. **Emit Response**
   - Return answer, path metadata, and abstain status.
