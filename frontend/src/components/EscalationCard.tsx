import { UserRoundCheck } from 'lucide-react'
import type { Escalation } from '../types'

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-[110px_1fr] gap-2 py-1">
      <dt className="text-xs font-semibold text-escalate/80">{label}</dt>
      <dd className="text-sm text-ink-900">{value}</dd>
    </div>
  )
}

export default function EscalationCard({
  escalation,
  compact = false,
}: {
  escalation: Escalation
  compact?: boolean
}) {
  const target = escalation.target === 'SUPERVISOR' ? 'supervisor' : 'human specialist'

  return (
    <div
      role="status"
      className={`rounded-lg border border-escalate/30 bg-escalate/[0.06] ${
        compact ? 'p-3' : 'p-4'
      }`}
    >
      <p className="flex items-center gap-2 text-sm font-semibold text-escalate">
        <UserRoundCheck size={16} strokeWidth={2.25} aria-hidden />
        Human escalation required
      </p>
      <p className="mt-1 text-xs text-escalate/80">
        Routed to a {target}. The agent has not actioned this request.
      </p>

      <dl className="mt-2.5 divide-y divide-escalate/15 border-t border-escalate/15 pt-1">
        <Row label="Reason" value={escalation.reason} />
        <Row label="Requested" value={escalation.requested_action} />
        <Row label="Policy limit" value={escalation.policy_limitation} />
        <Row label="Booking" value={escalation.booking_reference} />
      </dl>
    </div>
  )
}