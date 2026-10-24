// Live API base. Empty = same origin (when served by server.py). Override with ?api=https://your-tunnel
window.MEDMATCH_LIVE_URL = new URLSearchParams(location.search).get("api") || "";
