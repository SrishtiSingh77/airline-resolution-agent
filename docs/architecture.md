# Architecture

## The one idea worth understanding

The language layer and the decision layer are separate, and only the decision layer is
trusted. A message is parsed into an intent, the policy engine evaluates that intent against
static rules in Python, and the response is phrased from the structured result. The phrasing
layer can describe a decision; it can never make one, widen one, or invent a fact to support
one.

That is what makes the behaviour reproducible: the same request against the same booking
produces the same decision on every run, and `pytest` can assert on it.

## Request flow

```
Browser (React)
   │  POST /api/chat { booking_reference, message }
   ▼
FastAPI router  ── app/api/chat.py
   │
   ▼
Agent service  ── app/services/agent.py          orchestration only
   │
   ├─▶ Intent parser ── app/utils/intent_parser.py
   │      deterministic keyword/pattern matching → Intent enum
   │
   ├─▶ Policy engine ── app/services/policy_engine.py
   │      pure functions over static data → PolicyDecision
   │      { eligible, action, reason, requires_escalation, escalation_reason }
   │
   ├─▶ Action service ── app/services/action_service.py
   │      executes ONLY allowed actions, writes the audit log
   │
   └─▶ Escalation service ── app/services/escalation_service.py
          builds the escalation record when the decision demands it
   │
   ▼
ChatResponse { message, intent, policy_decision, actions, escalation }
   │
   ▼
Browser renders chat bubble + resolution panel + audit trail
```

The action service refuses any action type that is not in the allowed list, so a bug in the
phrasing layer cannot produce an unauthorised action. A prohibited request is recorded as
`status: not_authorized` with `requires_escalation: true` — it is logged, not performed.

## Layers

**Data** (`app/data/`) — the customers, bookings and policy text from the brief, as module
constants. Read-only. Three customers, three bookings, one operating day.

**Models** (`app/models/`) — Pydantic models for `Customer`, `Booking`, `PolicyDecision`,
`ActionLog` and the chat request/response. These are the contract the frontend types mirror.

**Policy engine** (`app/services/policy_engine.py`) — pure functions with no I/O and no
randomness: `calculate_delay_benefits`, `get_cancellation_options`,
`check_refund_eligibility`, `check_loyalty_benefits`, `evaluate_request`,
`determine_escalation`. Each returns a structured decision with the rule that produced it.

**Action service** — simulates execution and appends to the session audit log. Actions are
simulated because there is no airline backend; the simulation never fabricates operational
detail such as a flight number or seat.

**Escalation service** — turns a decision that requires escalation into a record carrying the
reason, the requested action, the policy limitation and the booking reference.

**API** (`app/api/`) — thin routers. Customers, bookings and flights are looked up by booking
reference, which doubles as the session identity for the demo.

## Frontend

React + TypeScript + Vite, Tailwind for styling, Lucide for icons. Three panes: case list,
conversation, resolution details.

State lives in `App.tsx` and is keyed by booking reference, so switching scenarios preserves
each conversation. The API client (`src/api/client.ts`) normalises one thing — an action's
name may arrive as `type` or `action` — and otherwise passes the backend response through
untouched. Components render only what the response contains; when a field is absent the UI
shows an empty state rather than a guess.

Quick-test prompt chips call `POST /api/chat` exactly like typed input. There are no canned
frontend replies, so what a reviewer sees is the real decision path.

Vite proxies `/api` to `http://127.0.0.1:8000`, which keeps the frontend origin-relative and
avoids needing CORS configuration for the demo.

## Session state

The audit log and escalation records live in memory for the life of the server process,
scoped by booking reference. `POST /api/reset` clears them. There is no database, no auth and
no external service, which keeps the project to two commands to run.

## Deliberate omissions

No LLM call is required for the app to work. If a generative phrasing layer were added, it
would receive the already-decided `PolicyDecision` and be constrained to describing it —
eligibility would still be computed in Python.

No persistence, no user accounts, no real payment or inventory integration. The booking
reference is treated as the authenticated identity for the demo, and every read is scoped to
it, which is what prevents cross-customer data access.