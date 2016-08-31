from catshef.exceptions import ArgumentError
from products.fields import RoundingDecimalModelField, round_decimal

from django.test import SimpleTestCase
from decimal import Decimal, ROUND_UP


class RoudingDecimalModelFieldTestCase(SimpleTestCase):
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



    def test_field_rounding(self):
        f1 = RoundingDecimalModelField(max_digits=10, decimal_places=2)
        f1 = f1.to_python(3.14159)
        self.assertEqual(f1, Decimal('3.14'))

        f1 = RoundingDecimalModelField(max_digits=10, decimal_places=2)
        f1 = f1.to_python(1.234)
        self.assertEqual(f1, Decimal('1.23'))

