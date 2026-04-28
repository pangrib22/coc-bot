import asyncio
import logging
from datetime import datetime
from bot.api import CoCAPI

log = logging.getLogger("farmer")

class Farmer:
    def __init__(self, api: CoCAPI, mode: str = "free", max_territories: int = 50):
        self.api = api
        self.mode = mode
        self.max_territories = max_territories

        # Stats untuk dashboard
        self.territories = 0
        self.attacks = 0
        self.balance = "—"
        self.quest_progress = 0
        self.status = "idle"
        self.logs = []
        self.running = False

    def _log(self, msg: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{level}] {msg}"
        self.logs.insert(0, entry)
        if len(self.logs) > 200:
            self.logs.pop()
        if level == "ERROR":
            log.error(msg)
        elif level == "WARN":
            log.warning(msg)
        else:
            log.info(msg)

    async def refresh_stats(self):
        """Ambil stats terbaru dari API"""
        self._log("Refresh stats...")

        bal = await self.api.get_balance()
        if bal:
            self.balance = bal.get("softCurrency") or bal.get("points") or "—"
            self._log(f"Balance: {self.balance} coins")

        activity = await self.api.get_daily_activity()
        if activity:
            self.quest_progress = activity.get("capturedLands", 0) or activity.get("captured", 0)
            self._log(f"Quest: {self.quest_progress}/50 lands captured")

    async def claim_daily_reward(self):
        """Claim reward harian jika tersedia"""
        result = await self.api.claim_daily()
        if result:
            self._log("Daily reward berhasil di-claim!", "INFO")
        else:
            self._log("Daily reward belum tersedia atau sudah di-claim", "WARN")

    async def farm_free_territories(self):
        """Claim semua territory kosong yang tersedia"""
        if self.territories >= self.max_territories:
            self._log(f"Sudah capai max territories ({self.max_territories})", "WARN")
            return

        self._log("Mencari territory kosong...")
        data = await self.api.get_all_provinces()

        provinces = []
        if isinstance(data, list):
            provinces = data
        elif isinstance(data, dict):
            provinces = data.get("provinces") or data.get("regions") or data.get("data") or []

        free = [p for p in provinces if not p.get("ownerId") and not p.get("owner")]
        self._log(f"Ditemukan {len(free)} territory kosong")

        claimed = 0
        for prov in free[:10]:  # max 10 per tick supaya tidak kena rate limit
            prov_id = prov.get("id") or prov.get("provinceId")
            if not prov_id:
                continue
            result = await self.api.capture_province(prov_id)
            if result:
                self.territories += 1
                claimed += 1
                self._log(f"✓ Captured province #{prov_id} ({self.territories} total)")
                # Auto build tower setelah capture
                await asyncio.sleep(1)
                await self.api.build_structure(prov_id, slot=1, structure_id=2)
                self._log(f"  └─ Built tower di #{prov_id}")
            else:
                self._log(f"✗ Gagal capture #{prov_id}", "WARN")
            await asyncio.sleep(1.5)  # jeda antar request

        if claimed == 0:
            self._log("Tidak ada territory berhasil di-claim saat ini")
        else:
            self._log(f"Total di-claim sesi ini: {claimed} territories")

    async def attack_territories(self):
        """Serang territory musuh"""
        self._log("Mode attack: mencari target...")
        data = await self.api.get_all_provinces()

        provinces = []
        if isinstance(data, list):
            provinces = data
        elif isinstance(data, dict):
            provinces = data.get("provinces") or data.get("regions") or []

        # Cari milik orang lain (bukan kosong)
        targets = [p for p in provinces if p.get("ownerId") and p.get("ownerId") != "me"][:5]
        self._log(f"Ditemukan {len(targets)} target untuk diserang")

        for target in targets:
            prov_id = target.get("id") or target.get("provinceId")
            result = await self.api.attack_province(prov_id)
            if result:
                self.attacks += 1
                self._log(f"⚔ Attack province #{prov_id} berhasil!")
            else:
                self._log(f"✗ Attack #{prov_id} gagal", "WARN")
            await asyncio.sleep(2)

    async def run_once(self):
        """Satu siklus bot"""
        self.status = "running"
        self._log("=== Mulai siklus bot ===")

        await self.refresh_stats()
        await self.claim_daily_reward()
        await self.farm_free_territories()

        if self.mode == "attack":
            await self.attack_territories()

        self.status = "idle"
        self._log("=== Siklus selesai ===")

    async def run_loop(self, interval_seconds: int = 30):
        """Loop utama bot"""
        self.running = True
        self._log(f"Bot dimulai. Interval: {interval_seconds}s, Mode: {self.mode}")
        while self.running:
            try:
                await self.run_once()
            except Exception as e:
                self._log(f"Error di loop: {e}", "ERROR")
            self._log(f"Menunggu {interval_seconds} detik...")
            await asyncio.sleep(interval_seconds)
