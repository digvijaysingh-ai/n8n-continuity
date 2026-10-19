# Operating model: running automation at the hospital

*One page the hospital keeps after the deployment team leaves. It says who can ask for an
automation, who owns it, what it must pass before it goes live, how credentials are held, and
which signals mean it's time to scale. It follows the discovery in [01](01_discovery.md) and the
backlog in [02](02_opportunity_backlog.md). Role names are generic; the hospital fills in people.*

## 1. Principles

1. **A human decides anything that commits the hospital.** Automations prepare, remind and record.
2. **Every automation has one named business owner.** No owner, no production.
3. **Systems of record stay read-only to n8n** unless the review gate approves a write.
4. **Every decision is logged**: who, when, what the AI suggested, what the human chose.
5. **Start small, prove it, then widen.** A gate between each phase, measured, not assumed.

## 2. Roles

| Role | Who (fill in) | Job |
|---|---|---|
| **Sponsor** | Hospital Manager | Sets priorities, approves scaling, gets the monthly report |
| **Business owner** | Head of Procurement (per workflow) | Owns the outcome, answers the digest, approves changes |
| **Automation lead** | A procurement analyst with IT support | Runs the n8n workspace, triages intake, keeps the backlog |
| **Builder** | Deployment engineer at first, then the automation lead | Builds and changes workflows |
| **Control** | Intervención (financial control) | Reviews the decision log; can veto anything touching payments |
| **Legal** | Legal advisers | Sign off any template or text that leaves the hospital |
| **IT & security** | Hospital IT, data protection officer | Hosting, credentials, access, data protection review |

## 3. Intake: how a new idea gets in

1. Anyone fills the **intake form** (an n8n form): the problem, who feels it, how often, what data it needs.
2. The automation lead **scores it weekly** with the backlog formula, V × D ÷ (E + R).
3. Ideas above the line go to the **monthly prioritisation** with the sponsor and business owners,
   with no more than **3 workflows in build at once**.
4. Every requester gets an answer within 2 weeks: *building*, *later* (with reason) or *no* (with reason).

## 4. Ownership and RACI

R = does it · A = accountable (one per row) · C = consulted · I = informed

| Activity | Sponsor | Business owner | Automation lead | Builder | Control | Legal | IT & security |
|---|---|---|---|---|---|---|---|
| Prioritise the backlog | **A** | C | R | C | I | I | I |
| Build or change a workflow | I | **A** | C | R | I | C* | C |
| Pass the review gate | I | **A** | R | R | C | C* | C |
| Run it and answer the digest | I | **A** / R | C | I | I | – | – |
| Monitor failures and fix | – | I | **A** | R | – | – | C |
| Review the decision log | I | R | C | – | **A** | – | – |
| Grant or rotate credentials | – | C | R | I | – | – | **A** |
| Retire a workflow | C | **A** | R | R | I | I | C |

\* Legal is consulted only when the workflow produces text that leaves the hospital (notices, pliegos).

## 5. Review gate: before anything goes to production

A workflow goes live only when the business owner and the automation lead tick every line:

- [ ] **Owner named** in the workflow's notes, plus a backup owner.
- [ ] **Human decision point** before any action that commits the hospital; nothing goes to suppliers automatically.
- [ ] **Read-only by default.** Any write to a system of record is listed and approved by IT.
- [ ] **Decision log** writes who, when, the AI's suggestion and the human's choice.
- [ ] **Failure path.** An error workflow alerts the automation lead; a silent day is visible (e.g. "no answer" rows).
- [ ] **AI use stated**: which model, what data it sees (no patient data), prompt kept in version control.
- [ ] **Tested** on last month's real data and one deliberately bad input.
- [ ] **Rollback.** Deactivating the workflow leaves the old manual process working.
- [ ] **Control briefed** if it touches money, deadlines or legal notices.

Changes to a live workflow go through the same gate, lighter: the owner approves, the builder records what
changed and why.

## 6. Credentials policy

- **Credentials live only in n8n's credential store**, encrypted with the instance key. Never in workflow
  JSON, code or chat. Exported workflows carry no secrets.
- **Shared service accounts, not personal ones.** The digest is sent from a procurement mailbox, not a
  person's email (the demo used a personal Gmail; production must not).
- **Least privilege.** Each credential gets only the scope its workflow needs: read-only data access, send-only mail.
- **Separate dev and prod** credentials and instances; test data never runs on prod credentials.
- **Rotate** API keys every 90 days and immediately when someone with access leaves.
- **On-prem or EU hosting** as IT decides. With an enterprise plan, pull secrets from the hospital's
  vault (external secrets) instead of storing them in n8n.

## 7. Run and measure

| Measure | Target | Who looks |
|---|---|---|
| Digest items answered within 3 days | ≥ 80 % | Business owner, weekly |
| Override rate (human ≠ Claude) | 10–50 %, with reasons | Automation lead, monthly |
| Matcher precision on confirmed answers | ≥ 70 % | Automation lead, monthly |
| Contracts lapsing without a successor | Falling vs the baseline | Sponsor, quarterly |
| Failed runs not fixed within 1 working day | 0 | Automation lead |

## 8. Expansion signals (handed to Customer Success)

These signals mean the hospital is ready for more. Each is passed on as soon as it's seen, with evidence from the log:

| Signal | What it suggests |
|---|---|
| A second hospital or the regional service asks for the radar | Multi-tenant rollout; central purchasing as the buyer |
| Requesting units ask to add their own categories or alerts | Self-service intake; more builders; training |
| Control asks for access to the decision log | Audit use case; log streaming, longer retention |
| More than 3 business owners or 10 live workflows | Projects and role-based access; SSO |
| IT asks for separate dev and prod, or change control | Source control and environments |
| Pressure to keep secrets in the hospital vault | External secrets (enterprise plan) |
| Override rate stable, precision ≥ 70 % for a quarter | Move items from "decide" to "inform", widen the scope |
