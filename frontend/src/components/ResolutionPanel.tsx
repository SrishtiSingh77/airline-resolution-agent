import { ClipboardList } from 'lucide-react'
import type { AgentAction, ChatMessage } from '../types'
import ActionLog from './ActionLog'
import EscalationCard from './EscalationCard'
import PolicyCard from './PolicyCard'

interface ResolutionPanelProps {
  /** The most recent agent turn, used for the policy and escalation cards. */
  latest: ChatMessage | null
  /** The customer message that produced it, shown in the reasoning breakdown. */
  latestRequest: string
  /** Every action logged in this session. */
  log: AgentAction[]
}

export default function ResolutionPanel({
  latest,
  latestRequest,
  log,
}: ResolutionPanelProps) {
  return (
    <aside
      className="w-full shrink-0 border-t border-line bg-paper lg:h-full lg:w-[22rem] lg:overflow-y-auto lg:border-l lg:border-t-0"
      aria-label="Resolution details"
    >
      <div className="border-b border-line bg-white px-5 py-4">
        <h2 className="flex items-center gap-2 text-sm font-semibold">
          <ClipboardList size={16} className="text-seal" aria-hidden />
          Resolution details
        </h2>
        <p className="mt-1 text-xs leading-relaxed text-ink-600">
          What the policy engine decided on the last request, and everything actioned so far.
        </p>
      </div>

      <div className="space-y-4 p-5">
        {latest?.policy_decision ? (
          <PolicyCard
            intent={latest.intent ?? 'UNKNOWN'}
            decision={latest.policy_decision}
            request={latestRequest}
            actions={latest.actions ?? []}
          />
        ) : (
          <div className="card p-4">
            <p className="text-sm font-semibold">No decision yet</p>
            <p className="mt-1 text-[13px] leading-relaxed text-ink-600">
              Send a message and the applicable policy, eligibility and reasoning appear here.
            </p>
          </div>
        )}

        {latest?.escalation && <EscalationCard escalation={latest.escalation} />}

        <ActionLog actions={log} />
      </div>
    </aside>
  )
}