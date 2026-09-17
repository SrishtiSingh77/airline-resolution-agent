import { useState } from 'react'
import { Check, ChevronDown, ScrollText, X } from 'lucide-react'
import type { Intent, PolicyDecision } from '../types'
import { actionLabel } from './ChatMessage'

/**
 * Display-only mapping from intent to the policy heading shown in the panel.
 * It labels the decision the backend already made — it never makes one.
 */
const POLICY_TITLES: Record<string, string> = {
  CANCELLED_FLIGHT: 'Cancellation rebooking',
  REQUEST_REFUND: 'Refund processing',
  REQUEST_REBOOKING: 'Cancellation rebooking',
  REQUEST_MEAL_VOUCHER: 'Delay compensation',
  REQUEST_LOUNGE: 'Delay compensation',
  REQUEST_HOTEL: 'Delay compensation',
  REQUEST_EXTRA_COMPENSATION: 'Compensation limits',
  REQUEST_UPGRADE: 'Compensation limits',
  REQUEST_HIGHER_FARE_FLIGHT: 'Fare difference',
  REQUEST_FARE_WAIVER: 'Fare difference',
  FORMAL_COMPLAINT: 'Escalation policy',
  LEGAL_THREAT: 'Escalation policy',
  BOOKING_STATUS: 'Booking information',
  FLIGHT_STATUS: 'Flight information',
}

interface PolicyCardProps {
  intent: Intent
  decision: PolicyDecision
  request: string
  actions: { type: string; status: string }[]
}

export default function PolicyCard({ intent, decision, request, actions }: PolicyCardProps) {
  const [open, setOpen] = useState(false)
  const title = decision.policy ?? POLICY_TITLES[intent] ?? 'Policy evaluation'

  const entitlements =
    decision.entitlements ??
    actions.map((action) => ({
      label: actionLabel(action.type),
      eligible: action.status === 'completed' || action.status === 'initiated',
      note: null,
    }))

  return (
    <div className="card p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="flex items-center gap-1.5 text-sm font-semibold">
            <ScrollText size={15} className="text-seal" aria-hidden />
            {title}
          </p>
          <p className="mt-1 text-sm leading-relaxed text-ink-600">{decision.reason}</p>
        </div>
        <span
          className={`shrink-0 rounded border px-2 py-0.5 text-xs font-semibold ${
            decision.eligible
              ? 'border-onTime/25 bg-onTime/10 text-onTime'
              : 'border-cancelled/25 bg-cancelled/10 text-cancelled'
          }`}
        >
          {decision.eligible ? 'Eligible' : 'Not eligible'}
        </span>
      </div>

      {entitlements.length > 0 && (
        <ul className="mt-3 space-y-1.5 border-t border-line pt-3">
          {entitlements.map((item, index) => (
            <li key={`${item.label}-${index}`} className="flex items-start gap-2 text-sm">
              {item.eligible ? (
                <Check size={15} strokeWidth={2.5} className="mt-0.5 shrink-0 text-onTime" aria-hidden />
              ) : (
                <X size={15} strokeWidth={2.5} className="mt-0.5 shrink-0 text-cancelled" aria-hidden />
              )}
              <span className={item.eligible ? 'text-ink-900' : 'text-ink-600'}>
                {item.label}
                {item.note && <span className="block text-xs text-ink-300">{item.note}</span>}
              </span>
            </li>
          ))}
        </ul>
      )}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="mt-3 inline-flex items-center gap-1 text-[13px] font-medium text-seal hover:underline"
      >
        Why this resolution?
        <ChevronDown size={14} className={`transition-transform ${open ? 'rotate-180' : ''}`} aria-hidden />
      </button>

      {open && (
        <dl className="mt-2 space-y-1.5 rounded-md bg-paper p-3 text-[13px]">
          <div className="grid grid-cols-[86px_1fr] gap-2">
            <dt className="text-ink-300">Request</dt>
            <dd className="text-ink-900">{request}</dd>
          </div>
          {(decision.evaluation ?? []).map((step) => (
            <div key={step.label} className="grid grid-cols-[86px_1fr] gap-2">
              <dt className="text-ink-300">{step.label}</dt>
              <dd className="text-ink-900 tabular">{step.value}</dd>
            </div>
          ))}
          <div className="grid grid-cols-[86px_1fr] gap-2">
            <dt className="text-ink-300">Result</dt>
            <dd className="text-ink-900">
              {decision.eligible ? 'Eligible under policy' : 'Not eligible under policy'}
              {decision.requires_escalation && ' · escalated'}
            </dd>
          </div>
          {decision.escalation_reason && (
            <div className="grid grid-cols-[86px_1fr] gap-2">
              <dt className="text-ink-300">Limit</dt>
              <dd className="text-ink-900">{decision.escalation_reason}</dd>
            </div>
          )}
        </dl>
      )}
    </div>
  )
}