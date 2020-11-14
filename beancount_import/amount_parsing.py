import re
from beancount.core.number import D
from beancount.core.amount import Amount
import locale
import decimal

locale.setlocale(locale.LC_ALL, "es_ES")

def parse_negative_parentheses(x):
    """Parses a string in parentheses as a negative."""
    m = re.fullmatch(r'^\((.*)\)$', x)
    if m is not None:
        return -1, m.group(1).strip()
    return 1, x

def parse_possible_negative(x):
    x = x.strip()
    m = re.fullmatch(r'^(-|\+)(.*)$', x)
    if m is not None:
        sign = -1 if m.group(1) == '-' else 1
        return sign, m.group(2).strip()
    return parse_negative_parentheses(x)

def parse_number(x):
    """Parses a number in the format of the CSV file.

    A number in parentheses is interpreted as a negative number.
    """
    sign, number_str = parse_possible_negative(x)
    return sign * D(number_str)

def parse_amount(x):
    """Parses a number and currency."""
    if not x:
        return None
    sign, amount_str = parse_possible_negative(x)
    m = re.fullmatch(r'([\$€£])?(EUR )?((?:[0-9](?:\,?[0-9])*|(?=,))(?:,[0-9]+)?)(?:\s+([A-Z]{3}))?', amount_str)
    if m is None:
        raise ValueError('Failed to parse amount from %r' % amount_str)
    if m.group(1):
        currency = {'$': 'USD', '€': 'EUR', '£': 'GBP'}[m.group(1)]
    elif m.group(2):
        currency = 'EUR' 
    elif m.group(4):
        currency = m.group(3)
    else:
        raise ValueError('Failed to determine currency from %r' % amount_str)
    number = locale.atof(m.group(3), decimal.Decimal)
    return Amount(number * sign, currency)
