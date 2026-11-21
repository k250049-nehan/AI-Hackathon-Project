# Last Mile — AI on Public Rails (PROTOTYPE)

> **PROTOTYPE — NOT AN OFFICIAL SERVICE.** All citizens, CNICs, identity records,
> payments, messages and policy documents are **mock/simulated**. No real personal
> data is used anywhere. Nothing here is connected to NADRA, Raast, or any
> government system.

## The task we finished end-to-end

> **We help a low-literacy citizen (or a community helper acting for one of 40
> families) apply for a relief payment even though they cannot read forms, have a
> weak connection, and are targeted by fake "relief payment" messages.**

The platform decides, explains, protects, says *"I am not sure"*, and hands the
case to a human. It is not a chatbot: it has users, roles, tenants, cases, rules,
consent and audit trails.

## Real vs simulated

| Layer | Status |
|---|---|
| FastAPI REST API, JWT login, server-side RBAC/consent, SQLite + Alembic migrations | **Real, working** |
| Versioned rules engine, Jev-style classifier, TF-IDF RAG, structured validation, anomaly detection, guardrails, agent orchestration | **Real, local, deterministic** (no external model/API) |
| Browser speech-to-text / text-to-speech | **Real browser Web Speech API** (Urdu locale; browser support varies) |
| Identity verification, data exchange, payment disbursement | **Mock services** (`mock: true` in every response) |
| Policy documents, citizens, evaluation labels | **Bundled mock fixtures** |
| Notifications and webhooks | Recorded locally; webhook delivery attempted with a 1s timeout |

## Quick start

```powershell
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Apply migrations (optional: startup also creates tables)
$env:DATABASE_URL = "sqlite:///./data/lastmile.db"
python -c "from alembic.config import Config; from alembic import command; command.upgrade(Config('alembic.ini'), 'head')"

# 3. Run the server (auto-seeds mock users, rules and demo cases)
python -m uvicorn app.main:app --reload --port 8000
```

Open:

- **Web app:** <http://127.0.0.1:8000/>
- **Swagger UI:** <http://127.0.0.1:8000/docs>
- **Health check:** <http://127.0.0.1:8000/health>

## Vercel deployment

The FastAPI app is deployed as a single Vercel Function using Vercel's native
FastAPI support (no Mangum adapter needed):

- **Live app:** <https://last-mile-prototype.vercel.app/>
- **Swagger UI:** <https://last-mile-prototype.vercel.app/docs>
- **Health check:** <https://last-mile-prototype.vercel.app/health>

Deploy or redeploy from this directory:

```powershell
python -m pip install uv                       # required by Vercel's local Python build
npx vercel deploy --prod --yes --project last-mile-prototype
```

`pyproject.toml` declares the entrypoint (`app.main:app`), Python 3.14 and the
runtime dependencies; `vercel.json` sets the function timeout to 60s. Vercel
SSO protection was intentionally disabled so judges can open the demo without
signing in.

**Serverless data caveat:** Vercel's filesystem is read-only except `/tmp`, so
`app/config.py` points SQLite at `/tmp/lastmile-data/lastmile.db` when the
`VERCEL` env var is present. Each cold start re-seeds the mock users, rules and
demo cases; changes made during a demo last only for the lifetime of that warm
function instance. For durable state, set `DATABASE_URL` to a hosted Postgres
connection string in the Vercel project settings — the SQLAlchemy layer already
supports it.

### Demo accounts

Password for every account: `Demo@123`

| Role | Email |
|---|---|
| Citizen (widow, low literacy) | `fatima@mock.local` |
| Citizen (second person) | `ahmed@mock.local` |
| Community helper | `helper@mock.local` |
| Department officer | `officer@mock.local` |
| Admin | `admin@mock.local` |
| Auditor | `auditor@mock.local` |
| Second tenant (isolation tests) | `zainab@mock.local`, `helper2@mock.local`, `officer2@mock.local` |

The UI has one-click role buttons, and each role opens a different Home workspace: citizen intake, helper families, officer review queue, admin rules, or auditor trail. Role and consent are still enforced server-side. The language toggle uses a drawn globe icon (Urdu default).

Citizen intake is voice-led: the microphone is the primary action and the seven labelled claim fields (full name, CNIC, district, category, monthly income, claim amount, optional dependents) stay visible as a clearly secondary panel next to the citizen's own request box. Speech fills the request box and every labelled field it can recognize. Spoken CNICs and amounts work in English or Urdu: Arabic-Indic (`١٢٣٤٥`) and Persian (`۱۲۳۴۵`) digits are normalised before extraction, so `12345-6789012-3`, `١٢٣٤٥-٦٧٨٩٠١٢-٣`, and `۱۲۳۴۵-۶۷۸۹۰۱۲-۳` all fill CNIC. The everyday Urdu word `رہائش` fills district just like `ضلع` or `district`. The Urdu typed example is a complete, natural mock sentence that fills every field without mixing in broken English fragments. When the citizen presses the red Stop button, the app asks by name and voice for the first required field still missing; answering that specific question fills only its field and leaves the original request text untouched. It repeats until every required field is valid, then points the citizen to Send. Fields the citizen has edited are never overwritten, and Send is blocked with inline errors until validation passes. The explicit `claim_data` travels with the transcript to `/api/ai/voice/intake` (and offline `voice_intake` replay), where the server validates it with `ClaimForm` before the shared `create_case()` decision path. Legacy transcript-only requests still work. The case is created only when the citizen presses Send; Send also stops the microphone immediately so late speech cannot change submitted text.

## Live demo script (curl)

```powershell
# Login
$body = @{email='fatima@mock.local'; password='Demo@123'} | ConvertTo-Json
$token = (Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/login -Method Post -Body $body -ContentType 'application/json').access_token
$h = @{Authorization = "Bearer $token"}

# 1. Voice/text intake — creates a case with an explanation and rule version
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/ai/voice/intake -Method Post -Headers $h -ContentType 'application/json' -Body (@{transcript='I need a relief payment'; language='ur'; claim_data=@{full_name='Fatima Bibi'; cnic='12345-1234567-1'; district='Karachi'; category='widow'; monthly_income=12000; claim_amount=5000; dependents=3}} | ConvertTo-Json)

# 2. Fake relief message — classified and blocked with confidence
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/ai/classify -Method Post -Headers $h -ContentType 'application/json' -Body (@{text='Congratulations! Relief payment ready. Click https://bit.ly/x and send OTP urgently.'} | ConvertTo-Json)

# 3. Rules answer with sources (RAG)
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/ai/rag -Method Post -Headers $h -ContentType 'application/json' -Body (@{question='What is the income limit?'} | ConvertTo-Json)

# 4. Consent take-back — helper access stops on the very next call
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/consent/withdraw -Method Post -Headers $h -ContentType 'application/json' -Body (@{subject_user_id='user_citizen_fatima'; purpose='relief_claim_assist'; grantee_user_id='user_helper_sana'} | ConvertTo-Json)
```

Then sign in as `helper@mock.local` and try to create a case for Fatima: the
API returns **403 consent_required**. The withdrawal is in `/api/audit/consent-events`.

```powershell
# 5. Admin changes a rule — no code change, no redeploy
$a = (Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/login -Method Post -Body (@{email='admin@mock.local';password='Demo@123'} | ConvertTo-Json) -ContentType 'application/json').access_token
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/rules -Method Post -Headers @{Authorization="Bearer $a"} -ContentType 'application/json' -Body (@{definition=@{max_income=8000}; change_note='tightened rule'} | ConvertTo-Json)
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/rules/active -Headers @{Authorization="Bearer $a"}

# 6. Digital Twin — replay past cases against a proposed rule without changing live rules
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/rules/digital-twin/simulate -Method Post -Headers @{Authorization="Bearer $a"} -ContentType 'application/json' -Body (@{definition=@{max_income=8000}} | ConvertTo-Json)

# 7. Public API key
$key = (Invoke-RestMethod -Uri http://127.0.0.1:8000/api/admin/api-keys -Method Post -Headers @{Authorization="Bearer $a"} -ContentType 'application/json' -Body (@{name='judge'; scopes=@('cases:read','cases:write','ai:infer')} | ConvertTo-Json)).plain_key
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/public/whoami -Headers @{'X-API-Key'=$key}
```

Everything on **server-side** is enforced for raw API calls; there are no
client-only checks.

## How the eight technical challenges are handled

| # | Challenge | Implementation |
|---|---|---|
| 01 | Cost of being wrong | Wrong approval = 100 units, wrong rejection = 10, manual review = 1. AI never releases payment; officer approval is mandatory. Thresholds: auto ≥ 0.90, ask-info ≥ 0.65, scam block ≥ 0.85. Numbers on `/api/evaluation/summary`. |
| 02 | "I am not sure" | Low confidence → `human_review` / `needs_info` with reasons attached in `decision_trace` and a plain-language prompt. |
| 03 | Bad data | CNIC normalisation, Muhammad/Mohammad/Muhammed aliases, missing fields → `needs_info` instead of a crash, duplicate/anomaly flags instead of silent approval. |
| 04 | Rules that change | Admin publishes immutable rule versions; new cases use the active version immediately; old cases keep their `rule_set_id`. Digital Twin replays past cases against a proposal. |
| 05 | Explain and audit | Every decision has a simple reason, an Urdu reason, and a full trace (input hash, rule version, model versions, confidence, checks). `/api/audit/ai-decisions`. |
| 06 | Consent and take-back | `/api/consent/mine`, grant/withdraw/correct. Withdrawal is enforced on the server on the next request and audited. |
| 07 | Works for everyone | Browser voice input + TTS, Urdu/English toggle, big icon-first UI, saved progress in `localStorage`, idempotent `/api/sync`. |
| 08 | Scams and fake docs | Multi-signal scam scoring (single-signal mentions are *not* blocked), mock OCR/QR/forgery analysis, honest false-alarm counts and a scam map. |

## AI features implemented

Jev-style classification & routing · RAG with source citations · autonomous agent
with tool calling · structured outputs (Pydantic) · guardrails + human approval ·
two-view explainability · anomaly detection · mock computer vision (OCR/QR/forgery) ·
conversation/progress memory in the database · evaluation dashboard.

## Bonus features implemented

Digital Twin rule simulation · Helper Mode (40 mock families, per-family consent) ·
Offline-First Sync (idempotent by `client_id` + `op_id`) · Scam Map (by district,
label and day).

## Tests

```powershell
python -m pytest tests -q
```

69 tests cover auth/RBAC, case lifecycle, consent take-back, rule versioning,
bad data, classifier routing and false alarms, multi-tenancy, API keys/scopes/
rate limiting, offline sync, accessibility, safety gates, explainability and
Alembic migrations.

## Project layout

```
app/
  main.py            FastAPI app, middleware, error handlers, OpenAPI, static UI
  config.py db.py models.py schemas.py security.py errors.py
  normalization.py   defensive name/CNIC handling
  audit.py consent.py
  ai/                jev, rag, agent, explain, guardrails, structured, anomaly, vision
  rules/engine.py    versioned cost-aware eligibility rules
  services/          mock identity/data/payment, cases, notifications, webhooks, evaluation
  api/               auth, cases, rules, consent, audit, admin, ai, public, sync, eval, mock
  data/              mock policy docs + deterministic seed
  static/            low-literacy voice-first UI
migrations/versions/ Alembic initial schema
tests/               69 passing tests
```

## Known limits (honest)

- Local heuristic models are transparent but not a trained ML system; confidence
  is calibrated for demonstration, not production.
- Browser voice support depends on the browser (Chromium works best); text input
  is always available. Microsoft Edge may report a `network` speech error for an
  Urdu locale even with working internet. The app retries `ur-PK`, `ur`, and
  `ur-IN`, then says plainly that Urdu recognition is unavailable in that browser
  rather than blaming the connection; it never transcribes Urdu with English.
- Webhooks are attempted but a failed delivery is recorded rather than retried.
- SQLite is used for a zero-setup demo; the SQLAlchemy layer can point at Postgres
  via `DATABASE_URL`.
- On Vercel the SQLite demo database lives in `/tmp`, so writes are per warm
  function instance and reset on a cold start. Set `DATABASE_URL` to a hosted
  Postgres URL for persistence.
