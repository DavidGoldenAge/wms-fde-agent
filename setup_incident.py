from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent

def main():
    repo, logs = ROOT / 'mock_repo', ROOT / 'mock_logs'
    repo.mkdir(exist_ok=True); logs.mkdir(exist_ok=True)
    db = ROOT / 'wms_prod_mirror.db'
    if db.exists():
        raise SystemExit('Database already exists; remove it manually to reset this synthetic incident.')
    with sqlite3.connect(db) as conn:
        conn.executescript('''
        CREATE TABLE inventory_ledger(sku TEXT PRIMARY KEY, physical_qty INTEGER, reserved_qty INTEGER, channel_synced_qty INTEGER, last_updated TEXT);
        CREATE TABLE webhook_events(event_id TEXT PRIMARY KEY, sku TEXT, event_type TEXT, payload_delta INTEGER, status TEXT, error_msg TEXT);
        INSERT INTO inventory_ledger VALUES ('SKU-8821',120,120,0,'2026-11-20 14:22:01'),('SKU-3049',500,10,490,'2026-11-20 15:00:00');
        INSERT INTO webhook_events VALUES ('EVT-9901','SKU-8821','ORDER_CANCELLED',15,'FAILED','ERR_NEG_RESERVE_LOCK'),('EVT-9902','SKU-8821','STOCK_AUDIT',0,'SKIPPED','LOCKED_BY_PREVIOUS_ERR');
        ''')
    (repo / 'inventory_sync.py').write_text('''def calculate_available_stock(physical_qty: int, reserved_qty: int) -> int:\n    return max(0, physical_qty - reserved_qty)\n\ndef process_order_cancellation(sku: str, cancel_qty: int, current_reserved: int) -> dict:\n    if cancel_qty > current_reserved:\n        raise ValueError(f"ERR_NEG_RESERVE_LOCK: Cannot release {cancel_qty} from {current_reserved}")\n    new_reserved = current_reserved - cancel_qty\n    return {"sku": sku, "new_reserved": new_reserved, "status": "RELEASED"}\n''')
    with (logs / 'sync_worker.log').open('w') as f:
        for i in range(500): f.write(f'2026-11-20 14:{i%60:02d}:00 INFO Heartbeat OK, queue_depth=0\n')
        f.write('2026-11-20 14:22:01 ERROR EVT-9901 SKU-8821 ValueError: ERR_NEG_RESERVE_LOCK: Cannot release 15 from 10\n2026-11-20 14:22:02 WARN SKU-8821 SYNC_LOCKED, skipping downstream Shopify push\n')
    print('Synthetic incident created:', db)
if __name__ == '__main__': main()
