# API Contracts

## POST /v1/conversation/turn

Request:
```json
{
  "conversation_id": "conv-123",
  "text": "switch topic: architecture",
  "metadata": {}
}
```

Response:
```json
{
  "conversation_id": "conv-123",
  "answer": "...",
  "route": "fast",
  "abstain": false,
  "verification_score": 0.82
}
```
