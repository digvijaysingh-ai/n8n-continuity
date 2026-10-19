# Running the expiry radar on n8n Cloud

About 10 minutes. You do the credential steps yourself (the API key and Google sign-in).

1. **Create the decision log.** Overview → Data tables → Create → name `continuity_decisions`.
   Add these columns, all of type *string*:
   `decided_at, hospital, radar_as_of, folder_id, title, flag, start_by, claude_recommendation,
   claude_confidence, decision, note, decided_by, execution_id, link`
2. **Import the workflow.** Create workflow → `…` menu (top right) → *Import from File* →
   `workflows/expiry_radar.json`.
3. **Claude credential.** Open the **Claude** node → Credential → *Create new* → paste your Anthropic
   API key. Model is `claude-sonnet-5-5`; change it in the node if your key can't use it.
4. **Gmail credential.** Open **Ask procurement head** → Credential → *Create new* → *Sign in with Google*.
5. **Config node.** Set `approver_email` to your own address. `radar_url` points to the public snapshot
   (`snapshot/radar_H-f381.json`); self-hosted, use `http://127.0.0.1:8787/radar?hospital=H-f381`.
6. **Run it.** *Execute workflow*. The run pauses at **Ask procurement head**; open the email, click
   *Open decision form*, choose a decision for each contract, submit. The run resumes and writes
   5 rows to `continuity_decisions`.
7. **Screenshot** the canvas after a green run (the screenshot the application asks for), plus the
   form and the Data table.

Verified end to end on n8n Cloud (2026-10-19): fetch → Claude briefs (n8n gateway credits) → Gmail
form → 5 rows in `continuity_decisions`. Data is anonymised: hospital code H-f381, contract refs C-….
