import asyncio
import json
import os
import logging
from aiohttp import web

log = logging.getLogger("dashboard")

HTML = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CoC Bot Dashboard</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: monospace; background: #0f0f0f; color: #e0e0e0; padding: 20px; }
  h1 { color: #f0a500; font-size: 20px; margin-bottom: 16px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px; }
  .card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 14px; }
  .card-label { font-size: 11px; color: #888; margin-bottom: 6px; }
  .card-value { font-size: 26px; color: #f0a500; }
  .log { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 14px; height: 400px; overflow-y: auto; }
  .log-line { font-size: 12px; padding: 3px 0; border-bottom: 1px solid #222; }
  .log-line.ok { color: #4caf50; }
  .log-line.warn { color: #ff9800; }
  .log-line.error { color: #f44336; }
  .badge { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 12px; }
  .badge-run { background: #1b5e20; color: #a5d6a7; }
  .badge-idle { background: #333; color: #aaa; }
  .header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
</style>
</head>
<body>
<div class="header">
  <h1>⚔ CoC Bot</h1>
  <span class="badge" id="status-badge">loading...</span>
</div>
<div class="grid">
  <div class="card"><div class="card-label">Territories</div><div class="card-value" id="m-terr">—</div></div>
  <div class="card"><div class="card-label">Attacks</div><div class="card-value" id="m-atk">—</div></div>
  <div class="card"><div class="card-label">Balance</div><div class="card-value" id="m-bal">—</div></div>
  <div class="card"><div class="card-label">Quest</div><div class="card-value" id="m-quest">—</div></div>
  <div class="card"><div class="card-label">Mode</div><div class="card-value" id="m-mode" style="font-size:16px;margin-top:4px">—</div></div>
</div>
<div class="log" id="log-box"></div>
<script>
async function refresh() {
  const r = await fetch('/status');
  const d = await r.json();
  document.getElementById('m-terr').textContent = d.territories;
  document.getElementById('m-atk').textContent = d.attacks;
  document.getElementById('m-bal').textContent = d.balance;
  document.getElementById('m-quest').textContent = d.quest + '/50';
  document.getElementById('m-mode').textContent = d.mode;
  const badge = document.getElementById('status-badge');
  badge.textContent = d.status.toUpperCase();
  badge.className = 'badge ' + (d.status === 'running' ? 'badge-run' : 'badge-idle');
  const box = document.getElementById('log-box');
  box.innerHTML = d.logs.map(l => {
    let cls = '';
    if (l.includes('[INFO]') && l.includes('✓')) cls = 'ok';
    else if (l.includes('[WARN]')) cls = 'warn';
    else if (l.includes('[ERROR]')) cls = 'error';
    else if (l.includes('✓') || l.includes('berhasil')) cls = 'ok';
    return '<div class="log-line ' + cls + '">' + l + '</div>';
  }).join('');
}
refresh();
setInterval(refresh, 5000);
</script>
</body>
</html>"""

async def run_dashboard(farmer):
    app = web.Application()

    async def index(req):
        return web.Response(text=HTML, content_type="text/html")

    async def status(req):
        return web.Response(
            text=json.dumps({
                "status": farmer.status,
                "territories": farmer.territories,
                "attacks": farmer.attacks,
                "balance": farmer.balance,
                "quest": farmer.quest_progress,
                "mode": farmer.mode,
                "logs": farmer.logs[:50],
            }),
            content_type="application/json"
        )

    app.router.add_get("/", index)
    app.router.add_get("/status", status)

    port = int(os.getenv("PORT", "8080"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    log.info(f"Dashboard berjalan di http://0.0.0.0:{port}")
    await asyncio.Event().wait()
