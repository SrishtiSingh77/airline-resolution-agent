import { AlertCircle, Ban, Check, Headset, User } from 'lucide-react'
import type { AgentAction, ChatMessage as Message } from '../types'
import EscalationCard from './EscalationCard'

export const ACTION_LABELS: Record<string, string> = {
  REBOOK_NEXT_AVAILABLE: 'Rebooking on the next available flight within 24 hours',
  INITIATE_REFUND: 'Full refund initiated to the original payment method',
  ISSUE_MEAL_VOUCHER: 'Meal voucher issued',
  ISSUE_LOUNGE_ACCESS: 'Lounge access issued',
  ARRANGE_DELAY_HOURS_HOTEL: 'Hotel arranged for the delayed hours',
  PROVIDE_BOOKING_STATUS: 'Booking details shared',
  PROVIDE_FLIGHT_STATUS: 'Flight status shared',
  ESCALATE_HUMAN: 'Escalated to a human specialist',
  ESCALATE_SUPERVISOR: 'Escalated to a supervisor',
  FULL_NIGHT_HOTEL: 'Full-night hotel',
  WAIVE_FARE_DIFFERENCE: 'Fare-difference waiver',
  UPGRADE_CABIN: 'Cabin upgrade',
}

export function actionLabel(type: string): string {
  return ACTION_LABELS[type] ?? type.replaceAll('_', ' ').toLowerCase()
}

function ActionRow({ action }: { action: AgentAction }) {
  const granted = action.status === 'completed' || action.status === 'initiated'
  const escalated = action.status === 'escalated'

  const Icon = granted ? Check : escalated ? Headset : Ban
  const tone = granted
    ? 'text-authorized'
    : escalated
      ? 'text-escalate'
      : 'text-cancelled'

  return (
    <li className="flex items-start gap-2 text-sm">
      <Icon size={15} strokeWidth={2.5} className={`mt-0.5 shrink-0 ${tone}`} aria-hidden />
      <span className={granted ? 'text-ink-900' : 'text-ink-600'}>
        {actionLabel(action.type)}
        {!granted && action.status === 'not_authorized' && ' — not authorised'}
        {!granted && action.status === 'denied' && ' — not eligible'}
      </span>
    </li>
  )
}

export default function ChatMessageBubble({ message }: { message: Message }) {
  const isCustomer = message.role === 'customer'
  const visibleActions = (message.actions ?? []).filter(
    (action) => !action.type.startsWith('ESCALATE_') || !message.escalation,
  )

  return (
    <article
      className={`flex animate-rise gap-3 ${isCustomer ? 'flex-row-reverse' : ''}`}
      aria-label={isCustomer ? 'Customer message' : 'Agent message'}
    >
      <span
        className={`grid h-8 w-8 shrink-0 place-items-center rounded-full ${
          isCustomer ? 'bg-ink-900/8 text-ink-700' : 'bg-seal text-white'
        }`}
        aria-hidden
      >
        {isCustomer ? <User size={15} /> : <Headset size={15} />}
      </span>

      <div className={`max-w-[42rem] ${isCustomer ? 'items-end text-right' : ''}`}>
        <div
          className={`inline-block rounded-lg px-4 py-2.5 text-left text-[15px] leading-relaxed ${
            isCustomer
              ? 'bg-ink-900 text-white'
              : message.failed
                ? 'border border-cancelled/30 bg-cancelled/5 text-cancelled'
                : 'border border-line bg-white text-ink-900 shadow-card'
          }`}
        >
          {message.failed && (
            <AlertCircle size={15} className="mr-1.5 inline-block align-[-2px]" aria-hidden />
          )}
          {message.content.split('\n').map((line, index) => (
            <p key={index} className={index > 0 ? 'mt-2' : ''}>
              {line}
            </p>
          ))}
        </div>

        {visibleActions.length > 0 && (
          <ul className="mt-2 space-y-1 rounded-lg border border-line bg-paper px-3.5 py-2.5 text-left">
            {visibleActions.map((action, index) => (
              <ActionRow key={`${action.type}-${index}`} action={action} />
            ))}
          </ul>
        )}

        {message.escalation && (
          <div className="mt-2 text-left">
            <EscalationCard escalation={message.escalation} compact />
          </div>
        )}

        <p className={`mt-1.5 text-[11px] tabular text-ink-300 ${isCustomer ? '' : 'pl-1'}`}>
          {message.timestamp}
          {!isCustomer && message.intent && message.intent !== 'UNKNOWN' && (
            <span className="ml-2 text-ink-300">{message.intent.replaceAll('_', ' ').toLowerCase()}</span>
          )}
        </p>
      </div>
    </article>
  )
}