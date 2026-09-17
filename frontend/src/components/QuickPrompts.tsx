import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { EDGE_CASE_PROMPTS } from '../data/scenarios'

interface QuickPromptsProps {
  prompts: string[]
  disabled: boolean
  onSelect: (prompt: string) => void
}

function Chip({
  prompt,
  disabled,
  onSelect,
}: {
  prompt: string
  disabled: boolean
  onSelect: (prompt: string) => void
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => onSelect(prompt)}
      className="rounded-full border border-line bg-white px-3 py-1.5 text-[13px] text-ink-700 transition-colors hover:border-seal hover:text-seal disabled:cursor-not-allowed disabled:opacity-50"
    >
      {prompt}
    </button>
  )
}

export default function QuickPrompts({ prompts, disabled, onSelect }: QuickPromptsProps) {
  const [showEdgeCases, setShowEdgeCases] = useState(false)

  return (
    <div className="border-t border-line bg-paper px-6 py-3">
      <div className="flex flex-wrap items-center gap-2">
        {prompts.map((prompt) => (
          <Chip key={prompt} prompt={prompt} disabled={disabled} onSelect={onSelect} />
        ))}
        <button
          type="button"
          onClick={() => setShowEdgeCases((open) => !open)}
          aria-expanded={showEdgeCases}
          className="inline-flex items-center gap-1 rounded-full px-2 py-1.5 text-[13px] font-medium text-ink-600 hover:text-ink-900"
        >
          Guard rails
          <ChevronDown
            size={14}
            className={`transition-transform ${showEdgeCases ? 'rotate-180' : ''}`}
            aria-hidden
          />
        </button>
      </div>

      {showEdgeCases && (
        <div className="mt-2 flex flex-wrap gap-2 border-t border-line pt-2.5">
          {EDGE_CASE_PROMPTS.map((prompt) => (
            <Chip key={prompt} prompt={prompt} disabled={disabled} onSelect={onSelect} />
          ))}
        </div>
      )}
    </div>
  )
}