# Discovery: contract continuity at a public hospital

*Written the way week one of an on-site deployment would produce it: what the process looks like
today, who is involved, where it breaks, and what we still need to ask. Figures come from public
PLACSP award data (radar as of 2026-10-10, data through 2026-09-30). The hospital is a design partner
of an independent research project and is not named here.*

DRAFT: the process map below is built from public data and the law, then checked against how
procurement teams describe their work. Items marked **[confirm]** need a conversation on site.

## 1. The problem (hypothesis to validate on site)

The procurement team finds out a contract is ending too late to re-tender it in time.

Spanish public hospitals buy most recurring services and supplies (maintenance, cleaning, catering,
lab reagents, medical gases) on fixed-term contracts. When one ends with no successor in place, the
hospital either extends it on emergency terms or keeps receiving the service with no contract. Both
show up later as audit findings, payment problems and staff time spent regularising.

The law leaves little slack (Ley 9/2017, LCSP, art. 29) **[confirm with legal]**:
- an extension binds the supplier only if notified **at least 2 months** before the end date;
- a contract can be kept running for up to **9 months** while its successor is formalised, but only
  if the new tender was **published at least 3 months** before the end date.

So the real deadline is not the end date. It is the publication date, and preparing a tender takes
months before that.

## 2. What the data says (one hospital, public data)

| Signal | Value | What it means |
|---|---|---|
| Recurring contracts tracked | 255 | One-off equipment purchases excluded |
| Need a decision now | **15 %** (38) | start now 18 · verify 14 · due within 6 months 6 |
| Of start-now / verify, no successor found | **84 %** | 27 of 32 (heuristic matcher, precision not yet measured) |
| Of start-now / verify, single bid last time | **69 %** | Little competition, so less room to wait |
| Typical lead time, award to award, for these categories | median 163 days (115–242) | p80 of past tenders in the same CPV, plus 90 days internal prep (an assumption) |
| Annual budget across the 38 | ≈ €8.5 M | Published budgets, not spend |
| Lots declared deserted since 2024 that were never re-published | **68 %** (19 of 28) | The need didn't go away; where did it go? |
| Same signals across all hospitals in the regional health service | 453 to decide, 192 start-now | The scale story |

Caveat that changes the conversation: the successor matcher is a heuristic. Until the procurement
team confirms a sample, these are **leads, not facts**, and every number above can be wrong in both
directions. That is why the first workflow asks a human about every item and logs the answer.

## 3. As-is process (how continuity is managed today)

```
 Unit needs a service ──► Contract awarded ──► Runs 1–5 years ──► ??? ──► Ends
                                                     │
              nobody owns "watch the end date" ──────┘
```

| Step | Who | How today **[confirm]** | Where it breaks |
|---|---|---|---|
| 1. Know what is ending | Procurement (Servicio de Contratación) | Spreadsheet per technician, or memory | No single list; staff turnover loses it |
| 2. Decide: extend, re-tender or drop | Procurement + requesting unit | Email or meeting when someone notices | Decided late, often after the 2-month notice window |
| 3. Write the need and specs (memoria, PPT) | Requesting unit (maintenance, pharmacy, lab…) | Word, from the last tender | Units see it as extra work; slowest step |
| 4. Legal and budget checks | Legal advisers, Intervención (financial control) | Sequential sign-offs | Queues; a late file gets rushed or misses |
| 5. Publish, evaluate, award, formalise | Procurement, tender board (mesa) | PLACSP | Fixed legal minimums; can't be compressed |
| 6. Contract lapses or is regularised | Procurement, Intervención, Gerencia | Emergency extension or payment without contract | Audit risk, appeals, staff time |

The fix is not faster tendering. It is **starting earlier, with a named owner and a dated decision**.

## 4. Stakeholders

| Who | Role in this deployment | What they need to hear | Likely stance |
|---|---|---|---|
| Head of Procurement (Jefe/a de Contratación) | Owner and primary user; decides each item | "One email a week, you stay in control, it learns from your answers" | Champion if it saves time; lost if it adds clicks |
| Hospital Manager (Gerente) | Sponsor | "Fewer contracts lapsing, visible in a monthly number" | Supportive; wants a low-risk pilot |
| Requesting units (maintenance, pharmacy, lab, IT) | Write the specs once a re-tender starts | Earlier, predictable requests instead of urgent ones | Neutral to resistant: it's more work, sooner |
| Intervención (financial control) | Watchdog; sees the lapses afterwards | "This reduces the cases you flag" | **Skeptic**: wary of AI near legal decisions |
| Legal advisers | Sign off pliegos and extensions | Nothing is decided by the AI; dates come from the contract | Cautious |
| Hospital IT | Gatekeeper for hosting, email, credentials | Read-only data, self-hosted option, no patient data | Gatekeeper; decides on-prem vs cloud |
| Regional health service (central purchasing) | Runs frameworks that can absorb a need | A contract may already be covered by a framework | Ally for the scale story |

The decision-maker for go-live is the Gerente. The person who decides whether it is *used* is the Head
of Procurement. Intervención can quietly stop it, so they get an early briefing, not a demo at the end.

## 5. What we still need to ask (week-one interviews)

Procurement head
1. How do you find out today that a contract is ending? Show me the list, if there is one.
2. Last year, how many contracts ran without coverage or needed an emergency extension? **[baseline]**
3. Who decides extend vs re-tender, and how long does that decision take?
4. How many hours a week does the team spend chasing end dates? **[baseline for ROI]**
5. Which of these 38 flagged contracts are wrong, and why? (ground truth for the matcher)

Requesting units
6. How much notice do you need to write a technical spec? What slows you down?

Intervención and legal
7. Which findings come up every year? Would a dated decision log help your review?
8. What must never be automated? (Expectation: anything that commits the hospital.)

IT
9. Email system (Outlook vs Gmail), hosting rules, can n8n run on-prem, who holds credentials?

## 6. Hypotheses to prove or kill in the pilot

| # | Hypothesis | How we'll know |
|---|---|---|
| H1 | Procurement will answer a weekly digest | ≥ 80 % of items answered within 3 days (decision log) |
| H2 | The radar is right often enough to trust | Matcher precision on the first 50 answers ≥ 70 % |
| H3 | Earlier decisions mean fewer lapses | Lapses per quarter vs the baseline from Q2 |
| H4 | Claude's suggestion helps rather than biases | Override rate stays between 10 % and 50 %; reasons logged |
