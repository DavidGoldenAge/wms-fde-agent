def calculate_available_stock(physical_qty: int, reserved_qty: int) -> int:
    return max(0, physical_qty - reserved_qty)

def process_order_cancellation(sku: str, cancel_qty: int, current_reserved: int) -> dict:
    if cancel_qty > current_reserved:
        raise ValueError(f"ERR_NEG_RESERVE_LOCK: Cannot release {cancel_qty} from {current_reserved}")
    new_reserved = current_reserved - cancel_qty
    return {"sku": sku, "new_reserved": new_reserved, "status": "RELEASED"}
