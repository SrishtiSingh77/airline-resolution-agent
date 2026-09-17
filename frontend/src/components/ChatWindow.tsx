import { useEffect, useRef, useState } from 'react'
import { Headset, SendHorizonal } from 'lucide-react'
import type { ChatMessage, Scenario } from '../types'
import ChatMessageBubble from './ChatMessage'
import QuickPrompts from './QuickPrompts'

interface ChatWindowProps {
  scenario: Scenario
  messages: ChatMessage[]
  sending: boolean
  onSend: (message: string) => void
}

function EmptyState({ scenario }: { scenario: Scenario }) {
  return (
    <div className="mx-auto max-w-md py-12 text-center">
      <span className="mx-auto grid h-11 w-11 place-items-center rounded-full bg-seal/10 text-seal">
        <Headset size={20} aria-hidden />
      </span>
      <h3 className="mt-3 text-base font-semibold">
        {scenario.name.split(' ')[0]}&rsquo;s case is open
      </h3>
      <p className="mt-1 text-sm leading-relaxed text-ink-600">
        Ask about the {scenario.headline.toLowerCase()}, or pick a prompt below. Every reply
        comes from the policy engine, so the resolution panel updates with each turn.
      </p>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-3" aria-live="polite">
      <span className="grid h-8 w-8 place-items-center rounded-full bg-seal text-white" aria-hidden>
        <Headset size={15} />
      </span>
      <span className="flex items-center gap-1 rounded-lg border border-line bg-white px-4 py-3 shadow-card">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-300"
            style={{ animationDelay: `${i * 120}ms` }}
          />
        ))}
        <span className="sr-only">Checking policy</span>
      </span>
    </div>
  )
}

export default function ChatWindow({
  scenario,
  messages,
  sending,
  onSend,
}: ChatWindowProps) {
  const [draft, setDraft] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages.length, sending])

  function submit() {
    const text = draft.trim()
    if (!text || sending) return
    onSend(text)
    setDraft('')
  }

  return (
    <section className="flex min-h-0 flex-1 flex-col" aria-label="Conversation">
      <div className="scroll-thin flex-1 space-y-5 overflow-y-auto px-6 py-5">
        {messages.length === 0 ? (
          <EmptyState scenario={scenario} />
        ) : (
          messages.map((message) => <ChatMessageBubble key={message.id} message={message} />)
        )}
        {sending && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      <QuickPrompts
        prompts={scenario.quickPrompts}
        disabled={sending}
        onSelect={onSend}
      />

      <div className="border-t border-line bg-white px-6 py-4">
        <div className="flex items-end gap-2">
          <label htmlFor="composer" className="sr-only">
            Message the resolution agent
          </label>
          <textarea
            id="composer"
            rows={1}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault()
                submit()
              }
            }}
            placeholder={`Message support as ${scenario.name}`}
            className="max-h-32 min-h-[44px] flex-1 resize-y rounded-lg border border-line bg-white px-3.5 py-2.5 text-[15px] placeholder:text-ink-300 focus:border-seal"
          />
          <button
            type="button"
            onClick={submit}
            disabled={sending || !draft.trim()}
            className="inline-flex h-[44px] items-center gap-2 rounded-lg bg-seal px-4 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <SendHorizonal size={16} aria-hidden />
            Send
          </button>
        </div>
      </div>
    </section>
  )
}