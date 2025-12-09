import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/onchain_monitor",
        )
    )
    etherscan_api_key: str = field(
        default_factory=lambda: os.getenv("ETHERSCAN_API_KEY", "")
    )
    monitored_addresses: List[str] = field(default_factory=list)
    poll_interval_seconds: int = field(
        default_factory=lambda: int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    )

    def __post_init__(self):
        raw = os.getenv("MONITORED_ADDRESSES", "")
        if raw:
            self.monitored_addresses = [a.strip() for a in raw.split(",") if a.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
