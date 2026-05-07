# Manual Test Scenarios

Scenarios used to verify the agent end-to-end. Each scenario is run by typing the user input into `python main.py`. The expected behavior is what a correct run should produce.

## Pricing reference (from `PricingSheet`)

| Service | base | urgent ×1.25 | emergency ×1.5 | simple ×0.9 | standard ×1.0 | complex ×1.3 |
|---|---:|---:|---:|---:|---:|---:|
| ceiling fan installation | 150 | 187.50 | 225.00 | 135.00 | 150.00 | 195.00 |
| faucet repair | 95 | 118.75 | 142.50 | 85.50 | 95.00 | 123.50 |
| tv mounting | 120 | 150.00 | 180.00 | 108.00 | 120.00 | 156.00 |
| drywall patch | 110 | 137.50 | 165.00 | 99.00 | 110.00 | 143.00 |

Final price = `base × urgency_mult × complexity_mult`.

---

## A. Pricing — single turn

### A1. Simple quote
- **Input:** `how much for drywall patch?`
- **Expected:** `pricing_tool` called once. Result `$110` (urgency=normal, complexity=standard).

### A2. Urgent
- **Input:** `urgent quote for faucet repair`
- **Expected:** `pricing_tool` called once. Result `$118.75` (95 × 1.25 × 1.0).

### A3. Emergency
- **Input:** `EMERGENCY! how much for faucet repair right now`
- **Expected:** `pricing_tool` called once. Result `$142.50` (95 × 1.5 × 1.0).

### A4. Complex
- **Input:** `quote for complex ceiling fan installation`
- **Expected:** `pricing_tool` called once. Result `$195` (150 × 1.0 × 1.3).

### A5. Urgent + complex
- **Input:** `quote for urgent ceiling fan installation with complex wiring`
- **Expected:** `pricing_tool` called once. Result `$243.75` (150 × 1.25 × 1.3).

### A6. Simple
- **Input:** `simple drywall patch quote`
- **Expected:** `pricing_tool` called once. Result `$99` (110 × 1.0 × 0.9).

---

## B. Scheduling — date format coverage

### B1. Weekday name
- **Input:** `any morning slots Friday?`
- **Expected:** `scheduling_tool` with `requested_day='Friday'`. Returns up to 5 slots between 9:00 and 12:00 on the next Friday, in `America/Chicago`.

### B2. Relative date
- **Input:** `any morning slots tomorrow?`
- **Expected:** `scheduling_tool` with `requested_day='tomorrow'`. Returns slots for `today + 1 day`.

### B3. ISO date
- **Input:** `any morning slots 2026-05-08?`
- **Expected:** `scheduling_tool` with `requested_day='2026-05-08'`. Returns slots for that date.

### B4. Natural-language date
- **Input:** `any morning slots May 8?`
- **Expected:** `scheduling_tool` with `requested_day='May 8'`. Resolves to current year, rolls to next year if past.

### B5. Calendar full
- **Input:** `any morning slots tomorrow?` on a fully-booked day
- **Expected:** `scheduling_tool` returns `available_slots: []`. Agent explains no slots and offers alternatives. Does **not** invent slots.

---

## C. Combined — single turn, both tools

### C1. Quote + scheduling in one message
- **Input:** `how much for tv mounting? any morning slots tomorrow?`
- **Expected:** Both `pricing_tool` AND `scheduling_tool` called in the same turn. Final response includes the `$120` quote and the 5 numbered slot options.

---

## D. Multi-turn happy path — full booking flow

### D1. End-to-end booking
- **Inputs (3 turns):**
  1. `how much for faucet repair?`
  2. `any morning slots tomorrow?`
  3. `option 2, my name is John Smith`
- **Expected per turn:**
  - Turn 1: only `pricing_tool` called → `$95`.
  - Turn 2: only `scheduling_tool` called → 5 numbered slot options.
  - Turn 3: only `create_calendar_event_tool` called with `customer_name='John Smith'` and `start_iso` matching option 2 from turn 2's result. Returns `status: success` and an `event_id`.
- **Tool-call budget:** exactly 3 calls total across the 3 turns. No re-quoting, no re-fetching availability.

### D2. Booking on a fully-booked day
- **Inputs (3 turns):**
  1. `how much for faucet repair?`
  2. `any morning slots tomorrow?` (calendar fully booked)
  3. `option 2, my name is John Smith`
- **Expected:**
  - Turn 2: `scheduling_tool` returns empty `available_slots`.
  - Turn 3: agent does **not** call `create_calendar_event_tool`. Explains there are no options and offers a different day or time window. No phantom booking.

---

## E. LLM-provider switch

### E1. Default — Google
- **Setup:** unset or `LLM_PROVIDER=google` in `.env`.
- **Expected:** `type(model).__name__ == 'ChatGoogleGenerativeAI'`. All scenarios above pass.

### E2. Anthropic
- **Setup:** `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY=...` in `.env`.
- **Expected:** `type(model).__name__ == 'ChatAnthropic'`. All scenarios above pass.

### E3. Bad provider
- **Setup:** `LLM_PROVIDER=foo`.
- **Expected:** `ValueError: Unknown LLM_PROVIDER: 'foo'. Expected 'google' or 'anthropic'.` raised at startup before any tool is loaded.

---

## How to clean up after testing

Booking scenarios create real events on the user's primary Google Calendar. Use the helper script:

```bash
python cleanup_test_events.py
```

It deletes future events whose summary starts with `Handyman Appointment - Test` or `Handyman Appointment - TEST`. Run it before each D-series scenario to guarantee a clean calendar — otherwise `scheduling_tool` may legitimately return `available_slots: []` from prior bookings, and a passing scenario can look like a regression.
