import { History } from 'lucide-react'
import type { AgentAction } from '../types'
import { ActionStatusBadge } from './StatusBadge'
import { actionLabel } from './ChatMessage'

function timeOf(timestamp?: string): string {
  if (!timestamp) return '--:--'
  const parsed = new Date(timestamp)
  if (Number.isNaN(parsed.getTime())) return timestamp
  return parsed.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function ActionLog({ actions }: { actions: AgentAction[] }) {
  return (
    <div className="card p-4">
      <p className="flex items-center gap-1.5 text-sm font-semibold">
        <History size={15} className="text-seal" aria-hidden />
        Audit trail
      </p>

      {actions.length === 0 ? (
        <p className="mt-2 text-[13px] leading-relaxed text-ink-600">
          Nothing logged yet. Every action the agent takes, denies or escalates is recorded
          here for this session.
        </p>
      ) : (
        <ol className="mt-3 space-y-3 border-l border-line pl-3.5">
          {actions.map((action, index) => (
            <li key={action.id ?? `${action.type}-${index}`} className="relative">
              <span
                className="absolute -left-[18px] top-1.5 h-1.5 w-1.5 rounded-full bg-ink-300"
                aria-hidden
              />
              <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                <span className="text-[11px] tabular text-ink-300">
                  {timeOf(action.timestamp)}
                </span>
                <span className="text-[11px] font-semibold tabular text-ink-700">
                  {action.type}
                </span>
                <ActionStatusBadge status={action.status} />
              </div>
              <p className="mt-0.5 text-[13px] leading-snug text-ink-600">
                {action.reason ?? actionLabel(action.type)}
              </p>
              {action.details &&
                Object.entries(action.details).map(([key, value]) => (
                  <p key={key} className="text-[12px] text-ink-300">
                    {key.replaceAll('_', ' ')}: <span className="text-ink-600">{value}</span>
                  </p>
                ))}
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}