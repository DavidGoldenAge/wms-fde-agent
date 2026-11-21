"""Ten independent contract checks for a synthetic cancellation function.

Mounted read-only into the sandbox; the candidate implementation is patch.py.
These are input cases for one incident, not ten distinct tickets.
"""
import unittest
from patch import process_order_cancellation as f

class CancellationContract(unittest.TestCase):
    def test_normal(self): self.assertEqual(f('A', 4, 10), {'sku':'A','new_reserved':6,'status':'RELEASED'})
    def test_excess(self): self.assertEqual(f('A', 15, 10), {'sku':'A','new_reserved':0,'status':'RELEASED'})
    def test_equal(self): self.assertEqual(f('A', 10, 10)['new_reserved'], 0)
    def test_zero_cancel(self): self.assertEqual(f('A', 0, 10)['new_reserved'], 10)
    def test_zero_reserved(self): self.assertEqual(f('A', 1, 0)['new_reserved'], 0)
    def test_both_zero(self): self.assertEqual(f('A', 0, 0)['new_reserved'], 0)
    def test_negative_cancel(self):
        with self.assertRaises(ValueError): f('A', -1, 10)
    def test_negative_reserved(self):
        with self.assertRaises(ValueError): f('A', 1, -1)
    def test_both_negative(self):
        with self.assertRaises(ValueError): f('A', -1, -1)
    def test_sku_preserved(self): self.assertEqual(f('SKU-8821', 1, 2)['sku'], 'SKU-8821')

if __name__ == '__main__': unittest.main()
