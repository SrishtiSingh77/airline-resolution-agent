import type {
  AgentAction,
  Booking,
  ChatResponse,
  Customer,
} from '../types'

const BASE = import.meta.env.VITE_API_BASE ?? '/api'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    })
  } catch {
    throw new ApiError(
      'Cannot reach the resolution service. Start the backend with `uvicorn app.main:app --reload`.',
      0,
    )
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') detail = body.detail
    } catch {
      /* response had no JSON body */
    }
    throw new ApiError(detail, response.status)
  }

  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

/**
 * The backend may label an action `type` or `action`. Normalise to `type` so
 * components have a single field to read.
 */
export function normaliseAction(raw: Record<string, unknown>): AgentAction {
  return {
    id: raw.id as string | undefined,
    timestamp: raw.timestamp as string | undefined,
    type: (raw.type ?? raw.action ?? 'UNKNOWN_ACTION') as string,
    status: (raw.status ?? 'completed') as AgentAction['status'],
    booking_reference: raw.booking_reference as string | undefined,
    reason: (raw.reason ?? null) as string | null,
    requires_escalation: (raw.requires_escalation ?? null) as boolean | null,
    details: (raw.details ?? null) as Record<string, string> | null,
  }
}

export const api = {
  getCustomer: (bookingReference: string) =>
    request<Customer>(`/customers/${bookingReference}`),

  getBooking: (bookingReference: string) =>
    request<Booking>(`/bookings/${bookingReference}`),

  getFlight: (bookingReference: string) =>
    request<Booking>(`/flights/${bookingReference}`),

  async sendMessage(bookingReference: string, message: string): Promise<ChatResponse> {
    const raw = await request<Record<string, unknown>>('/chat', {
      method: 'POST',
      body: JSON.stringify({ booking_reference: bookingReference, message }),
    })

    const actions = Array.isArray(raw.actions)
      ? (raw.actions as Record<string, unknown>[]).map(normaliseAction)
      : []

    return {
      message: (raw.message as string) ?? '',
      intent: (raw.intent as string) ?? 'UNKNOWN',
      policy_decision: (raw.policy_decision ?? null) as ChatResponse['policy_decision'],
      actions,
      escalation: (raw.escalation ?? null) as ChatResponse['escalation'],
      audit_log: (raw.audit_log ?? null) as ChatResponse['audit_log'],
    }
  },

  async getActionLog(bookingReference: string): Promise<AgentAction[]> {
    const raw = await request<unknown>(`/actions/${bookingReference}`)
    const list = Array.isArray(raw)
      ? raw
      : ((raw as Record<string, unknown>)?.actions as unknown[]) ?? []
    return (list as Record<string, unknown>[]).map(normaliseAction)
  },

  reset: () => request<void>('/reset', { method: 'POST' }),
}