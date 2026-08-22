# Stage 12 — Real Integration & Deployment
- Production configuration validation
- `/ready` dependency readiness
- Explicit Tool Registry
- Real M-One HTTP adapter
- Agent → Tool Registry → M-One path
- Automatic Alembic migration at startup
- Production Docker startup
- External integration test gate
- Production smoke test

Required secrets:
`DATABASE_URL`, `REDIS_URL`, `AI_API_KEY`, `MONE_API_URL`, `MONE_API_TOKEN`, `ALLOWED_ORIGINS`.

Release order:
1. PostgreSQL
2. Redis
3. secrets
4. backend deploy
5. `/health`
6. `/ready`
7. pytest
8. Playwright staging
9. WebRTC
10. M-One read tool
11. confirmation tool
12. RBAC isolation
13. reconnect/resume
14. production promotion

External tests run only with `RUN_EXTERNAL_INTEGRATION=1`.
