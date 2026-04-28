from api import CoCAPI
from farmer import Farmer
from dashboard import run_dashboard

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("main")

async def main():
    token = os.getenv("BEARER_TOKEN", "")
    if not token:
        log.error("BEARER_TOKEN belum diset! Tambahkan ke Railway Variables.")
        return

    mode = os.getenv("BOT_MODE", "free")       # free / attack
    interval = int(os.getenv("BOT_INTERVAL", "30"))  # detik antar aksi
    max_terr = int(os.getenv("MAX_TERRITORIES", "50"))

    log.info(f"=== Clash of Coins Bot ===")
    log.info(f"Mode: {mode} | Interval: {interval}s | Max territories: {max_terr}")

    api = CoCAPI(token)
    farmer = Farmer(api, mode=mode, max_territories=max_terr)

    # Jalankan dashboard web + loop bot bersamaan
    await asyncio.gather(
        run_dashboard(farmer),
        farmer.run_loop(interval)
    )

if __name__ == "__main__":
    asyncio.run(main())
