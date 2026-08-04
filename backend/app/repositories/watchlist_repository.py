from app.core.config import get_settings
from app.core.database import get_supabase


class WatchlistRepository:
    def __init__(self) -> None:
        self.supabase = get_supabase()
        self.settings = get_settings()

    def get_or_create_main_watchlist(self) -> dict:
        response = (
            self.supabase
            .table("watchlists")
            .select("id,name")
            .eq("user_id", self.settings.dev_user_id)
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]

        created = (
            self.supabase
            .table("watchlists")
            .insert(
                {
                    "user_id": self.settings.dev_user_id,
                    "name": "Main Watchlist",
                }
            )
            .execute()
        )

        if not created.data:
            raise RuntimeError(
                "Could not create the default watchlist"
            )

        return created.data[0]

    def list_items(
        self,
        watchlist_id: str,
    ) -> list[dict]:
        response = (
            self.supabase
            .table("watchlist_items")
            .select("id,ticker")
            .eq("watchlist_id", watchlist_id)
            .order("added_at")
            .execute()
        )

        return response.data or []

    def add_item(
        self,
        watchlist_id: str,
        ticker: str,
    ) -> dict:
        clean_ticker = ticker.strip().upper()

        response = (
            self.supabase
            .table("watchlist_items")
            .insert(
                {
                    "watchlist_id": watchlist_id,
                    "ticker": clean_ticker,
                }
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Could not add the watchlist item"
            )

        return response.data[0]

    def remove_item(
        self,
        item_id: str,
    ) -> bool:
        response = (
            self.supabase
            .table("watchlist_items")
            .delete()
            .eq("id", item_id)
            .execute()
        )

        return bool(response.data)


watchlist_repository = WatchlistRepository()