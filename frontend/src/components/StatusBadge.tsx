import { AlertTriangle, CheckCircle2, Clock, ShieldAlert, XCircle } from 'lucide-react'
import type { ActionStatus, LoyaltyTier } from '../types'

type Tone = 'cancelled' | 'delayed' | 'ok' | 'escalate' | 'neutral'

const TONES: Record<Tone, string> = {
  cancelled: 'bg-cancelled/10 text-cancelled border-cancelled/25',
  delayed: 'bg-delayed/10 text-delayed border-delayed/25',
  ok: 'bg-onTime/10 text-onTime border-onTime/25',
  escalate: 'bg-escalate/10 text-escalate border-escalate/25',
  neutral: 'bg-ink-900/5 text-ink-700 border-line',
}

const ICONS: Record<Tone, typeof Clock> = {
  cancelled: XCircle,
  delayed: Clock,
  ok: CheckCircle2,
  escalate: ShieldAlert,
  neutral: AlertTriangle,
}

function toneForFlight(status: string): Tone {
  const value = status.toLowerCase()
  if (value.includes('cancel')) return 'cancelled'
  if (value.includes('delay')) return 'delayed'
  if (value.includes('unaffected') || value.includes('on time')) return 'ok'
  return 'neutral'
}

export function toneForAction(status: ActionStatus): Tone {
  if (status === 'completed' || status === 'initiated') return 'ok'
  if (status === 'escalated') return 'escalate'
  return 'cancelled'
}

interface BadgeProps {
  label: string
  tone: Tone
  withIcon?: boolean
  className?: string
}

export function Badge({ label, tone, withIcon = false, className = '' }: BadgeProps) {
  const Icon = ICONS[tone]
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded border px-2 py-0.5 text-xs font-semibold ${TONES[tone]} ${className}`}
    >
      {withIcon && <Icon size={13} strokeWidth={2.5} aria-hidden />}
      {label}
    </span>
  )
}

/** Flight status, e.g. CANCELLED / DELAYED 4H. Uppercase matches the PNR. */
export function FlightStatusBadge({
  status,
  delayHours,
}: {
  status: string
  delayHours?: number | null
}) {
  const tone = toneForFlight(status)
  const label =
    tone === 'delayed' && delayHours
      ? `DELAYED ${delayHours}H`
      : status.toUpperCase()
  return <Badge label={label} tone={tone} withIcon />
}

const TIER_STYLES: Record<LoyaltyTier, string> = {
  Platinum: 'bg-ink-900 text-white border-ink-900',
  Gold: 'bg-[#8A6512] text-white border-[#8A6512]',
  Silver: 'bg-ink-300/25 text-ink-700 border-ink-300/50',
}

export function TierBadge({ tier }: { tier: LoyaltyTier }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${
        TIER_STYLES[tier] ?? TIER_STYLES.Silver
      }`}
      title={
        tier === 'Silver'
          ? 'Standard rebooking priority'
          : 'Priority rebooking. No additional compensation.'
      }
    >
      {tier}
    </span>
  )
}

const ACTION_LABELS: Record<string, string> = {
  completed: 'Completed',
  initiated: 'Initiated',
  denied: 'Not eligible',
  not_authorized: 'Not authorised',
  escalated: 'Escalated',
}

export function ActionStatusBadge({ status }: { status: ActionStatus }) {
  return <Badge label={ACTION_LABELS[status] ?? status} tone={toneForAction(status)} />
}

export default Badge