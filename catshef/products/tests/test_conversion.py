from decimal import ROUND_HALF_UP

from catshef.exceptions import ArgumentError
from products.utils.conversion import round_decimal, to_decimal


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

class ToDecimalTestCase(SimpleTestCase):
    def test_to_decimal_basic(self):
        a, b, c = 10, 1.1, 0.3333
        a, b, c = to_decimal([a, b, c])
        self.assertEqual(a, Decimal('10'))
        self.assertEqual(b, Decimal('1.10'))
        self.assertEqual(c, Decimal('0.33'))


    def test_to_decimal_rounding(self):

        def round_sample(value, precision=3, rounding=ROUND_HALF_UP):
            """
            Round a Decimal to the given precision.
            """
            return (value.quantize(Decimal(10) ** -precision, rounding=rounding) 
                if value is not None 
                else value)

        a = 1.12345
        a = to_decimal((a,), rounding=None)
        self.assertEqual(a, Decimal(1.12345))

        a, b, c = 1.12345, 10, 0.1234
        a, b, c = to_decimal((a, b, c), rounding=round_sample)
        self.assertCountEqual((a,b, c),
            (Decimal('1.123'), Decimal('10'), Decimal('0.123')))

    def test_to_decimal_string(self):
        a = to_decimal('1.123')
        self.assertEqual(a, Decimal('1.12'))

        a, b, c = to_decimal(('1.23', '0.125', '3.1345'))
        self.assertCountEqual([a, b, c], 
            [Decimal('1.23'), Decimal('0.13'), Decimal('3.13')])
