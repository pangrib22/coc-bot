import aiohttp
import logging

log = logging.getLogger("api")

BASE = "https://api.clashofcoins.com/api"

class CoCAPI:
    def __init__(self, token: str):
        self.token = token if token.startswith("Bearer ") else f"Bearer {token}"
        self.headers = {
            "Authorization": self.token,
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": "https://clashofcoins.com",
            "Referer": "https://clashofcoins.com/",
        }
        self.session = None

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def get(self, path: str) -> dict:
        session = await self._get_session()
        url = BASE + path
        try:
            async with session.get(url) as r:
                if r.status == 200:
                    return await r.json()
                log.warning(f"GET {path} -> HTTP {r.status}")
                return {}
        except Exception as e:
            log.error(f"GET {path} error: {e}")
            return {}

    async def post(self, path: str, body: dict = {}) -> dict:
        session = await self._get_session()
        url = BASE + path
        try:
            async with session.post(url, json=body) as r:
                text = await r.text()
                if r.status in (200, 201):
                    try:
                        return await r.json(content_type=None)
                    except:
                        return {"ok": True}
                log.warning(f"POST {path} -> HTTP {r.status}: {text[:100]}")
                return {}
        except Exception as e:
            log.error(f"POST {path} error: {e}")
            return {}

    # ── Endpoint-endpoint utama ──────────────────────────────────────

    async def get_balance(self) -> dict:
        return await self.get("/balances?fields=points,softCurrency,technologyRes")

    async def get_user(self) -> dict:
        return await self.get("/leaderboard/user")

    async def get_daily_activity(self) -> dict:
        return await self.get("/user-daily-game-activity")

    async def get_lobby(self) -> dict:
        return await self.get("/game-lobby?isBaseMiniApp=false")

    async def get_inventory(self) -> dict:
        return await self.get("/game-inventory")

    async def claim_daily(self) -> dict:
        return await self.post("/daily")

    async def get_all_provinces(self) -> dict:
        # Endpoint ini muncul di screenshot: "all?isBaseMiniApp=false"
        return await self.get("/all?isBaseMiniApp=false")

    async def capture_province(self, province_id: int) -> dict:
        # Endpoint capture - perlu dikonfirmasi dari network tab
        return await self.post(f"/game/province/{province_id}/capture")

    async def build_structure(self, province_id: int, slot: int, structure_id: int) -> dict:
        # Terlihat dari console log: Building Slot[1] Structure ID: 2 in Province: 783
        return await self.post(f"/game/province/{province_id}/build", {
            "slot": slot,
            "structureId": structure_id
        })

    async def upgrade_structure(self, province_id: int, structure_id: int) -> dict:
        return await self.post(f"/game/province/{province_id}/upgrade", {
            "structureId": structure_id
        })

    async def attack_province(self, province_id: int) -> dict:
        return await self.post(f"/game/province/{province_id}/attack")
