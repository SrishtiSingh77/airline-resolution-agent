import { ArrowRight, Info } from 'lucide-react'
import type { Booking } from '../types'
import { FlightStatusBadge } from './StatusBadge'

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="label">{label}</p>
      <p className="value tabular mt-0.5">{value}</p>
    </div>
  )
}

export function BookingCardSkeleton() {
  return (
    <div className="card m-6 mb-0 p-5">
      <div className="h-4 w-32 animate-pulse rounded bg-line" />
      <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i}>
            <div className="h-3 w-16 animate-pulse rounded bg-line" />
            <div className="mt-2 h-4 w-24 animate-pulse rounded bg-line" />
          </div>
        ))}
      </div>
    </div>
  )
}

export default function BookingCard({ booking }: { booking: Booking }) {
  const isDelayed = Boolean(booking.delay_hours)
  const returnFlight = booking.return_flight

  return (
    <section className="card m-6 mb-0 overflow-hidden" aria-label="Booking summary">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line bg-paper px-5 py-3">
        <div className="flex items-baseline gap-3">
          <span className="text-base font-semibold tabular">{booking.flight_number}</span>
          <span className="flex items-center gap-1.5 text-sm text-ink-600">
            {booking.route.split('→')[0]?.trim()}
            <ArrowRight size={14} aria-hidden />
            {booking.route.split('→')[1]?.trim() ?? booking.route}
          </span>
        </div>
        <FlightStatusBadge status={booking.status} delayHours={booking.delay_hours} />
      </div>

      <div className="grid grid-cols-2 gap-4 px-5 py-4 sm:grid-cols-4">
        <Field label="Date" value={booking.date} />
        <Field label="Scheduled departure" value={booking.scheduled_departure} />
        {isDelayed && booking.new_departure ? (
          <Field label="New departure" value={booking.new_departure} />
        ) : (
          <Field label="Booking reference" value={booking.booking_reference} />
        )}
        {isDelayed ? (
          <Field label="Delay" value={`${booking.delay_hours} hours`} />
        ) : (
          <Field label="Passenger" value={booking.customer_name} />
        )}
      </div>

      {booking.cancellation_reason && (
        <p className="flex items-start gap-2 border-t border-line bg-cancelled/5 px-5 py-2.5 text-sm text-cancelled">
          <Info size={15} className="mt-0.5 shrink-0" aria-hidden />
          Cancelled by the airline — {booking.cancellation_reason}.
        </p>
      )}

      {returnFlight && (
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line px-5 py-3">
          <div className="text-sm text-ink-600">
            <span className="font-medium text-ink-900">Return</span>{' '}
            <span className="tabular">
              {returnFlight.route} · {returnFlight.date} · {returnFlight.scheduled_departure}
            </span>
          </div>
          <FlightStatusBadge status={returnFlight.status} />
        </div>
      )}
    </section>
  )
}