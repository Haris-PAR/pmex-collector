"""
PMEX Agriculture Crop Data Collector
=====================================
Fetches agriculture crop data from the PMEX API and stores snapshots
in a SQLite database for volume analysis and key metrics.

Targets:
    - Category "Agri"     → International (ICORN, ICOTTON, ICOTTON50K, ISOYBEAN, IWHEAT)
    - Category "Phy_Agri" → Domestic     (LGMRRICE, MAIZELD, SUGAR, WHEAT, PKWHEATLD, PALMOLEIN)

Active contracts are detected by: Bid > 0 OR Ask > 0.

Usage:
    python crop_collector.py              # single fetch
    python crop_collector.py --force      # ignore market-hours check
    python crop_collector.py --status     # show DB stats
"""

import os
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from main import fetch_pmex
from data import (
    COMMODITY_CODES,
    parse_pmex_symbol,
    trading_schedule,
    symbol_to_category,
)

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent / "pmex_crops.db"
PST = ZoneInfo("Asia/Karachi")  # Pakistan Standard Time (UTC+5)

# API response categories we care about
TARGET_CATEGORIES = {"Agri", "Phy_Agri"}

# Numeric contract sizes for volume → commodity unit conversion
CONTRACT_SIZES: dict[str, tuple[float, str]] = {
    "ICORN":      (5000,  "bushels"),
    "ICOTTON":    (5000,  "pounds"),
    "ICOTTON50K": (50000, "pounds"),
    "ISOYBEAN":   (5000,  "bushels"),
    "IWHEAT":     (5000,  "bushels"),
    "LGMRRICE":   (10,    "MT"),
    "SUGAR":      (12,    "MT"),
    "MAIZELD":    (10,    "MT"),
    "MAIZESD":    (10,    "MT"),
    "PKWHEATSD":  (10,    "MT"),
    "PKWHEATLD":  (10,    "MT"),
    "WHEAT":      (10,    "MT"),
    "PALMOLEIN":  (25,    "MT"),
}

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("crop_collector")


# ─────────────────────────────────────────────────────────────────────────────
# Database setup
# ─────────────────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS crop_snapshots (
    id                INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    fetch_time        TIMESTAMP NOT NULL,
    fetch_date        DATE NOT NULL,

    contract          TEXT NOT NULL,
    commodity_code    TEXT NOT NULL,
    commodity_name    TEXT,
    asset_class       TEXT,
    category          TEXT NOT NULL,

    contract_size     DOUBLE PRECISION,
    size_unit         TEXT,
    price_unit        TEXT,

    bid               DOUBLE PRECISION,
    ask               DOUBLE PRECISION,
    open_price        DOUBLE PRECISION,
    high              DOUBLE PRECISION,
    low               DOUBLE PRECISION,
    close_price       DOUBLE PRECISION,
    last_price        DOUBLE PRECISION,

    last_volume       INTEGER,
    total_volume      INTEGER,

    change_val        DOUBLE PRECISION,
    change_pct        DOUBLE PRECISION,

    spread            DOUBLE PRECISION,
    spread_pct        DOUBLE PRECISION,

    commodity_volume  DOUBLE PRECISION,
    api_datetime      BIGINT,

    UNIQUE(fetch_time, contract)
);

CREATE INDEX IF NOT EXISTS idx_crop_date
    ON crop_snapshots (commodity_code, fetch_date);

CREATE INDEX IF NOT EXISTS idx_contract_time
    ON crop_snapshots (contract, fetch_time);

CREATE INDEX IF NOT EXISTS idx_fetch_date
    ON crop_snapshots (fetch_date);


CREATE TABLE IF NOT EXISTS fetch_log (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    fetch_time          TIMESTAMP NOT NULL UNIQUE,

    contracts_found     INTEGER,
    active_stored       INTEGER,
    skipped_inactive    INTEGER,

    status              TEXT,
    error_message       TEXT
);
"""


def _get_conn() -> connection:
    """Open a psycopg2 connection using DATABASE_URL env var (Supabase/prod)
    or individual env vars (local dev fallback)."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return psycopg2.connect(url)
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database=os.environ.get("DB_NAME", "pmex"),
        user=os.environ.get("DB_USER", "harry"),
        password=os.environ.get("DB_PASSWORD", "harry"),
    )


def init_db() -> connection:
    """Create schema if needed, return an open connection."""
    conn = _get_conn()
    cur = conn.cursor()
    for statement in SCHEMA_SQL.strip().split(";"):
        if statement.strip():
            cur.execute(statement)
    conn.commit()
    return conn


# ─────────────────────────────────────────────────────────────────────────────
# Market hours helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_time_12h(time_str: str) -> tuple[int, int]:
    """Parse '04:30 AM' → (4, 30), '03:00 AM' (next day close) → (3, 0)."""
    dt = datetime.strptime(time_str.strip(), "%I:%M %p")
    return dt.hour, dt.minute


def is_weekday(now: datetime) -> bool:
    """Check if current day is a weekday (Mon-Fri)."""
    return now.weekday() < 5  # 0=Mon, 4=Fri


def any_agri_session_open(now: datetime) -> bool:
    """
    Check if ANY agriculture-related trading session is currently open.

    Uses the trading_schedule from data.py for international contracts.
    For domestic physical agri (not in schedule), we assume they trade
    during standard hours (roughly 10 AM - 10 PM PST weekdays), but
    we don't hard-filter them — the API's Bid/Ask=0 handles it.

    Returns True if at least one session could be active, or if we can't
    determine (safe to fetch and let API filter).
    """
    if not is_weekday(now):
        return False

    day_name = now.strftime("%A")

    # Check known international agri schedules from data.py
    agri_categories = {"ICotton", "Grains_Group_(ISoybean_ICorn_IWheat)"}

    for cat_name in agri_categories:
        if cat_name not in trading_schedule:
            continue
        day_sched = trading_schedule[cat_name].get(day_name)
        if not day_sched:
            continue

        # Use "revised" times
        revised = day_sched.get("revised", day_sched.get("existing", {}))
        open_h, open_m = _parse_time_12h(revised["open"])
        close_h, close_m = _parse_time_12h(revised["close"])

        open_time = now.replace(hour=open_h, minute=open_m, second=0, microsecond=0)

        # Handle overnight sessions: close time is next day
        if (close_h, close_m) < (open_h, open_m):
            # e.g., open 03:30 AM, close 11:00 PM same day → NOT overnight
            # e.g., open 03:00 AM, close 02:00 AM → IS overnight
            close_time = now.replace(hour=close_h, minute=close_m, second=0, microsecond=0)
            if close_h < 12 and open_h < 12 and close_h < open_h:
                # Overnight: close is next day
                close_time += timedelta(days=1)
            elif close_h < open_h:
                close_time += timedelta(days=1)
        else:
            close_time = now.replace(hour=close_h, minute=close_m, second=0, microsecond=0)

        if open_time <= now <= close_time:
            return True

    # For domestic agri: check if within generous 09:00-22:00 PST window
    domestic_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    domestic_close = now.replace(hour=22, minute=0, second=0, microsecond=0)
    if domestic_open <= now <= domestic_close:
        return True

    return False


# ─────────────────────────────────────────────────────────────────────────────
# Data processing
# ─────────────────────────────────────────────────────────────────────────────

def _safe_float(val) -> float | None:
    """Convert a value to float, returning None for empty/null/invalid."""
    if val is None:
        return None
    try:
        f = float(val)
        return f if f != 0 else None
    except (ValueError, TypeError):
        return None


def _safe_float_keep_zero(val) -> float | None:
    """Convert to float, keeping 0 as a valid value (only None → None)."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _safe_int(val) -> int | None:
    """Convert a value to int, returning None for empty/null/invalid."""
    if val is None:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def process_contract(item: dict, fetch_ts: str, fetch_date: str) -> dict | None:
    """
    Process a single API contract item into a row for crop_snapshots.

    Returns None if the contract is inactive (Bid=0 AND Ask=0).
    """
    bid = _safe_float_keep_zero(item.get("Bid"))
    ask = _safe_float_keep_zero(item.get("Ask"))

    # Active check: skip if both Bid and Ask are 0 or None
    if (bid is None or bid == 0) and (ask is None or ask == 0):
        return None

    contract = item.get("Contract", "").strip()
    if not contract:
        return None

    # Parse symbol for enrichment
    parsed = parse_pmex_symbol(contract)
    commodity_code = parsed.get("commodity_code", "UNKNOWN")
    commodity_name = parsed.get("commodity_name", "Unknown")
    asset_class = parsed.get("asset_class", "Unknown")
    price_unit = parsed.get("price_unit", "Unknown")

    # Contract size lookup
    size_val, size_unit = CONTRACT_SIZES.get(commodity_code, (None, None))

    # Price fields
    open_price = _safe_float(item.get("Open"))
    high = _safe_float(item.get("High"))
    low = _safe_float(item.get("Low"))
    close_price = _safe_float_keep_zero(item.get("Close"))
    last_price = _safe_float(item.get("Last_Price"))
    last_volume = _safe_int(item.get("Last_Vol"))
    total_volume = _safe_int(item.get("Total_Vol"))
    change_val = _safe_float_keep_zero(item.get("Change"))
    change_pct = _safe_float_keep_zero(item.get("Change_Per"))
    category = item.get("Category", "")
    api_datetime = item.get("_datetime")

    # Computed fields
    spread = None
    spread_pct = None
    if bid is not None and ask is not None and bid > 0 and ask > 0:
        spread = round(ask - bid, 6)
        midpoint = (ask + bid) / 2
        if midpoint > 0:
            spread_pct = round((spread / midpoint) * 100, 4)

    commodity_volume = None
    if total_volume is not None and size_val is not None:
        commodity_volume = total_volume * size_val

    return {
        "fetch_time":       fetch_ts,
        "fetch_date":       fetch_date,
        "contract":         contract,
        "commodity_code":   commodity_code,
        "commodity_name":   commodity_name,
        "asset_class":      asset_class,
        "category":         category,
        "contract_size":    size_val,
        "size_unit":        size_unit,
        "price_unit":       price_unit,
        "bid":              bid,
        "ask":              ask,
        "open_price":       open_price,
        "high":             high,
        "low":              low,
        "close_price":      close_price,
        "last_price":       last_price,
        "last_volume":      last_volume,
        "total_volume":     total_volume,
        "change_val":       change_val,
        "change_pct":       change_pct,
        "spread":           spread,
        "spread_pct":       spread_pct,
        "commodity_volume": commodity_volume,
        "api_datetime":     api_datetime,
    }


INSERT_SQL = """
INSERT INTO crop_snapshots (
    fetch_time, fetch_date, contract, commodity_code, commodity_name,
    asset_class, category, contract_size, size_unit, price_unit,
    bid, ask, open_price, high, low, close_price,
    last_price, last_volume, total_volume,
    change_val, change_pct, spread, spread_pct,
    commodity_volume, api_datetime
) VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s
)
ON CONFLICT (fetch_time, contract) DO NOTHING
"""

LOG_SQL = """
INSERT INTO fetch_log (
    fetch_time, contracts_found, active_stored, skipped_inactive, status, error_message
) VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (fetch_time) DO UPDATE SET
    contracts_found = EXCLUDED.contracts_found,
    active_stored = EXCLUDED.active_stored,
    skipped_inactive = EXCLUDED.skipped_inactive,
    status = EXCLUDED.status,
    error_message = EXCLUDED.error_message
"""


# ─────────────────────────────────────────────────────────────────────────────
# Main collector
# ─────────────────────────────────────────────────────────────────────────────

def collect(force: bool = False) -> dict:
    """
    Run a single data collection cycle.

    Args:
        force: If True, skip market-hours check.

    Returns:
        Summary dict with keys: status, contracts_found, active_stored,
        skipped_inactive, error_message.
    """
    now = datetime.now(tz=PST)
    fetch_ts = now.isoformat(timespec="seconds")
    fetch_date = now.strftime("%Y-%m-%d")

    summary = {
        "fetch_time":       fetch_ts,
        "contracts_found":  0,
        "active_stored":    0,
        "skipped_inactive": 0,
        "status":           "unknown",
        "error_message":    None,
    }

    # ── Weekend / market-hours check ────────────────────────────────────
    if not force:
        if not is_weekday(now):
            summary["status"] = "skipped_weekend"
            log.info("⏭  Weekend — skipping fetch.")
            _log_to_db(summary)
            return summary

        if not any_agri_session_open(now):
            summary["status"] = "skipped_market_closed"
            log.info("⏭  No agriculture session currently open — skipping.")
            _log_to_db(summary)
            return summary

    # ── Fetch from API ──────────────────────────────────────────────────
    try:
        data = fetch_pmex("Active")
    except Exception as exc:
        summary["status"] = "error"
        summary["error_message"] = str(exc)
        log.error(f"❌ API request failed: {exc}")
        _log_to_db(summary)
        return summary

    if not isinstance(data, list):
        summary["status"] = "error"
        summary["error_message"] = f"Unexpected response type: {type(data).__name__}"
        log.error(f"❌ {summary['error_message']}")
        _log_to_db(summary)
        return summary

    # ── Filter to agriculture categories ────────────────────────────────
    agri_items = [item for item in data if item.get("Category") in TARGET_CATEGORIES]
    summary["contracts_found"] = len(agri_items)
    log.info(f"📡 API returned {len(data)} total contracts, {len(agri_items)} agriculture.")

    if not agri_items:
        summary["status"] = "success"
        log.info("ℹ️  No agriculture contracts found in API response.")
        _log_to_db(summary)
        return summary

    # ── Process each contract ───────────────────────────────────────────
    rows_to_insert = []
    for item in agri_items:
        row = process_contract(item, fetch_ts, fetch_date)
        if row is not None:
            rows_to_insert.append(row)
        else:
            summary["skipped_inactive"] += 1

    summary["active_stored"] = len(rows_to_insert)

    # ── Insert into database ────────────────────────────────────────────
    conn = init_db()
    try:
        cursor = conn.cursor()
        for row in rows_to_insert:
            cursor.execute(INSERT_SQL, (
                row["fetch_time"], row["fetch_date"], row["contract"], row["commodity_code"], row["commodity_name"],
                row["asset_class"], row["category"], row["contract_size"], row["size_unit"], row["price_unit"],
                row["bid"], row["ask"], row["open_price"], row["high"], row["low"], row["close_price"],
                row["last_price"], row["last_volume"], row["total_volume"],
                row["change_val"], row["change_pct"], row["spread"], row["spread_pct"],
                row["commodity_volume"], row["api_datetime"]
            ))
        conn.commit()
        cursor.close()
        summary["status"] = "success"
    except Exception as exc:
        summary["status"] = "error"
        summary["error_message"] = f"DB insert failed: {exc}"
        log.error(f"❌ {summary['error_message']}")
    finally:
        conn.close()

    # ── Log ─────────────────────────────────────────────────────────────
    _log_to_db(summary)

    # ── Print summary ───────────────────────────────────────────────────
    log.info(
        f"✅ Stored {summary['active_stored']} active contracts, "
        f"skipped {summary['skipped_inactive']} inactive. "
        f"({fetch_ts})"
    )

    if rows_to_insert:
        log.info("   ┌─────────────────────────────┬─────────┬──────────┬─────────────┐")
        log.info("   │ Contract                    │ Bid     │ Volume   │ Commodity   │")
        log.info("   ├─────────────────────────────┼─────────┼──────────┼─────────────┤")
        for r in sorted(rows_to_insert, key=lambda x: x["contract"]):
            bid_s = f"{r['bid']:.2f}" if r['bid'] is not None else "—"
            vol_s = str(r['total_volume'] or 0)
            cv = r['commodity_volume']
            unit = r['size_unit'] or ""
            cv_s = f"{cv:,.0f} {unit}" if cv is not None else "—"
            log.info(
                f"   │ {r['contract']:<27s} │ {bid_s:>7s} │ {vol_s:>8s} │ {cv_s:>11s} │"
            )
        log.info("   └─────────────────────────────┴─────────┴──────────┴─────────────┘")

    return summary


def _log_to_db(summary: dict) -> None:
    """Write a row to the fetch_log table."""
    try:
        conn = init_db()
        cursor = conn.cursor()
        cursor.execute(LOG_SQL, (
            summary["fetch_time"],
            summary["contracts_found"],
            summary["active_stored"],
            summary["skipped_inactive"],
            summary["status"],
            summary["error_message"],
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as exc:
        log.warning(f"⚠️  Could not write fetch_log: {exc}")




def show_status() -> None:
    """Print database statistics and recent fetch history."""
    try:
        conn = _get_conn()
    except Exception as e:
        print(f"❌ Could not connect to database: {e}")
        return

    cursor = conn.cursor(RealDictCursor)

    # Total snapshots
    cursor.execute("SELECT COUNT(*) AS cnt FROM crop_snapshots")
    total = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(DISTINCT fetch_date) AS cnt FROM crop_snapshots")
    dates = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(DISTINCT contract) AS cnt FROM crop_snapshots")
    contracts = cursor.fetchone()["cnt"]

    print(f"\n📊 PMEX Crop Collector — Database Status")
    print(f"   Database: {DB_PATH}")
    print(f"   Total snapshots: {total:,}")
    print(f"   Unique dates:    {dates}")
    print(f"   Unique contracts: {contracts}")

    # Recent fetches
    print(f"\n📋 Last 10 fetches:")
    print(f"   {'Time':<28s} {'Found':>6s} {'Stored':>7s} {'Skip':>5s} {'Status'}")
    print(f"   {'─'*28} {'─'*6} {'─'*7} {'─'*5} {'─'*20}")
    cursor.execute("SELECT * FROM fetch_log ORDER BY fetch_time DESC LIMIT 10")
    rows = cursor.fetchall()
    for row in rows:
        print(
            f"   {row['fetch_time']:<28s} "
            f"{row['contracts_found'] or 0:>6d} "
            f"{row['active_stored'] or 0:>7d} "
            f"{row['skipped_inactive'] or 0:>5d} "
            f"{row['status']}"
        )

    # Per-commodity volume today
    today = datetime.now(tz=PST).strftime("%Y-%m-%d")
    print(f"\n🌾 Today's latest snapshot ({today}):")
    cursor.execute("""
        SELECT
            s.contract,
            s.commodity_code,
            s.bid,
            s.ask,
            s.total_volume,
            s.commodity_volume,
            s.size_unit,
            s.spread,
            s.spread_pct,
            s.change_pct,
            s.last_price
        FROM crop_snapshots s
        INNER JOIN (
            SELECT contract, MAX(fetch_time) AS max_ft
            FROM crop_snapshots
            WHERE fetch_date = %s
            GROUP BY contract
        ) latest ON s.contract = latest.contract AND s.fetch_time = latest.max_ft
        ORDER BY s.commodity_code, s.contract
    """, (today,))
    today_rows = cursor.fetchall()

    if today_rows:
        print(f"   {'Contract':<25s} {'Bid':>9s} {'Ask':>9s} {'Vol':>6s} {'CmdtyVol':>12s} {'Spread%':>8s} {'Chg%':>7s}")
        print(f"   {'─'*25} {'─'*9} {'─'*9} {'─'*6} {'─'*12} {'─'*8} {'─'*7}")
        for r in today_rows:
            bid_s = f"{r['bid']:.2f}" if r['bid'] else "—"
            ask_s = f"{r['ask']:.2f}" if r['ask'] else "—"
            vol_s = str(r['total_volume'] or 0)
            cv = r['commodity_volume']
            unit = r['size_unit'] or ""
            cv_s = f"{cv:,.0f} {unit}" if cv else "—"
            sp_s = f"{r['spread_pct']:.2f}%" if r['spread_pct'] else "—"
            chg_s = f"{r['change_pct']:.2f}%" if r['change_pct'] else "—"
            print(
                f"   {r['contract']:<25s} "
                f"{bid_s:>9s} {ask_s:>9s} "
                f"{vol_s:>6s} {cv_s:>12s} "
                f"{sp_s:>8s} {chg_s:>7s}"
            )
    else:
        print("   No data for today yet.")

    cursor.close()
    conn.close()
    print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """CLI entry point."""
    args = sys.argv[1:]

    if "--status" in args:
        show_status()
        return

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    force = "--force" in args
    result = collect(force=force)

    # Exit with non-zero if error
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
