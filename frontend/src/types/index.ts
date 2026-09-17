/**
 * Types mirroring the backend Pydantic models.
 *
 * Optional fields are deliberate: the UI must render whatever the policy engine
 * returns without assuming a field exists, and must never fill a gap with
 * invented data.
 */

export type LoyaltyTier = 'Gold' | 'Silver' | 'Platinum'

export type FlightStatus = 'Cancelled' | 'Delayed' | 'Unaffected' | 'On time' | string

export interface Customer {
  name: string
  loyalty_tier: LoyaltyTier
  booking_reference: string
  email: string
  phone: string
  travel_history?: string | null
  prior_complaints?: string | null
}

export interface ReturnFlight {
  flight?: string | null
  flight_number?: string | null
  route: string
  date: string
  scheduled_departure: string
  status: FlightStatus
}

export interface Booking {
  booking_reference: string
  customer_name: string
  flight_number: string
  route: string
  date: string
  scheduled_departure: string
  status: FlightStatus
  delay_hours?: number | null
  new_departure?: string | null
  cancellation_reason?: string | null
  return_flight?: ReturnFlight | null
}

export interface PolicyDecision {
  eligible: boolean
  action?: string | null
  reason: string
  requires_escalation: boolean
  escalation_reason?: string | null
  policy?: string | null
  /** Optional rule-by-rule breakdown used by the "Why this resolution?" panel. */
  evaluation?: PolicyEvaluationStep[] | null
  entitlements?: Entitlement[] | null
}

export interface PolicyEvaluationStep {
  label: string
  value: string
}

export interface Entitlement {
  label: string
  eligible: boolean
  note?: string | null
}

export type ActionStatus =
  | 'completed'
  | 'initiated'
  | 'denied'
  | 'not_authorized'
  | 'escalated'

export interface AgentAction {
  id?: string
  timestamp?: string
  /** Backend may name this `type` or `action`; the client normalises to `type`. */
  type: string
  status: ActionStatus
  booking_reference?: string
  reason?: string | null
  requires_escalation?: boolean | null
  details?: Record<string, string> | null
}

export type EscalationTarget = 'HUMAN' | 'SUPERVISOR' | string

export interface Escalation {
  reason: string
  requested_action: string
  policy_limitation: string
  booking_reference: string
  target?: EscalationTarget | null
  timestamp?: string
}

export type Intent =
  | 'BOOKING_STATUS'
  | 'FLIGHT_STATUS'
  | 'CANCELLED_FLIGHT'
  | 'REQUEST_REFUND'
  | 'REQUEST_REBOOKING'
  | 'REQUEST_MEAL_VOUCHER'
  | 'REQUEST_LOUNGE'
  | 'REQUEST_HOTEL'
  | 'REQUEST_EXTRA_COMPENSATION'
  | 'REQUEST_UPGRADE'
  | 'REQUEST_HIGHER_FARE_FLIGHT'
  | 'REQUEST_FARE_WAIVER'
  | 'FORMAL_COMPLAINT'
  | 'LEGAL_THREAT'
  | 'UNKNOWN'
  | string

export interface ChatResponse {
  message: string
  intent: Intent
  policy_decision: PolicyDecision | null
  actions: AgentAction[]
  escalation: Escalation | null
  audit_log?: AuditEntry[] | null
}

export interface AuditEntry {
  timestamp: string
  event: string
  detail?: string | null
}

export interface ChatMessage {
  id: string
  role: 'customer' | 'agent'
  content: string
  timestamp: string
  /** Resolution metadata attached to an agent turn. */
  intent?: Intent
  actions?: AgentAction[]
  escalation?: Escalation | null
  policy_decision?: PolicyDecision | null
  /** Set when the request failed, so the UI can show an error state. */
  failed?: boolean
}

export interface Scenario {
  id: string
  bookingReference: string
  name: string
  tier: LoyaltyTier
  headline: string
  quickPrompts: string[]
}