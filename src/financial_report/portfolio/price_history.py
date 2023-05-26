"""
`price_history` handles the portfolio's price history
"""

from data import processing as proc
from report import image


def run(df, port):
    """
    `run` runs the calculation of the portfolio's price history

    Parameters
    ----------
    df : dataframe
        portfolio allocation per name.
    port : Portfolio
        instance of the class portfolio.

    Returns
    -------
    None.

    """

    # Sort by `Code` and get a list of names and symbols
    df = df.sort_values(by=['Code'], ascending=True)
    names = df.index.get_level_values(level='Name').tolist()
    symbols_1 = df.index.get_level_values(level='Code').tolist()

    # Get the price history pivot table, change the symbols by their
    # respective name, and drop the benchmark
    price_history_pivot = proc.price_history_pivot(df, port)
    for s1, name in zip(symbols_1, names):
        price_history_pivot = (
            price_history_pivot.rename(columns={s1: name})
        )
    price_history_pivot = (
            price_history_pivot.drop(columns=[port.benchmark[0]])
    )

    daily_return = (
        price_history_pivot.pct_change().drop(price_history_pivot.index[0])
    )

    # Calculates the commulative product of a portoflio with an equal weight
    # for every asset
    equal_weight_portfolio = (
        (daily_return.mean(axis=1) + 1).cumprod()
    )

    # Calculate the commulative product of the current portfolio
    allocation = (
        df.sort_values(by=['Code'],
                       ascending=True)['Allocation (%)'].values/100
    )
    weighted_portfolio = (
        ((daily_return*allocation).sum(axis=1)/sum(allocation) + 1).cumprod()
    )

    # Normalized price history of each asset using the first non-null value
    # by using the back propagation method of fillna
    norm_price_history = (
        price_history_pivot
        / price_history_pivot.fillna(method='bfill').iloc[0, :]
    )

    image.price_history(norm_price_history, equal_weight_portfolio,
                        weighted_portfolio, port)
