# Demo script (~3 minutes)

Goal: show a real agent doing real work over real data, with the Fivetran MCP integration
visually obvious. Judging criteria to hit: Technological Implementation, Design, Potential
Impact, Quality of Idea.

## Storyboard
1. **Hook (0:00–0:20)** — "Developers can't see their own productivity blind spots." Show the
   dashboard landing with the four connected sources.
2. **Live sync (0:20–0:50)** — Click **Sync Now** on GitHub. The **MCP Activity Log** lights up:
   `[Fivetran MCP] → sync_connector(github) → success`. Call out the partner integration.
3. **Sprint health (0:50–1:30)** — Walk the three charts: PR review lag (a stuck PR + the
   bottleneck reviewer), deep work vs meetings, estimation accuracy.
4. **Proactive alert (1:30–2:00)** — Show an alert that appeared on its own: "3 high-risk tickets
   entering sprint planning." Emphasize *proactive*, not asked-for.
5. **Chat with visible reasoning (2:00–2:45)** — Ask: "Why did the auth feature take so long last
   month?" Show the agent's thinking + tool calls (BigQuery + MCP) streaming, ending in an
   evidence-backed answer.
6. **Close (2:45–3:00)** — Recap impact + stack (Google Cloud Agent Builder + Gemini 3 + Fivetran
   MCP).

## Pre-demo checklist
- [ ] Connectors synced with realistic data
- [ ] At least one genuinely "stuck" PR and one underestimated ticket in the data
- [ ] One proactive alert pre-generated and visible
- [ ] Hosted Cloud Run URL loads cleanly
- [ ] MCP log scrolls visibly during the sync + chat
