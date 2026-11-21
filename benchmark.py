"""Compare baseline and known-good implementations against the same ten checks."""
import ast, json, time
from pathlib import Path
import fde

source = (Path(__file__).resolve().parent / 'mock_repo' / 'inventory_sync.py').read_text()
tree = ast.parse(source)
node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'process_order_cancellation')
BASELINE = ast.get_source_segment(source, node)
REFERENCE = '''def process_order_cancellation(sku: str, cancel_qty: int, current_reserved: int) -> dict:
    if cancel_qty < 0 or current_reserved < 0:
        raise ValueError("negative quantities are invalid")
    return {"sku": sku, "new_reserved": max(0, current_reserved - cancel_qty), "status": "RELEASED"}
'''

def main():
    outcomes = {}
    for name, code in [('original', BASELINE), ('reference', REFERENCE)]:
        start = time.monotonic()
        passed, output = fde.verify(code)
        outcomes[name] = passed
        print(json.dumps({'candidate':name,'all_ten_pass':passed,'seconds':round(time.monotonic()-start,2),'test_output':output}, ensure_ascii=False))
    if outcomes != {'original': False, 'reference': True}:
        raise SystemExit('Unexpected benchmark outcome; check the Docker output above.')
if __name__ == '__main__': main()
