"""
`monte_carlo` handles the Monte Carlo simulation
"""

import numpy as np
import pandas as pd
from data import processing as proc
from report import image


def run(df, port):
    """
    `run` runs the Monte Carlo simulation. It exports a graph of the simulation
    and a table with the simulation statistics.

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

    # Calculations
    daily_return = (
        price_history_pivot.pct_change().drop(price_history_pivot.index[0])
    )
    allocation = df['Allocation (%)'].values/100
    mean_daily_return = daily_return.mean()
    portfolio_mean_daily_return = np.sum(mean_daily_return*allocation)

    # Calculates the covariation matrix for each asset
    cov_matrix = daily_return.cov()

    # Calculates the portfolio standard deviation
    portfolio_std = (
        np.sqrt(np.dot(allocation, np.dot(cov_matrix, allocation)))
    )

    # Define parameters for the Monte Carlo simulation
    init_portfolio = 1  # Initialize the portfolio return as 1

    # Initialize a matrix to store the simulation restuls
    portfolio_sims = (
        np.full(shape=(port.time_sim, port.num_sim), fill_value=0.0)
    )

    for m in range(0, port.num_sim):
        random_return = (
            np.random.normal(portfolio_mean_daily_return,
                             portfolio_std,
                             size=(1, port.time_sim))
        )
        portfolio_sims[:, m] = np.cumprod(random_return+1)*init_portfolio

    # Turn portfolio_sims into a dataframe
    portfolio_sims = pd.DataFrame(data=portfolio_sims)

    # Statistical summary
    min_value = portfolio_sims.loc[port.time_sim-1].min()
    max_value = portfolio_sims.loc[port.time_sim-1].max()
    avg_value = portfolio_sims.loc[port.time_sim-1].mean()
    med_value = portfolio_sims.loc[port.time_sim-1].median()
    prob_lt_1 = (
        100 *
        portfolio_sims
        .loc[port.time_sim-1][portfolio_sims.loc[port.time_sim-1] < 1].count()
        / port.num_sim
    )
    prob_mt_1 = (
        100 *
        portfolio_sims
        .loc[port.time_sim-1][portfolio_sims.loc[port.time_sim-1] > 1].count()
        / port.num_sim
    )

    # Dataframe
    data = {'': [min_value,
                 max_value,
                 avg_value,
                 med_value,
                 f'{prob_lt_1}%',
                 f'{prob_mt_1}%']}
    index = ['Minimum return',
             'Maximum return',
             'Average return',
             'Median return',
             'Probability return < 1',
             'Probability return > 1']
    print_df = pd.DataFrame(data, index=index).T
    print_df = (
        print_df.style
        .format(precision=2)
    )

    # Export image
    image.export(print_df, port.parent_dir, 'table', 'monte_carlo')

    # Export graph
    image.monte_carlo(portfolio_sims, port)
