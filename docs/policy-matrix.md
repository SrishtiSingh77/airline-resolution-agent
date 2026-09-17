# Policy matrix

Every row below is implemented in `backend/app/services/policy_engine.py` and covered by a
test in `backend/tests/`. Nothing outside this matrix is authorised by the agent. Where a
situation is not covered, the agent says so and escalates rather than improvising.

## Disruption handling

| Situation | Entitlement | Agent may action | Notes |
| --- | --- | --- | --- |
| Flight cancelled by the airline | Free rebooking on the next available flight within 24 hours **OR** a full refund | Yes | The customer chooses. The agent does not choose for them. |
| Delay under 3 hours | ₹500 meal voucher | Yes | |
| Delay more than 3 hours | Meal voucher + lounge access | Yes | |
| Delay more than 5 hours | Meal voucher + lounge access + hotel covering the delayed hours | Yes | Delayed-hours portion only — never a full night. |
| Refund for an airline-caused cancellation | Full refund, original payment method, within 7 business days | Yes | No fare amount exists in the source data, so no rupee figure is quoted. |

## Delay thresholds applied to the three cases

| Booking | Flight | Delay | Meal voucher | Lounge | Hotel (delayed hours) | Full-night hotel |
| --- | --- | --- | --- | --- | --- | --- |
| TR1190B (Arvind) | SK-118 | 4 h | Yes | Yes | No | No |
| WL7742 (Meher) | SK-305 | 6 h | Yes | Yes | Yes | No |
| SK4821X (Priya) | SK-204 | Cancelled | Not applicable | Not applicable | Not applicable | Not applicable |

Arvind fails the hotel rule because the threshold is *more than 5 hours*, and 4 is not more
than 5. A missed connecting meeting is an inconvenience, not an entitlement under the
supplied rules, so it changes nothing.

## Loyalty tiers

| Tier | Benefit | Additional compensation |
| --- | --- | --- |
| Platinum | Priority rebooking, first access to next-available seats | None |
| Gold | Priority rebooking, first access to next-available seats | None |
| Silver | Standard handling | None |

Tier never unlocks a cabin upgrade, a fare-difference waiver, or a compensation amount
beyond the standard policy.

## Fare difference

| Situation | Outcome |
| --- | --- |
| Voluntary rebooking onto a higher-fare flight (not airline-caused) | Customer pays the fare difference |
| Waiver requested, difference at or below ₹1,500 | Agent may authorise |
| Waiver requested, difference above ₹1,500 | Supervisor approval required — escalate |

Meher's ₹2,000 difference is above the ₹1,500 limit, so `ESCALATE_SUPERVISOR` is the only
permitted outcome. The agent does not book the alternate flight, quote a flight number, or
claim the difference has been waived.

## Escalation triggers

| Trigger | Route | Agent behaviour |
| --- | --- | --- |
| Compensation beyond stated policy amounts | Human | Explains the limit, escalates, actions nothing |
| Fare-difference waiver above ₹1,500 | Supervisor | Escalates, does not book the flight |
| Exception requested for a non-airline-caused disruption | Human | Escalates |
| Threat of legal action | Human | Escalates immediately, stops negotiating compensation |
| Formal complaint | Human | Escalates immediately |
| Refund to a payment method other than the original | Human | Escalates, restates the original-method rule |

## Information boundaries

| Request | Response |
| --- | --- |
| Own booking or flight status | Provided from stored data |
| Another customer's booking | Refused — only the current booking is accessible |
| Unknown booking reference | No data returned, nothing confirmed or denied about the reference |
| Policy question with no matching rule | Stated as unavailable in the provided data; no policy invented |

## Values that are never invented

Refund amounts, next-flight numbers and times, seat numbers, hotel names or prices, lounge
names, business-class availability, payment card details, supervisor names, and any
compensation figure not listed above. Where the data does not supply a value, the agent
says the detail is not available rather than filling the gap.