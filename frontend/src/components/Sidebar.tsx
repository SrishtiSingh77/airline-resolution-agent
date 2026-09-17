import { PlaneTakeoff, RotateCcw } from 'lucide-react'
import { DEMO_DATE, SCENARIOS } from '../data/scenarios'
import type { Scenario } from '../types'

interface SidebarProps {
  active: Scenario
  onSelect: (scenario: Scenario) => void
  onReset: () => void
  resetting: boolean
}

export default function Sidebar({ active, onSelect, onReset, resetting }: SidebarProps) {
  return (
    <aside className="flex w-full shrink-0 flex-col border-b border-ink-700 bg-ink-900 text-white lg:h-full lg:w-72 lg:border-b-0 lg:border-r">
      <div className="flex items-center gap-2.5 px-5 py-5">
        <span className="grid h-9 w-9 place-items-center rounded-md bg-seal">
          <PlaneTakeoff size={18} strokeWidth={2.25} aria-hidden />
        </span>
        <div className="leading-tight">
          <h1 className="text-[15px] font-semibold">Airline Resolution Agent</h1>
          <p className="text-xs text-ink-300">Disruption support console</p>
        </div>
      </div>

      <div className="px-5 pb-3">
        <p className="text-xs text-ink-300">Operating day</p>
        <p className="text-sm font-medium tabular">{DEMO_DATE}</p>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-2" aria-label="Scenarios">
        <p className="px-2 pb-2 text-[11px] font-semibold text-ink-300">Open cases</p>
        <ul className="space-y-1">
          {SCENARIOS.map((scenario) => {
            const isActive = scenario.bookingReference === active.bookingReference
            return (
              <li key={scenario.id}>
                <button
                  type="button"
                  onClick={() => onSelect(scenario)}
                  aria-current={isActive ? 'true' : undefined}
                  className={`w-full rounded-md px-3 py-2.5 text-left transition-colors ${
                    isActive
                      ? 'bg-ink-700 text-white'
                      : 'text-ink-300 hover:bg-ink-800 hover:text-white'
                  }`}
                >
                  <span className="block text-sm font-semibold">{scenario.name}</span>
                  <span className="mt-0.5 flex items-center gap-2 text-xs">
                    <span className="tabular">{scenario.bookingReference}</span>
                    <span aria-hidden className="opacity-40">
                      |
                    </span>
                    <span>{scenario.headline}</span>
                  </span>
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="border-t border-ink-700 p-3">
        <button
          type="button"
          onClick={onReset}
          disabled={resetting}
          className="flex w-full items-center justify-center gap-2 rounded-md border border-ink-600 px-3 py-2 text-sm font-medium text-ink-300 transition-colors hover:border-ink-300 hover:text-white disabled:opacity-50"
        >
          <RotateCcw size={15} className={resetting ? 'animate-spin' : ''} aria-hidden />
          {resetting ? 'Resetting' : 'Reset conversation'}
        </button>
        <p className="mt-2 px-1 text-[11px] leading-snug text-ink-300">
          Clears the chat, actions and audit trail for this session.
        </p>
      </div>
    </aside>
  )
}