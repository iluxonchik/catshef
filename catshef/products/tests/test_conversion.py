from catshef.exceptions import ArgumentError
from products.utils.conversion import round_decimal

from django.test import SimpleTestCase
from decimal import Decimal, ROUND_UP

class RoundDecimalTestCase(SimpleTestCase):
    def test_round_decimal(self):
        d1 = round_decimal(Decimal('1.234'), precision=3)
        self.assertEqual(d1, Decimal('1.234'))

        with self.assertRaises(ArgumentError):
            round_decimal(42)

        d1 = round_decimal(Decimal('1.2345'), precision=3)
        self.assertEqual(d1, Decimal('1.235'))

        d1 = round_decimal(Decimal('1.2341'), precision=3,
            rounding=ROUND_UP)
        self.assertEqual(d1, Decimal('1.235'))

        d1 = round_decimal(Decimal('1.234'))
        self.assertEqual(d1, Decimal('1.23'))
