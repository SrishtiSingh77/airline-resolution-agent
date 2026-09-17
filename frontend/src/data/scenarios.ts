import type { Scenario } from '../types'

/**
 * Scenario routing only.
 *
 * Everything the agent says about a customer, a booking or a policy comes from
 * the backend. This file holds the booking references the demo switches
 * between, plus the reviewer's quick-test prompts. The prompts are sent through
 * `POST /api/chat` exactly like typed messages — there are no canned replies on
 * the frontend.
 */
export const SCENARIOS: Scenario[] = [
  {
    id: 'priya',
    bookingReference: 'SK4821X',
    name: 'Priya Nair',
    tier: 'Gold',
    headline: 'Cancelled flight',
    quickPrompts: [
      'Why was my flight cancelled?',
      'I want a full refund.',
      'I want a business class upgrade for the trouble.',
      'I want both a refund and a free upgrade.',
      "I'm furious about this.",
    ],
  },
  {
    id: 'arvind',
    bookingReference: 'TR1190B',
    name: 'Arvind Kulkarni',
    tier: 'Silver',
    headline: '4-hour delay',
    quickPrompts: [
      'My flight is delayed. What am I entitled to?',
      'I want a meal voucher.',
      'Can I get lounge access?',
      'I need a hotel because I missed my meeting.',
      'I want extra compensation.',
    ],
  },
  {
    id: 'meher',
    bookingReference: 'WL7742',
    name: 'Meher Kaur',
    tier: 'Platinum',
    headline: '6-hour delay',
    quickPrompts: [
      'My flight is delayed 6 hours. What do I get?',
      "I want a full night's hotel.",
      'I only want hotel coverage for the delay.',
      'Move me to a higher-fare flight.',
      'Waive the ₹2,000 fare difference.',
      "I want compensation because I'm Platinum.",
    ],
  },
]

/** Prompts that exercise the guard rails from any scenario. */
export const EDGE_CASE_PROMPTS = [
  'Send my refund to a different card.',
  'I want to file a formal complaint.',
  "I'm taking legal action.",
]

export const DEMO_DATE = 'Wednesday, 23 September 2026'

export function scenarioFor(bookingReference: string): Scenario {
  const match = SCENARIOS.find((s) => s.bookingReference === bookingReference)
  if (!match) throw new Error(`Unknown scenario: ${bookingReference}`)
  return match
}