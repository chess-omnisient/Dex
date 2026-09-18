# Shape Up Methodology — Quick Reference

## What is Shaping?

Shaping is the pre-build phase where you define a solution at the right level of abstraction — specific enough to be implementable, abstract enough to leave room for the build team to make decisions. It sits between a raw idea and a detailed spec.

## The Altitude Principle

- **Too abstract:** "We need better notifications" — no one can build from this
- **Too concrete:** Pixel-perfect mockups with exact copy — leaves no room for the team
- **Right altitude:** "There's a notification settings screen where users toggle channels and set frequency, connected from the account menu" — clear shape, flexible details

## Breadboards

Named after the electrical prototyping boards. A breadboard shows the **logical flow** of a solution without any visual design.

**Three elements:**
1. **Places** — Screens, pages, dialogs, or states the user visits
2. **Affordances** — Things the user can do at each place (buttons, fields, links, dropdowns)
3. **Connection lines** — How affordances lead to other places

**What breadboards are NOT:**
- Not wireframes (no layout, no visual hierarchy)
- Not flowcharts (they show user-facing places, not system processes)
- Not architecture diagrams (no databases, APIs, or backend components)

**When to use:** Early in shaping, to map out the flow and spot missing paths, dead ends, or unnecessary complexity.

## Fat Marker Sketches

Drawn "as if with a fat marker" — so thick you can't add fine detail even if you wanted to. They show **what goes where** on a screen without committing to visual design.

**Key characteristics:**
- Show regions/zones, not pixel positions
- Label element types (CHART, TABLE, BUTTON), not exact content
- Deliberately rough — if it looks polished, you've gone too far
- One sketch per screen/place

**What fat marker sketches are NOT:**
- Not wireframes (too rough for that)
- Not mockups (no colors, typography, or styling)
- Not design specs (no spacing, sizing, or responsive behavior)

**When to use:** After the breadboard, when you need to communicate how a specific screen is arranged — particularly for screens with complex layouts (dashboards, multi-panel views, data-heavy screens).

## When to Use Which

| Situation | Use |
|-----------|-----|
| Mapping a multi-step flow | Breadboard |
| Showing how a single screen is laid out | Fat marker sketch |
| Shaping a complete feature | Both — breadboard for flow, fat marker for key screens |
| Communicating to engineers | Breadboard first (flow logic), then fat marker for complex screens |
| Quick ideation | Simple breadboard only |
| Dashboard or data-heavy screen | Fat marker sketch |

## Common Pitfalls

1. **Going too detailed** — If your breadboard has "Cancel" buttons and loading states, you're wireframing, not shaping
2. **Skipping error paths** — Breadboards should show what happens when things go wrong
3. **Making fat markers too neat** — The roughness is a feature, not a bug. It signals "this is negotiable"
4. **Breadboarding internal systems** — Breadboards are for user-facing flows. Use architecture diagrams for backend
5. **One giant diagram** — Split complex flows into sub-flows (happy path, error handling, admin flow)
