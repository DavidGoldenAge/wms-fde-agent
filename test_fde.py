import sqlite3
import unittest
import fde

class ToolTests(unittest.TestCase):
    def test_incident_evidence(self):
        ev = fde.evidence('SKU-8821')
        self.assertEqual(ev['events'][0]['event_id'], 'EVT-9901')
        self.assertTrue(any('Cannot release 15 from 10' in line for line in ev['logs']))
        self.assertIn('5:     if cancel_qty > current_reserved:', ev['code'])
    def test_read_only_blocks_write_and_attach(self):
        for statement in ('DELETE FROM inventory_ledger', "ATTACH DATABASE ':memory:' AS x", 'PRAGMA user_version=1'):
            with self.subTest(statement=statement), self.assertRaises(sqlite3.DatabaseError): fde.query(statement)
        self.assertEqual(fde.query('SELECT reserved_qty FROM inventory_ledger WHERE sku=?', ('SKU-8821',))[0]['reserved_qty'], 120)
    def test_patch_shape(self):
        with self.assertRaises(ValueError): fde.validate_code('import os\ndef process_order_cancellation(a,b,c): pass')
    def test_parameter_binding(self):
        self.assertEqual(fde.evidence("SKU-8821' OR 1=1 --")['inventory'], [])
if __name__ == '__main__': unittest.main()
