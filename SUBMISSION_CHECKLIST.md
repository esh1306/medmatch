# Submission checklist (audited 24 Oct 2026 ~08:40 BST)

| # | Requirement | Done? | Evidence |
|---|---|---|---|
| 1 | Side quest: show the best thing Sapling can do (semantic verification / anomaly identification) | Yes | Sapling verifies each care-chart line against the current prescription; catches stopped-still-given, replace-not-add, wrong dose (Burgess 4ml vs 10ml caught by Sapling alone, 0.84) |
| 2 | Sapling doing the hard part, not a chat box | Yes | 22 Sapling calls per full run, one per medicine x chart; LLM only normalises; no chat UI. Rule check is labelled separately as code |
| 3 | Demo where we watch it work on a realistic input | Yes | Streamlit app streams each Sapling verdict live; messy synthetic records rebuilt from 3 coroner reports (2024-2026). Screenshots in `screenshots/` |
| 4 | Use exact Sapling endpoint from official quickstart | Yes | `judge.py`: `SAPLING_URL = "https://6adbee0669a00298cd4774c9.endpoints.huggingface.cloud"`, payload `{"inputs":{"policy","evidence","claim"}}` |
| 5 | Main brief: route LLM calls through the Mubit gateway | Yes | `normalise.py`: OpenAI SDK, `base_url="https://api.mubit.ai/openai/v1"` (docs.mubit.ai quickstart: OpenAI base `https://api.mubit.ai/openai/v1`, Anthropic `https://api.mubit.ai/anthropic`, Gemini `https://api.mubit.ai/gemini`) |
| 6 | Correct model naming | Yes | Docs: "Your model IDs stay the same", no Mubit model ID. We send `gpt-4o-mini` (accepted; no `400 starter_credit_model`). Docs' starter-credit example uses `gpt-6-luna` |
| 7 | Correct headers | Yes | Auth = Mubit key as the OpenAI `api_key` (Bearer). Optional `x-middleware-store` / `x-middleware-record` not needed |
| 8 | Proof calls went through Mubit | Yes | Every response carried `x-middleware-request-id` (Mubit's call ID, `mreq_` + 32 hex), stored in `data/results/*.json`, e.g. `mreq_01a16cd5abef7a4192ae76aa97febc3c`. GAP: not cross-checked in the Mubit console (needs Sahid's login) |
| 9 | Key never exposed | Yes | Read from file at runtime only; errors reduced to class+status; `.gitignore` has `.secrets/`, `.env`, `.venv/`; script scan of tree + git history: key not found |
| 10 | Post on X with the task + demo video (<=2 min) or screenshots, tag @MubitLabs | NO (draft) | `POSTS.md` draft. Sahid must record video / attach screenshots and post |
| 11 | Post on LinkedIn, tag Mubit | NO (draft) | `POSTS.md` draft. Sahid must post |
| 12 | Post in side-quests by 10:30 with team name, one-line task, both post links, repo link | NO (draft) | Template in `POSTS.md`. Needs team name + links |
| 13 | Public repo | NO (blocked) | Connected GitHub account is `esh1306` (Eshita Agarwal), not Sahid; cursor-github connector also has no create-repo tool. Not pushed pending Sahid's decision |
| 14 | Video up to 2 min | NO | Script in `POSTS.md` (90 s) |
