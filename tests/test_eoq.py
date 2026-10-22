
"""Unit tests for the standalone EOQ model."""

import math
import unittest

from models.eoq import calculate_eoq, orders_per_year, total_annual_cost


class TestEOQModel(unittest.TestCase):

    def test_known_eoq_example(self):
        # D = 12,000; S = R50; H = R2
        expected = math.sqrt((2 * 12000 * 50) / 2)
        self.assertAlmostEqual(
            calculate_eoq(12000, 50, 2), expected, places=7
        )

    def test_orders_per_year(self):
        self.assertAlmostEqual(
            orders_per_year(12000, 774.5966692414834),
            15.491933384829668,
            places=7,
        )

    def test_total_annual_cost(self):
        eoq = calculate_eoq(12000, 50, 2)
        self.assertAlmostEqual(
            total_annual_cost(12000, 50, 2, eoq),
            1549.1933384829668,
            places=7,
        )

    def test_invalid_zero_demand(self):
        with self.assertRaises(ValueError):
            calculate_eoq(0, 50, 2)

    def test_invalid_negative_holding_cost(self):
        with self.assertRaises(ValueError):
            calculate_eoq(12000, 50, -2)


if __name__ == "__main__":
    unittest.main()
