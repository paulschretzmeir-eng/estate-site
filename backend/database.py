from dotenv import load_dotenv
load_dotenv()

import os
from supabase import create_client, Client

print("[database] Loading Supabase-based database module")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


class Database:
    """Database wrapper using the Supabase Python client.

    Provides a similar interface to the previous Database utility:
    - connect(): create Supabase client
    - get_cursor(): returns the client instance (used by callers)
    - commit(): no-op (Supabase is REST/transactionless for our use)
    - close(): clear client reference
    - insert_listing(): convenience helper to insert a listing
    """

    def __init__(self):
        self.client: Client | None = None

    def connect(self) -> bool:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("[database] SUPABASE_URL or SUPABASE_KEY not set in environment")
            return False

        try:
            print("[database] Creating Supabase client")
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("[database] Supabase client created")
            return True
        except Exception as e:
            print(f"[database] Supabase client creation failed: {e}")
            self.client = None
            return False

    def get_cursor(self):
        """Return the Supabase client as a replacement for cursor usage.

        Callers should use `client.table(...).insert(...).execute()` or
        `client.table(...).select(...).execute()`.
        """
        if not self.client:
            raise RuntimeError("Supabase client not connected")
        return self.client

    def commit(self):
        # Supabase operations are immediate; nothing to commit here.
        print("[database] commit() called (no-op for Supabase)")

    def close(self):
        # No explicit close on Supabase client; clear reference.
        self.client = None

    def insert_listing(self, listing: dict) -> dict:
        """Insert a listing dictionary into the `listings` table via Supabase.

        Returns the Supabase response object/dict.
        """
        if not self.client:
            raise RuntimeError("Supabase client not connected")

        print(f"[database] Inserting listing {listing.get('id')}")
        response = self.client.table("listings").insert(listing).execute()
        return response


# global instance
db = Database()
connected = db.connect()
print(f"[database] Connected: {connected}")
