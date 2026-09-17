import { useCallback, useEffect, useMemo, useState } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { api, ApiError } from './api/client'
import BookingCard, { BookingCardSkeleton } from './components/BookingCard'
import ChatWindow from './components/ChatWindow'
import CustomerHeader from './components/CustomerHeader'
import ResolutionPanel from './components/ResolutionPanel'
import Sidebar from './components/Sidebar'
import { SCENARIOS } from './data/scenarios'
import type { AgentAction, Booking, ChatMessage, Customer, Scenario } from './types'

function now(): string {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function makeId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export default function App() {
  const [scenario, setScenario] = useState<Scenario>(SCENARIOS[0])
  const [customer, setCustomer] = useState<Customer | null>(null)
  const [booking, setBooking] = useState<Booking | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  const [conversations, setConversations] = useState<Record<string, ChatMessage[]>>({})
  const [logs, setLogs] = useState<Record<string, AgentAction[]>>({})
  const [sending, setSending] = useState(false)
  const [resetting, setResetting] = useState(false)

  const reference = scenario.bookingReference
  const messages = conversations[reference] ?? []
  const log = logs[reference] ?? []

  const loadCase = useCallback(async (bookingReference: string) => {
    setLoading(true)
    setLoadError(null)
    try {
      const [customerData, bookingData] = await Promise.all([
        api.getCustomer(bookingReference),
        api.getBooking(bookingReference),
      ])
      setCustomer(customerData)
      setBooking(bookingData)
    } catch (error) {
      setCustomer(null)
      setBooking(null)
      setLoadError(
        error instanceof ApiError
          ? error.message
          : 'Could not load this case. Check that the backend is running.',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadCase(reference)
  }, [reference, loadCase])

  const handleSend = useCallback(
    async (text: string) => {
      const customerTurn: ChatMessage = {
        id: makeId(),
        role: 'customer',
        content: text,
        timestamp: now(),
      }
      setConversations((current) => ({
        ...current,
        [reference]: [...(current[reference] ?? []), customerTurn],
      }))
      setSending(true)

      try {
        const response = await api.sendMessage(reference, text)
        const agentTurn: ChatMessage = {
          id: makeId(),
          role: 'agent',
          content: response.message,
          timestamp: now(),
          intent: response.intent,
          actions: response.actions,
          escalation: response.escalation,
          policy_decision: response.policy_decision,
        }
        setConversations((current) => ({
          ...current,
          [reference]: [...(current[reference] ?? []), agentTurn],
        }))

        // Prefer the server's audit trail; fall back to appending this turn's actions.
        try {
          const serverLog = await api.getActionLog(reference)
          setLogs((current) => ({ ...current, [reference]: serverLog }))
        } catch {
          setLogs((current) => ({
            ...current,
            [reference]: [
              ...(current[reference] ?? []),
              ...response.actions.map((action) => ({
                ...action,
                timestamp: action.timestamp ?? new Date().toISOString(),
                booking_reference: action.booking_reference ?? reference,
              })),
            ],
          }))
        }
      } catch (error) {
        setConversations((current) => ({
          ...current,
          [reference]: [
            ...(current[reference] ?? []),
            {
              id: makeId(),
              role: 'agent',
              content:
                error instanceof ApiError
                  ? error.message
                  : 'Something went wrong handling that request. Try again.',
              timestamp: now(),
              failed: true,
            },
          ],
        }))
      } finally {
        setSending(false)
      }
    },
    [reference],
  )

  const handleReset = useCallback(async () => {
    setResetting(true)
    try {
      await api.reset()
    } catch {
      /* The demo session is cleared locally regardless. */
    } finally {
      setConversations({})
      setLogs({})
      setResetting(false)
      void loadCase(reference)
    }
  }, [reference, loadCase])

  const lastAgentTurn = useMemo(
    () => [...messages].reverse().find((message) => message.role === 'agent' && !message.failed) ?? null,
    [messages],
  )

  const lastCustomerTurn = useMemo(
    () => [...messages].reverse().find((message) => message.role === 'customer')?.content ?? '',
    [messages],
  )

  return (
    <div className="flex h-full flex-col lg:flex-row">
      <Sidebar
        active={scenario}
        onSelect={setScenario}
        onReset={handleReset}
        resetting={resetting}
      />

      <main className="flex min-h-0 min-w-0 flex-1 flex-col bg-white">
        <CustomerHeader customer={customer} />

        {loading && <BookingCardSkeleton />}

        {!loading && loadError && (
          <div className="m-6 mb-0 flex items-start gap-3 rounded-lg border border-cancelled/25 bg-cancelled/5 p-4">
            <AlertTriangle size={18} className="mt-0.5 shrink-0 text-cancelled" aria-hidden />
            <div>
              <p className="text-sm font-semibold text-cancelled">Case did not load</p>
              <p className="mt-0.5 text-sm text-ink-600">{loadError}</p>
              <button
                type="button"
                onClick={() => void loadCase(reference)}
                className="mt-2 inline-flex items-center gap-1.5 rounded border border-cancelled/30 px-2.5 py-1 text-[13px] font-medium text-cancelled hover:bg-cancelled/10"
              >
                <RefreshCw size={13} aria-hidden />
                Try again
              </button>
            </div>
          </div>
        )}

        {!loading && booking && <BookingCard booking={booking} />}

        <ChatWindow
          scenario={scenario}
          messages={messages}
          sending={sending}
          onSend={handleSend}
        />
      </main>

      <ResolutionPanel latest={lastAgentTurn} latestRequest={lastCustomerTurn} log={log} />
    </div>
  )
}