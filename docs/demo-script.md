# Demo script (~3 minutes)

Goal: show a real agent doing real work over real data, with **two** MCP integrations visually
obvious — Fivetran (sync) and GitLab (action). Hit all four criteria: Technological Implementation,
Design, Potential Impact, Quality of Idea.

## Storyboard
1. **Hook (0:00–0:20)** — "Team discussions never become tracked work, and nobody can see who's
   overloaded." Show the dashboard with the five connected sources.
2. **Live sync (0:20–0:45)** — Click **Sync Now**. The **MCP Activity Log** lights up:
   `[Fivetran MCP] → sync_connector(gitlab) → success`. Call out the mandatory partner integration.
3. **The bridge — the money shot (0:45–1:40)** — Show the **Proposal Queue**: the agent read a Slack
   thread ("we should add rate-limiting to the auth endpoint") and drafted a GitLab issue with a
   suggested assignee (the *least-loaded* suitable dev). Click **Approve** →
   `[GitLab MCP] → create_issue → success`, and the real issue opens in GitLab, linked back to the
   thread. Emphasize: agent proposes, human approves, GitLab MCP acts.
4. **Observability (1:40–2:15)** — Workload Heatmap (who's overloaded) + Reliability Table (who
   consistently delivers vs lags). Tie back: that's *why* the agent picked that assignee.
5. **Chat with visible reasoning (2:15–2:50)** — Ask: "Why did the auth feature take so long?" The
   agent streams thinking + tool calls (BigQuery + GitLab) and answers with evidence (MR + ticket +
   meeting load).
6. **Close (2:50–3:00)** — Recap impact + stack (Google Cloud Agent Builder + Gemini 3 + Fivetran MCP
   + GitLab MCP).

## Pre-demo checklist
- [ ] Connectors synced with realistic data (incl. a clearly actionable Slack/Jira thread)
- [ ] One genuinely "stuck" MR and one overloaded dev in the data
- [ ] At least one pending issue proposal queued and ready to approve live
- [ ] GitLab project reachable; the create_issue call works end-to-end
- [ ] Hosted Cloud Run URL loads cleanly
- [ ] MCP log scrolls visibly during sync + approval + chat (both servers appear)
