"""Generate the n8n workflow JSON files (python3 workflows/build.py).

Kept as code so node versions and wiring are reviewable in a diff; the JSON files are what you import.
Node versions are checked against n8n 2.43.8.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

OUT = Path(__file__).parent
MODEL = "claude-sonnet-5-5"


def node(name, type_, version, pos, params, **extra):
    return {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"n8n-continuity/{name}")), "name": name, "type": type_,
            "typeVersion": version, "position": list(pos), "parameters": params, **extra}


def note(name, pos, w, h, text, color=None):
    p = {"content": text, "width": w, "height": h}
    if color:
        p["color"] = color
    return node(name, "n8n-nodes-base.stickyNote", 1, pos, p)


def main_link(*pairs):
    """pairs of (from, to[, from_output]) -> n8n connections dict."""
    conns: dict = {}
    for p in pairs:
        src, dst, out = (*p, 0)[:3]
        outs = conns.setdefault(src, {"main": []})["main"]
        while len(outs) <= out:
            outs.append([])
        outs[out].append({"node": dst, "type": "main", "index": 0})
    return conns


# ---------------------------------------------------------------- expiry radar

BRIEF_PROMPT = """=You help the procurement head of a Spanish public hospital avoid contracts lapsing without a successor.
Write in {{ $('Config').first().json.language }}. Use ONLY the facts below; if something is unknown, say so. No legal advice.
Name the contract by what it buys (e.g. 'Da Vinci maintenance'), never by its ref code. Write 're-tender' with a hyphen.

Contract: {{ $json.title }}
Contract ref: {{ $json.contract_ref }}
Ends (initial term): {{ $json.end_initial ?? 'unknown' }} | Max with extensions: {{ $json.end_max ?? 'unknown' }}
Annual budget (EUR): {{ $json.annual_budget ?? 'unknown' }} | Bids last time: {{ $json.min_bids ?? '?' }}–{{ $json.max_bids ?? '?' }}
Radar flag: {{ $json.flag }} (start_now = the start-by date has passed; verify = ended recently, successor uncertain)
Start-by date: {{ $json.start_by ?? 'unknown' }} = end minus typical lead time for this CPV ({{ $json.lead_days }} days, p80 of past tenders) minus {{ $json.prep_days }} days internal preparation (an assumption)
Successor match: {{ $json.successor_status }} (heuristic, confidence {{ $json.match_confidence }}){{ $json.successor_title ? ' – candidate: ' + $json.successor_title : '' }}

Pick one recommendation:
- start_retender: no successor and the timeline is tight
- confirm_extension: the max term is later than the initial end, so an extension may cover it
- check_successor: a successor may exist but the match is uncertain, or the contract already ended
- no_action: only if the facts clearly show it is covered

Reply with ONLY one JSON object, no code fence, no text before or after:
{"recommendation": "start_retender|confirm_extension|check_successor|no_action",
 "headline": "max 15 words", "why": "two sentences from the facts above",
 "next_step": "one concrete action with an owner", "confidence": "high|medium|low"}"""

PARSE_JS = r"""
// Read Claude's reply tolerantly. A reply that can't be read becomes a visible low-confidence
// "check successor" item on the form; it never silently drops a contract.
const allowed = { recommendation: ['start_retender', 'confirm_extension', 'check_successor', 'no_action'],
                  confidence: ['high', 'medium', 'low'] };
return $input.all().map((it, i) => {
  const contract = $('Top contracts').all()[i].json;
  const raw = String(it.json.text ?? it.json.output ?? '');
  let brief = null;
  try {
    const m = raw.replace(/```(?:json)?/g, '').match(/\{[\s\S]*\}/);
    brief = m ? JSON.parse(m[0]) : null;
    if (brief && typeof brief.output === 'object') brief = brief.output;   // Claude sometimes wraps it
  } catch (e) { brief = null; }
  const ok = brief && allowed.recommendation.includes(brief.recommendation) && brief.headline;
  if (!ok) brief = { recommendation: 'check_successor', confidence: 'low', headline: String(contract.title ?? '').slice(0, 90),
                     why: 'Claude\'s reply could not be read, so this needs a manual look.',
                     next_step: 'Procurement: check this contract by hand.' };
  if (!allowed.confidence.includes(brief.confidence)) brief.confidence = 'low';
  return { json: { ...contract, brief, brief_parsed: !!ok } };
});
"""

DIGEST_JS = r"""
// One weekly digest: one form with Claude's brief + a decision dropdown per contract.
const cfg = $('Config').first().json;
const meta = $('Fetch radar').first().json;
const briefs = $input.all().map((it, i) => ({ n: i + 1, ...it.json }));
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const label = { start_retender: 'Start re-tender', confirm_extension: 'Confirm extension',
                check_successor: 'Check successor', no_action: 'No action' };
const options = ['Start re-tender', 'Confirm extension', 'Dismiss', 'Needs checking'];

const fields = [];
for (const b of briefs) {
  fields.push({ fieldType: 'html', elementName: `brief_${b.n}`, html:
    `<h3>${b.n}. ${esc(b.brief.headline)}</h3>` +
    `<p><b>${esc(b.title)}</b><br>Ends ${esc(b.end_initial)} · start-by ${esc(b.start_by)} · ` +
    `${esc(b.flag)} · Claude suggests: <b>${esc(label[b.brief.recommendation])}</b> (${esc(b.brief.confidence)})</p>` +
    `<p>${esc(b.brief.why)}</p><p><i>Next step:</i> ${esc(b.brief.next_step)}</p>` +
    (b.link ? `<p><a href="${esc(b.link)}">Open on PLACSP</a></p>` : '') });
  fields.push({ fieldLabel: `Decision ${b.n}`, fieldType: 'dropdown', requiredField: true,
                fieldOptions: { values: options.map(option => ({ option })) } });
}
fields.push({ fieldLabel: 'Note for the team', fieldType: 'textarea', requiredField: false });

const lines = briefs.map(b => `${b.n}. ${b.brief.headline} (${b.flag}, start-by ${b.start_by ?? 'unknown'})`);
const message = [
  `${briefs.length} contracts at ${meta.name} need a decision this week.`,
  `Data: public PLACSP awards, radar as of ${meta.as_of}. Claude drafts, you decide; nothing is sent to suppliers.`,
  '', ...lines, '', 'Open the form below to decide on each one.',
].join('\n');

return [{ json: { subject: `Contract continuity: ${briefs.length} decisions (${meta.name})`, message,
                  formJson: JSON.stringify(fields), briefs, as_of: meta.as_of, hospital: meta.hospital,
                  approver: cfg.approver_email } }];
"""

ROWS_JS = r"""
// Turn the form answers into one decision row per contract (the audit trail).
const d = $('Build digest').first().json;
const answers = $input.first().json.data ?? {};
const decidedAt = $now.toISO();
return d.briefs.map(b => ({ json: {
  decided_at: decidedAt, hospital: d.hospital, radar_as_of: d.as_of,
  folder_id: b.contract_ref, title: b.title, flag: b.flag, start_by: b.start_by ?? '',
  claude_recommendation: b.brief.recommendation, claude_confidence: b.brief.confidence,
  decision: answers[`Decision ${b.n}`] ?? 'no answer', note: answers['Note for the team'] ?? '',
  decided_by: d.approver, execution_id: $execution.id, link: b.link ?? '',
} }));
"""


def expiry_radar() -> dict:
    nodes = [
        node("Every Monday 08:00", "n8n-nodes-base.scheduleTrigger", 1.2, (0, 0),
             {"rule": {"interval": [{"field": "weeks", "triggerAtDay": [1], "triggerAtHour": 8}]}}),
        node("Run now", "n8n-nodes-base.manualTrigger", 1, (0, 200), {}),
        node("Config", "n8n-nodes-base.set", 3.4, (240, 100), {"assignments": {"assignments": [
            {"id": "c1", "name": "radar_url", "type": "string",
             "value": "https://raw.githubusercontent.com/digvijaysingh-ai/n8n-continuity/main/snapshot/radar_H-f381.json"},
            {"id": "c2", "name": "approver_email", "type": "string", "value": "you@example.com"},
            {"id": "c3", "name": "max_decisions", "type": "number", "value": 5},
            {"id": "c4", "name": "language", "type": "string", "value": "English"},
        ]}, "options": {}}),
        node("Fetch radar", "n8n-nodes-base.httpRequest", 4.2, (480, 100),
             {"url": "={{ $json.radar_url }}",
              # raw.githubusercontent.com serves text/plain: force JSON parsing
              "options": {"timeout": 30000, "response": {"response": {"responseFormat": "json"}}}},
             retryOnFail=True, maxTries=3, waitBetweenTries=5000),
        node("One item per contract", "n8n-nodes-base.splitOut", 1, (720, 100), {"fieldToSplitOut": "items", "options": {}}),
        node("Needs a decision", "n8n-nodes-base.filter", 2.2, (960, 100), {"conditions": {
            "options": {"caseSensitive": True, "typeValidation": "strict", "version": 2},
            "combinator": "or", "conditions": [
                {"id": "f1", "leftValue": "={{ $json.flag }}", "rightValue": "start_now",
                 "operator": {"type": "string", "operation": "equals"}},
                {"id": "f2", "leftValue": "={{ $json.flag }}", "rightValue": "verify",
                 "operator": {"type": "string", "operation": "equals"}}]}, "options": {}}),
        node("Top contracts", "n8n-nodes-base.limit", 1, (1200, 100),
             {"maxItems": "={{ $('Config').first().json.max_decisions }}"}),
        node("Claude brief", "@n8n/n8n-nodes-langchain.chainLlm", 1.7, (1440, 100),
             {"promptType": "define", "text": BRIEF_PROMPT, "hasOutputParser": False}),
        node("Claude", "@n8n/n8n-nodes-langchain.lmChatAnthropic", 1.6, (1400, 320),
             {"model": {"__rl": True, "mode": "id", "value": MODEL},
              "options": {"temperature": 0.2, "maxTokensToSample": 1024}}),
        node("Parse brief", "n8n-nodes-base.code", 2, (1760, 100), {"jsCode": PARSE_JS.strip()}),
        node("Build digest", "n8n-nodes-base.code", 2, (2000, 100), {"jsCode": DIGEST_JS.strip()}),
        node("Ask procurement head", "n8n-nodes-base.gmail", 2.1, (2240, 100), {
            "resource": "message", "operation": "sendAndWait", "sendTo": "={{ $json.approver }}",
            "subject": "={{ $json.subject }}", "message": "={{ $json.message }}",
            "responseType": "customForm", "defineForm": "json", "jsonOutput": "={{ $json.formJson }}",
            "options": {"messageButtonLabel": "Open decision form",
                        "responseFormTitle": "Contract continuity – this week's decisions",
                        "responseFormButtonLabel": "Submit decisions",
                        "appendAttribution": False,
                        "limitWaitTime": {"values": {"limitType": "afterTimeInterval", "resumeAmount": 3,
                                                     "resumeUnit": "days"}}}}, webhookId=str(uuid.uuid4())),
        node("Decision rows", "n8n-nodes-base.code", 2, (2480, 100), {"jsCode": ROWS_JS.strip()}),
        node("Log decisions", "n8n-nodes-base.dataTable", 1, (2720, 100), {
            "resource": "row", "operation": "insert",
            "dataTableId": {"__rl": True, "mode": "name", "value": "continuity_decisions"},
            "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": [], "schema": []},
            "options": {}}),
        note("About", (-40, -380), 640, 330,
             "## Contract continuity: weekly expiry radar\n"
             "Finds contracts that will lapse without a successor and asks the procurement head to decide.\n\n"
             "**Data:** public PLACSP awards via Licita (read-only). Swap `radar_url` in Config for the live "
             "Licita API (`http://127.0.0.1:8787/radar?hospital=H-f381`) when self-hosted.\n\n"
             "**Guardrails:** Claude only drafts; a human decides every item; nothing goes to suppliers; "
             "every decision is logged with who, when and what Claude suggested.", "5"),
        note("Human in the loop", (2180, -280), 520, 250,
             "### One email, one form\nThe head gets one weekly digest, not five emails. Each contract shows "
             "Claude's brief and a required decision. If nobody answers in 3 days the run resumes and logs "
             "`no answer`, so silence is visible, not lost.", "4"),
        note("Audit trail", (2420, 320), 520, 220,
             "### Decision log\nData table `continuity_decisions`. One row per contract per week: decision, "
             "Claude's suggestion and confidence, who decided, execution id. That gives you the adoption metric "
             "and lets you check how often Claude's suggestion is overridden.", "6"),
    ]
    connections = main_link(
        ("Every Monday 08:00", "Config"), ("Run now", "Config"), ("Config", "Fetch radar"),
        ("Fetch radar", "One item per contract"), ("One item per contract", "Needs a decision"),
        ("Needs a decision", "Top contracts"), ("Top contracts", "Claude brief"),
        ("Claude brief", "Parse brief"), ("Parse brief", "Build digest"),
        ("Build digest", "Ask procurement head"), ("Ask procurement head", "Decision rows"),
        ("Decision rows", "Log decisions"))
    connections["Claude"] = {"ai_languageModel": [[{"node": "Claude brief", "type": "ai_languageModel", "index": 0}]]}
    return {"name": "Contract continuity – weekly expiry radar", "nodes": nodes, "connections": connections,
            "settings": {"executionOrder": "v1", "timezone": "Europe/Madrid", "saveManualExecutions": True},
            "pinData": {}, "tags": []}


if __name__ == "__main__":
    for fname, wf in {"expiry_radar.json": expiry_radar()}.items():
        (OUT / fname).write_text(json.dumps(wf, indent=2, ensure_ascii=False) + "\n")
        print("wrote", fname, len(wf["nodes"]), "nodes")
