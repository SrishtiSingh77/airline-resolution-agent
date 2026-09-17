import { Mail, Phone } from 'lucide-react'
import type { Customer } from '../types'
import { TierBadge } from './StatusBadge'

export default function CustomerHeader({ customer }: { customer: Customer | null }) {
  if (!customer) {
    return (
      <header className="border-b border-line bg-white px-6 py-4">
        <div className="h-5 w-40 animate-pulse rounded bg-line" />
        <div className="mt-2 h-4 w-64 animate-pulse rounded bg-line" />
      </header>
    )
  }

  return (
    <header className="border-b border-line bg-white px-6 py-4">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
        <h2 className="text-lg font-semibold">{customer.name}</h2>
        <TierBadge tier={customer.loyalty_tier} />
        <span className="rounded border border-line bg-paper px-2 py-0.5 text-xs font-semibold tabular text-ink-700">
          {customer.booking_reference}
        </span>
      </div>

      <div className="mt-1.5 flex flex-wrap items-center gap-x-5 gap-y-1 text-xs text-ink-600">
        <span className="inline-flex items-center gap-1.5">
          <Mail size={13} aria-hidden />
          {customer.email}
        </span>
        <span className="inline-flex items-center gap-1.5 tabular">
          <Phone size={13} aria-hidden />
          {customer.phone}
        </span>
        {customer.travel_history && <span>{customer.travel_history}</span>}
        {customer.prior_complaints && <span>{customer.prior_complaints}</span>}
      </div>
    </header>
  )
}