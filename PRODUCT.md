# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The primary user is a low-literacy citizen who needs to apply for a relief payment by voice on a phone with a weak connection. They cannot reliably read forms, are targeted by fake "relief payment" messages, and need the system to explain itself in plain language and in Urdu.

Secondary roles in the same workflow:

- **Community helper** — acts on behalf of up to 40 families, one family at a time, with per-family consent that the citizen can withdraw.
- **Department officer** — the human who must approve any case before payment is released; the AI never releases payment.
- **Admin** — publishes immutable rule versions and can simulate rule changes against past cases.
- **Auditor** — reads decision traces and consent events.

Demo accounts for every role are seeded locally (`fatima@mock.local`, `helper@mock.local`, `officer@mock.local`, `admin@mock.local`, `auditor@mock.local`, plus a second tenant for isolation tests); password `Demo@123` for all.

## Product Purpose

A working, runnable prototype for the AI Hackathon evaluation that helps a citizen get a relief decision even with low literacy, weak connectivity, and scam targeting. It decides, explains, says "I am not sure" and hands the case to a human. Success is an honest end-to-end demonstration that the hard parts are solved in the *system* — users, roles, tenants, cases, rules, consent and audit trails — not in a chatbot facade.

The artifact is a prototype and evaluation exhibit, not a service intended for real disbursement. No real personal data, identity records, payments, messages, or government connections are used anywhere.

## Positioning

"AI on public rails": a deterministic, local, inspectable decision system rather than an opaque chatbot. Its distinguishing mechanism is that a versioned, cost-aware rules engine and local classifiers route and score every case, but every result carries a plain-language reason, an Urdu reason, a complete decision trace (input hash, rule version, model versions, confidence, checks), and a mandatory human approval gate. Consent and RBAC are enforced server-side, so taking back consent stops helper access on the very next request. Low confidence produces `human_review` or `needs_info` with reasons — never a silent guess and never an automatic payment.

Identity verification, data exchange, and payment disbursement are explicitly mocked and marked `mock: true` in every response; this honesty is part of the product claim, not a hidden compromise.

## Operating Context

- Urdu-first browser experience (`<html lang="ur" dir="rtl">`) with an English toggle; voice input and text-to-speech via the browser Web Speech API (Urdu locale; support varies by browser, text input is always available).
- Big icon-first, touch-friendly controls for low-literacy phone use; saved progress in `localStorage`; offline requests queued locally and replayed through an idempotent `/api/sync` keyed by `client_id` + `op_id`.
- A persistent prototype banner states that this is NOT an official service and all data is mocked.
- One-click role logins let an evaluator move between distinct citizen, helper, officer, admin, and auditor views. Each role sees its own Home workspace with server-backed data; the server remains the only authority for role and consent decisions.
- Rules are changed at runtime by an admin (immutable versions, active version applied immediately, old cases retain their `rule_set_id`), and proposed rules can be replayed against historical cases with the Digital Twin simulation before adoption.
- Local dev: `python -m uvicorn app.main:app --reload --port 8000`; the web app is at `/`, Swagger UI at `/docs`, health at `/health`. SQLite database with Alembic migrations; config via `DATABASE_URL`.

## Capabilities and Constraints

- **Real and working:** FastAPI REST API, JWT login, server-side RBAC/consent, SQLite + Alembic migrations; versioned rules engine (wrong approval = 100 units, wrong rejection = 10, manual review = 1; thresholds auto ≥ 0.90, ask-info ≥ 0.65, scam block ≥ 0.85); Jev-style classifier, TF-IDF RAG with citations, structured Pydantic outputs, guardrails, anomaly detection, agent orchestration, mock computer vision (OCR/QR/forgery), decision traces and audit endpoints.
- **Real but browser-dependent:** Web Speech API voice input and TTS in Urdu; text path always works.
- **Mock by design:** identity verification, data exchange, payment disbursement; policy documents, citizens and evaluation labels are bundled fixtures; notifications and webhooks are recorded locally, with webhook delivery attempted at a 1s timeout and failures recorded rather than retried.
- **Bonus capabilities:** Digital Twin rule simulation; Helper Mode with 40 mock families and per-family consent; offline-first sync; scam map by district, label and day; evaluation dashboard (`/api/evaluation/summary`).
- **Hard product rule:** no fabricated real data, testimonials, customers, benchmarks, licensing, or deployment claims. Nothing here may be presented as connected to NADRA, Raast, or any government system.
- **Honest limits to preserve:** local heuristics are transparent but not a trained ML system; confidence is calibrated for demonstration, not production; SQLite is a zero-setup demo (SQLAlchemy layer can point at Postgres via `DATABASE_URL`); webhooks are not retried.
- **Quality bar:** 62 tests cover auth/RBAC, case lifecycle, consent take-back, rule versioning, bad data, classifier routing and false alarms, multi-tenancy, API keys/scopes/rate limiting, offline sync, accessibility, safety gates, explainability and migrations.

## Brand Commitments

- Name: **Last Mile**; full prototype title "Last Mile — AI on Public Rails (PROTOTYPE)".
- The prototype/mock-only notice must be visible in the product, not buried in docs.
- Voice is plain-language, honest about uncertainty, and explicitly non-official; the citizen is always told a human checks the case before any payment.
- Bilingual Urdu/English is a binding product commitment, as is the "not an official service, all data mocked" framing across UI and docs.

## Evidence on Hand

- `README.md` — authoritative product summary, demo script, eight technical challenges, honest limits, and test coverage.
- `AI_Hackathon_Problem_Statement.pdf` and `AI_Hackathon_Evaluation_Rubrics.pdf` — the evaluation source documents at the project root (this subagent's model cannot parse PDF input, so their contents were not ingested; treat them as unread evidence, not a source of invented claims).
- `app/data/rules_docs/` — bundled mock policy documents: `relief_eligibility_policy.md`, `complaint_procedure.md`, `scam_advisory.md`, `scam_advisory_ur.md`, `cnic_verification_guide.md`.
- `app/static/` — the incumbent voice-first web UI (HTML, CSS, JS) with bilingual i18n strings.
- `tests/` — 62 passing tests as described in the README; `/api/evaluation/summary` exposes the cost/threshold numbers.
- No real user research, testimonials, customers, production benchmarks, or external model/API credentials are on hand; none may be fabricated.

## Product Principles

1. **A human always decides money.** Approval by a department officer is mandatory; the AI never releases a payment.
2. **Uncertainty is a feature.** Low confidence routes to `human_review` or `needs_info` with concrete reasons instead of a guess.
3. **Every decision explains itself.** Plain-language and Urdu reasons plus a full trace with rule and model versions; audits are first-class.
4. **Consent is real and revocable.** Grants and withdrawals are enforced server-side on the next request and recorded in the audit trail.
5. **Honesty over polish.** Mock and prototype status is stated everywhere; weak data produces safe `needs_info` outcomes, and no government affiliation is implied.

## Accessibility & Inclusion

- Designed first for low-literacy users: icon-first controls, large touch targets, minimal reading, and spoken prompts and status.
- Urdu is the default language with an English toggle; all UI copy, reasons, and error messages are localized in both languages.
- Voice input is optional, never mandatory: text input, typed questions, and read-aloud controls provide equivalent paths; browser voice support is disclosed when unavailable.
- Weak connectivity is an expected condition, not an error: requests save on the device with clear "offline — saved" status and sync when the network returns.
- The incumbent implementation supports reduced-motion preferences and accessible names/roles; preserve these in any future interface work.
