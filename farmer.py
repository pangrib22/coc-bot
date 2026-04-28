import asyncio
import logging
from datetime import datetime
from api import CoCAPI

log = logging.getLogger("farmer")

class Farmer:
    def __init__(self, api: CoCAPI, mode: str = "free", max_territories: int = 50):
        self.api = api
        self.mode = mode
        self.max_territories = max_territories
        self.territories = 0
        self.attacks = 0
        self.balance = "—"
        self.quest_progress = 0
        self.status = "idle"
        self.logs = []
        self.running = False
        self.room_id = None

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
        result = await self.api.claim_daily()
        if result and result.get("ok"):
            self._log("Daily reward berhasil di-claim!")
        else:
            self._log("Daily reward belum tersedia atau sudah di-claim", "WARN")

    async def get_room(self):
        """Ambil room yang tersedia dari lobby"""
        self._log("Mencari room...")
        lobby = await self.api.get_lobby()
        if not lobby:
            self._log("Gagal ambil lobby", "WARN")
            return None
        rooms = lobby.get("rooms") or []
        if not rooms:
            self._log("Tidak ada room tersedia", "WARN")
            return None
        # Pilih room dengan slot terbanyak
        room = max(rooms, key=lambda r: r.get("availableSlots", 0))
        self.room_id = room.get("roomId")
        self._log(f"Room: {room.get('roomName')} | Slots: {room.get('availableSlots')}/{room.get('slotsCapacity')}")
        return room

    async def farm_free_territories(self):
        if self.territories >= self.max_territories:
            self._log(f"Sudah capai max territories ({self.max_territories})", "WARN")
            return

        room = await self.get_room()
        if not room:
            return

        room_id = room.get("roomId")
        available = room.get("availableSlots", 0)
        self._log(f"Mencari territory kosong di room {room_id}... ({available} slot tersedia)")

        # Coba capture slot yang tersedia di room ini
        claimed = 0
        for i in range(min(available, 10)):
            result = await self.api.post(f"/game/room/{room_id}/province/capture", {})
            if result and (result.get("id") or result.get("provinceId") or result.get("ok")):
                self.territories += 1
                claimed += 1
                prov_id = result.get("id") or result.get("provinceId", "?")
                self._log(f"✓ Captured province #{prov_id} ({self.territories} total)")
                await asyncio.sleep(1)
                # Build tower
                await self.api.post(f"/game/room/{room_id}/province/{prov_id}/build", {"slot": 1, "structureId": 2})
                self._log(f"  └─ Built tower di #{prov_id}")
            else:
                self._log(f"✗ Capture gagal di slot {i+1}", "WARN")
                break
            await asyncio.sleep(1.5)

        if claimed == 0:
            self._log("Tidak ada territory berhasil di-claim saat ini")
        else:
            self._log(f"Total di-claim sesi ini: {claimed} territories")

    async def attack_territories(self):
        self._log("Mode attack: mencari target...")
        room = await self.get_room()
        if not room:
            return
        room_id = room.get("roomId")
        # Ambil data provinces di room
        data = await self.api.get(f"/game/room/{room_id}/provinces")
        provinces = data if isinstance(data, list) else data.get("provinces", []) if isinstance(data, dict) else []
        targets = [p for p in provinces if p.get("ownerId") and p.get("ownerId") != "me"][:5]
        self._log(f"Ditemukan {len(targets)} target")
        for target in targets:
            prov_id = target.get("id") or target.get("provinceId")
            result = await self.api.post(f"/game/room/{room_id}/province/{prov_id}/attack", {})
            if result:
                self.attacks += 1
                self._log(f"⚔ Attack #{prov_id} berhasil!")
            else:
                self._log(f"✗ Attack #{prov_id} gagal", "WARN")
            await asyncio.sleep(2)

    async def run_once(self):
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
        self.running = True
        self._log(f"Bot dimulai. Interval: {interval_seconds}s, Mode: {self.mode}")
        while self.running:
            try:
                await self.run_once()
            except Exception as e:
                self._log(f"Error di loop: {e}", "ERROR")
            self._log(f"Menunggu {interval_seconds} detik...")
            await asyncio.sleep(interval_seconds)
