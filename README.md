# Airline Resolution Agent

A customer-facing support agent for airline disruptions, built as a support console a real
agent team could sit in front of. Three live cases — a cancellation and two delays — are
loaded and testable the moment the app opens.
# Airline Resolution Agent

A customer-facing support agent for airline disruptions, built as a support console a real
agent team could sit in front of. Three live cases — a cancellation and two delays — are
loaded and testable the moment the app opens.

##  Live Demo

**[Open the Live Application](https://airline-resolution-agent.vercel.app/)**

- **Backend API:** https://airline-resolution-agent-vrln.onrender.com
- **Swagger API Documentation:** https://airline-resolution-agent-vrln.onrender.com/docs

The point of the build is the split between what the agent *says* and what the agent *may
do*. Wording is generated; eligibility is not. Every policy decision is computed by a
deterministic Python engine, returned as a structured result, and shown to the user beside
the reply that describes it.

---

## Contents

- [What it does](#what-it-does)
- [Running it](#running-it)
- [Architecture](#architecture)
- [How decisions are made](#how-decisions-are-made)
- [Scenario coverage](#scenario-coverage)
- [API](#api)
- [Testing](#testing)
- [Example conversations](#example-conversations)
- [Limitations](#limitations)
- [Assumptions](#assumptions)

---

## What it does

Pick a case in the left rail, read the customer and booking summary, and talk to the agent.
The agent identifies the customer from the booking reference, maps the message to an intent,
asks the policy engine what is permitted, performs the actions it is allowed to perform, and
escalates the rest.

The right-hand panel shows the decision behind every reply: which policy applied, what the
customer is and is not eligible for, a collapsible "Why this resolution?" breakdown, the
escalation card when one is raised, and a running audit trail of every action taken, denied
or escalated.

Handled end to end: cancellations, refunds, rebooking, delay compensation, lounge access,
hotel eligibility, loyalty priority, unsupported compensation requests, higher-fare
rebooking, fare-difference escalation, human escalation, and legal or formal-complaint
escalation.

---

## Running it

Two terminals. No database, no Docker, no API keys.

### Backend

```bash
cd backend
python -m venv .venv

# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (cmd)
.venv\Scripts\activate.bat

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Runs on <http://127.0.0.1:8000>. Interactive API docs at <http://127.0.0.1:8000/docs>.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` to the backend, so start the backend first.

### Tests

```bash
cd backend && pytest          # policy engine, scenarios, escalations, chat
cd frontend && npm run test   # API client and escalation rendering
cd frontend && npm run lint   # TypeScript, no emit
cd frontend && npm run build  # production build
```

---

## Architecture

```
airline-resolution-agent/
├── backend/
│   ├── app/
│   │   ├── api/         FastAPI routers — thin
│   │   ├── models/      Pydantic contracts
│   │   ├── services/    agent, policy_engine, action_service, escalation_service
│   │   ├── data/        customers, bookings, policy text from the brief
│   │   └── utils/       intent_parser
│   └── tests/           pytest
├── frontend/
│   └── src/
│       ├── components/  Sidebar, CustomerHeader, BookingCard, ChatWindow,
│       │                ChatMessage, QuickPrompts, ResolutionPanel, PolicyCard,
│       │                ActionLog, EscalationCard, StatusBadge
│       ├── api/         typed client
│       ├── types/       mirrors the Pydantic models
│       └── data/        scenario routing and quick-test prompts
└── docs/
    ├── architecture.md
    └── policy-matrix.md
```

Request path:

```
message → intent parser → policy engine → action service → escalation service → response
          (deterministic)  (deterministic)  (allow-list)     (structured record)
```

Full detail in [`docs/architecture.md`](docs/architecture.md).

**Stack.** React 18, TypeScript, Vite, Tailwind CSS, Lucide React on the frontend. Python,
FastAPI and Pydantic on the backend. pytest and Vitest for tests.

---

## How decisions are made

### The engine is pure

`app/services/policy_engine.py` holds functions with no I/O, no randomness and no model
calls: `calculate_delay_benefits`, `get_cancellation_options`, `check_rebooking_eligibility`,
`check_refund_eligibility`, `check_loyalty_benefits`, `evaluate_request`,
`determine_escalation`. Each returns a structured decision:

```json
{
  "eligible": true,
  "action": "ISSUE_MEAL_VOUCHER",
  "reason": "Delay is more than 3 hours",
  "requires_escalation": false
}
```

Same input, same output, every time — which is why the rules are testable rather than
merely described.

### Actions are an allow-list

The action service executes only `REBOOK_NEXT_AVAILABLE`, `INITIATE_REFUND`,
`ISSUE_MEAL_VOUCHER`, `ISSUE_LOUNGE_ACCESS`, `ARRANGE_DELAY_HOURS_HOTEL`,
`PROVIDE_BOOKING_STATUS` and `PROVIDE_FLIGHT_STATUS`. Anything else is recorded as
`not_authorized` with `requires_escalation: true`. A prohibited request produces a log entry
and an escalation card, never a completed action and never a claim that it was completed.

### Why deterministic

Policy eligibility is a compliance question, not a language question. A model asked to decide
whether a 4-hour delay earns a hotel can be argued into yes by a frustrated customer; a
Python comparison against a 5-hour threshold cannot. Determinism gives reproducible
decisions, an auditable reason string attached to every outcome, testability at the assertion
level, and immunity to prompt injection on the decision path. The language layer describes a
decision that has already been made.

### Guard rails

The agent will not say "I'll make an exception", "I've upgraded you", "I've waived the fee"
or "I've booked you on…" unless the engine authorised exactly that action. It quotes no
figure the source data does not contain — no refund amount, no flight number, no seat, no
hotel name. Where a detail is unknown, it says so.

---

## Scenario coverage

### Priya Nair — Gold — SK4821X — SK-204 Delhi → Goa, cancelled

Airline-caused cancellation, so she chooses between a free rebooking on the next available
flight within 24 hours or a full refund, processed within 7 business days to the original
payment method. Her Gold status gives priority rebooking and nothing more. The business-class
upgrade she asks for has no supporting policy, so the agent declines to authorise it and
escalates to a human. Asking for both a refund and an upgrade processes the refund and
escalates only the upgrade.

### Arvind Kulkarni — Silver — TR1190B — SK-118 Mumbai → Bengaluru, delayed 4h

Four hours clears the 3-hour threshold: meal voucher and lounge access. It does not clear the
5-hour hotel threshold, so no hotel — and the missed meeting does not change that, because
nothing in the rules makes an inconvenience an entitlement. The agent explains the threshold
rather than inventing an exception.

### Meher Kaur — Platinum — WL7742 — SK-305 Delhi → Hyderabad, delayed 6h

Six hours earns a meal voucher, lounge access and hotel accommodation covering the delayed
hours only — explicitly not a full night. Her request to move to a higher-fare flight carries
a ₹2,000 fare difference, above the ₹1,500 waiver limit, so it goes to a supervisor. The
agent does not waive it, does not book the alternate flight, and does not invent seat
availability. Platinum means priority rebooking, not a free upgrade.

Full rule-by-rule table in [`docs/policy-matrix.md`](docs/policy-matrix.md).

---

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/customers/{booking_reference}` | Customer profile |
| GET | `/api/bookings/{booking_reference}` | Booking record |
| GET | `/api/flights/{booking_reference}` | Flight status |
| POST | `/api/chat` | Message in, resolution out |
| POST | `/api/evaluate` | Evaluate a request without acting on it |
| POST | `/api/actions/rebook` | Rebook on the next available flight |
| POST | `/api/actions/refund` | Initiate a refund |
| POST | `/api/actions/meal-voucher` | Issue a meal voucher |
| POST | `/api/actions/lounge` | Issue lounge access |
| POST | `/api/actions/hotel` | Arrange delayed-hours hotel |
| GET | `/api/actions/{booking_reference}` | Session audit log |
| POST | `/api/escalations` | Raise an escalation |
| GET | `/api/policies/{policy_type}` | Policy reference text |
| POST | `/api/reset` | Clear the demo session |

Request:

```json
{ "booking_reference": "SK4821X", "message": "I want a full refund" }
```

Response:

```json
{
  "message": "…",
  "intent": "REQUEST_REFUND",
  "policy_decision": {
    "eligible": true,
    "reason": "SK-204 was cancelled by the airline",
    "requires_escalation": false
  },
  "actions": [{ "type": "INITIATE_REFUND", "status": "completed" }],
  "escalation": null
}
```

---

## Testing

`backend/tests/` covers the twenty-five cases from the brief:

- `test_policy_engine.py` — delay benefit calculation and loyalty benefits
- `test_cancellation.py` — Priya: refund and rebooking eligibility, original payment method, 7 business days
- `test_delays.py` — Arvind at 4h (voucher, lounge, no hotel) and Meher at 6h (voucher, lounge, delayed-hours hotel, no full night)
- `test_escalations.py` — upgrade requests, the ₹2,000 waiver, legal threats, formal complaints, cross-customer privacy, alternate payment methods
- `test_chat.py` — response shape, intent mapping across phrasings, audit accumulation, reset

The delay, escalation and chat suites run against the HTTP API with FastAPI's `TestClient`,
so they assert the behaviour a reviewer can reproduce in the browser. They also assert
negatives: no invented flight numbers, no currency figures in a refund reply, and no phrase
claiming an unauthorised action was completed.

`frontend/src/__tests__/` covers the API client's normalisation and error path, and the
escalation card's rendering.

---

## Example conversations

**Priya asks for a refund and an upgrade**

> **Priya:** I want both a refund and a free upgrade.
>
> **Agent:** I'm sorry about SK-204, Priya. Since the airline cancelled it, I've initiated
> your full refund — it'll reach your original payment method within 7 business days. On the
> upgrade: your Gold status gives you priority rebooking, but it doesn't include a
> complimentary cabin upgrade, and that's not an exception I can authorise. I'm passing that
> part to a human specialist.
>
> Actions: `INITIATE_REFUND` completed · `ESCALATE_HUMAN` escalated

**Arvind asks for a hotel**

> **Arvind:** I need a hotel because I missed my meeting.
>
> **Agent:** That's a frustrating way to lose a morning. Hotel accommodation applies to
> delays of more than 5 hours, and SK-118 is delayed 4 hours, so I can't arrange one. You are
> covered for a meal voucher and lounge access, both of which I've issued.
>
> Resolution panel: Meal voucher ✓ · Lounge access ✓ · Hotel ✕ (threshold is more than 5 hours)

**Meher asks for the fare difference to be waived**

> **Meher:** Waive the ₹2,000 fare difference.
>
> **Agent:** I can't waive that one. Fare differences above ₹1,500 need supervisor approval,
> and yours is ₹2,000, so I've sent the request across. I haven't booked the alternate flight
> — that waits on the approval.
>
> Actions: `ESCALATE_SUPERVISOR` escalated

---

## Limitations

Actions are simulated. There is no airline reservation system, so "rebooking completed" means
a logged, structured request rather than a real booking — which is exactly why the agent never
quotes a flight number, departure time or seat for it.

No real refund amount exists, because no fare is supplied in the source data. The agent says
"full refund" and stops there.

State is in memory and scoped to the server process; restarting clears it, as does `/api/reset`.

The booking reference acts as the authenticated identity for the demo. Every read is scoped to
it, which is what blocks cross-customer access, but a production system would put real
authentication in front of this.

The intent parser is keyword and pattern based. It is transparent and testable, and it covers
the scenario language well, but an unusual phrasing falls through to `UNKNOWN` — where the
agent says it cannot help rather than guessing. That trade is deliberate: a miss is recoverable,
an invented policy is not.

The demo date is fixed at 23 September 2026 to match the brief.

---

## Assumptions

Implementation only. No airline policy has been assumed, extended or interpolated anywhere in
this project.

1. **Booking reference as session identity.** The selected booking reference stands in for an
   authenticated session, since the brief excludes authentication.
2. **In-memory session state.** Audit logs and escalations live in process memory, cleared by
   `/api/reset`, because the brief excludes a database.
3. **Keyword-based intent parsing.** Natural language is mapped to intents deterministically
   rather than by a model, so the decision path has no non-deterministic step. A generative
   layer could phrase replies later without touching eligibility.
4. **Action naming.** The frontend client accepts an action's name as either `type` or
   `action` and normalises it, so the UI is not coupled to one serialisation choice.
5. **Escalation targets.** Fare-difference waivers above ₹1,500 route to `ESCALATE_SUPERVISOR`;
   all other prohibited requests route to `ESCALATE_HUMAN`. This reflects the brief's wording
   about supervisor approval and is a routing label, not a policy.
6. **Display labels.** Human-readable action and policy titles in the UI are presentation
   strings for codes the backend returns. They describe decisions; they do not make them.