# Stage 11 — Full Production Integration Checklist

## Automated
- [x] Python syntax
- [x] Agent runtime policy boundary
- [x] RBAC + confirmation
- [x] Redis resume cursor
- [x] Confirmation token one-time use
- [x] PostgreSQL conversation repository contracts
- [x] Playwright E2E scaffold
- [x] Docker Compose PostgreSQL + Redis

## Before public release
- [ ] Put real PostgreSQL URL in Render
- [ ] Put real Redis URL in Render
- [ ] Put AI_API_KEY only in backend secrets
- [ ] Put MONE_API_TOKEN only in backend secrets
- [ ] Set exact ALLOWED_ORIGINS
- [ ] Run `alembic upgrade head`
- [ ] Run backend pytest
- [ ] Run frontend Playwright against staging
- [ ] Test microphone permission
- [ ] Test Realtime SDP/WebRTC
- [ ] Test tool.call → M-One → tool.result
- [ ] Test confirmation approval
- [ ] Test reconnect/resume
- [ ] Test workshop isolation with two users
- [ ] Test attachment upload limits
- [ ] Test backup/restore
- [ ] Run load test
- [ ] Enable alerting
- [ ] Rotate any development secrets

## Important
The repository now contains the integration contracts and test harness. External provider calls remain disabled until real credentials/services are supplied.
