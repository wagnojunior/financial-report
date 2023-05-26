"""
`financial-report` is a Python library for investment portfolio summary and
report.

It analyses a **buy/sell/dividend** log file and generates a `.pdf` report
which contains the following:

1. current portfolio
    i. total amount invested
    ii. portfolio composition
    iii. dividends
    iv. capital gain
    v. asset allocation
        a. name
        b. type
        c. industry
        d. market
    vi. technical analysis
        a. portfolio beta
        b. correlation matrix
        c. price history
        d. efficient frontier
2. past portfolio
    i. portfolio composition
    ii. capital gain
3. fees
    i. total fees
    ii. fee allocation
        a. name
        b. type
        c. industry
        d. market
"""

__author__ = """Wagno Alves Braganca Junior"""
__email__ = 'wagnojunior@gmail.com'
__version__ = '0.0.1'

from financial_report import data, main, portfolio, report, utils

__all__ = ['data', 'portfolio', 'report', 'utils', 'main']
