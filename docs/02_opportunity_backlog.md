# Opportunity backlog and roadmap

*From the discovery in [01_discovery.md](01_discovery.md). Scores are my judgement before week-one
interviews and will move once the customer answers. Every input marked **placeholder** is a round
number to be replaced by the customer's own figure.*

## 1. How opportunities are scored

| Criterion | 1 | 5 |
|---|---|---|
| **Value** (V) | Nice to have | Removes lapses or audit findings |
| **Effort** (E) | Days, one workflow | Weeks, several teams and sign-offs |
| **Risk** (R) | Read-only, a human decides | Touches legal documents or commits the hospital |
| **Data readiness** (D) | Data doesn't exist yet | Available today, already in the spine |

**Priority = V × D ÷ (E + R).** Value only counts if the data exists. Effort and risk add up because
both cost the same thing in a hospital: time and goodwill with control functions.

## 2. Backlog

| # | Opportunity | Who it helps | V | E | R | D | Priority | Status |
|---|---|---|---|---|---|---|---|---|
| B | **Extension-notice alerts**: warn 3 weeks before the 2-month notice deadline, with a draft notice for a human to send | Procurement | 4 | 1 | 2 | 4 | **5.3** | Next |
| F | **Ground-truth loop**: every form answer feeds Licita's truth table, so the matcher learns and precision is measured | Procurement, us | 4 | 2 | 1 | 4 | **5.3** | Next |
| A | **Weekly expiry radar**: Claude briefs, one decision form, decision log | Procurement | 5 | 2 | 2 | 4 | **5.0** | **Built** |
| C | **Monthly sponsor report** from the decision log: answered rate, lapses avoided, overrides | Gerente | 3 | 1 | 1 | 3 | 4.5 | After 1 month of log |
| D | **Deserted-lot triage**: classify why a lot got no bids (structural / earlier decision / addressable) and route it to an owner | Procurement, units | 4 | 2 | 2 | 4 | 4.0 | Workflow 2 |
| G | **Single-bid early warning**: before a re-tender, flag low past competition and suggest a market consultation | Procurement | 4 | 3 | 2 | 3 | 2.4 | Pilot in month 2 |
| E | **Re-tender kickoff pack**: on "Start re-tender", open a task for the requesting unit and have Claude draft the needs memo from the last tender | Units | 5 | 4 | 4 | 2 | 1.3 | Needs legal sign-off of template |
| H | **Framework coverage check**: is the need already covered by a regional framework? | Procurement | 3 | 3 | 2 | 2 | 1.2 | Needs central purchasing data |
| I | **Appeals watch**: alert when tribunal rulings hit clauses the hospital reuses | Legal | 2 | 3 | 2 | 3 | 1.2 | Later |

Two calls worth defending in front of the customer:
- **E has the highest value and the lowest priority.** Drafting legal documents is where AI pays off
  most and where Intervención and legal will stop the programme if it arrives too early. It waits until
  A–D have built trust and a template has been signed off.
- **F ranks above the built workflow** because it is what makes A trustworthy. Without measured
  precision, the radar is an opinion.

## 3. Roadmap (90-day pilot, one hospital)

| Phase | Ships | Gate to the next phase |
|---|---|---|
| **Days 0–30: prove the habit** | A live with the procurement head · B · F · baseline measured (lapses last year, hours per week) | ≥ 80 % of digest items answered in 3 days (H1) |
| **Days 31–60: widen the net** | D (deserted lots) · C (first sponsor report) · G piloted on 3 re-tenders | Matcher precision ≥ 70 % on the first 50 answers (H2) |
| **Days 61–90: scale decision** | E designed with legal · second hospital onboarded on A+B+F · operating model handed over | Gerente signs off on scale to the regional service |

## 4. ROI logic

The value case leads with **risk and time**, not price. Price is the easiest number to compute and the
hardest to attribute.

| Value pool | Formula | Inputs |
|---|---|---|
| **Staff time** | hours/week chasing end dates × share saved × loaded hourly cost × 46 weeks | All three **placeholders**, measured in week one |
| **Lapses avoided** | lapses/year in the baseline × share avoided × cost per lapse (regularisation time + emergency terms) | Baseline from the procurement head and Intervención **[confirm]** |
| **Competition** | annual budget of single-bid contracts flagged in time × share moved to 2+ bids × median discount gain | Budget **measured**; share **placeholder**; discount gain **measured** |

Worked example for the competition pool, the only one with measured inputs today:

| Input | Value | Source |
|---|---|---|
| Annual budget of flagged contracts that had a single bid last time | ≈ €4.9 M (22 contracts) | Public PLACSP data, this hospital |
| Share moved to two or more bids by starting earlier | 10 % | **placeholder** |
| Median discount gain from 1 to 2 bids, Spanish health buyers | 6.9 points | 140,952 lots, 2017–2026 (correlation, not proof of cause) |
| **Estimate** | **≈ €34,000 a year** | 4.9 M × 10 % × 6.9 % |

What it costs: the n8n licence (customer's plan), Claude usage (5 short calls a week, cents per run on
this design), and procurement time to answer the digest (about 10 minutes a week, to be measured).
The deployment's own cost belongs in the customer's business case, not in this estimate.

What would make this case wrong: if most flagged contracts turn out to be covered (low precision, H2),
the time and lapse pools shrink to near zero. That's why precision is measured in the first 60 days,
before anyone quotes the ROI to the Gerente.
