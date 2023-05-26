"""
`correlation` handles the calculation of the portfolio's correlation table
"""

import numpy as np
from data import processing as proc
from report import image


def run(df, port):
    """
    `run` runs the calcularion of the correlation matrix

    Parameters
    ----------
    df : dataframe
        portfolio allocation per name.
    port : Portfolio
        instance of the class Portfolio.

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

    # Calculate Pearson correlation coefficient
    corr_matrix = price_history_pivot.corr(method='pearson')

    # Take the bottom triangle since it repeats itself
    # Set k=0 (k=1) to exclude (include) the diagonal
    mask = np.zeros_like(corr_matrix)
    mask[np.triu_indices_from(mask, k=1)] = True

    # Export graph
    image.correlation(corr_matrix, names, port)
