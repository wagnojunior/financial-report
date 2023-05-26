"""
`beta` handles the portfolio's beta
"""

import numpy as np
import pandas as pd
from data import acquisition as acq
from data import processing as proc
from report import image
from sklearn.linear_model import LinearRegression


def run(df, port):
    """
    `run` runs the calculation of the portfolio's beta. It exports a graph with
    the graphical representation of each asset's beta and a table with the
    beta value of each asset and the of the portfolio as a whole.

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
    symbols_1 = df.index.get_level_values(level='Code').tolist()
    names = df.index.get_level_values(level='Name').tolist()

    # Get the price history pivot table
    price_history_pivot = proc.price_history_pivot(df, port)

    # Empty list to store the beta for each asset
    beta = []

    for symbol, name in zip(symbols_1, names):
        aux = price_history_pivot[[symbol, port.benchmark[0]]].copy()
        aux = aux.dropna()

        # Calculate the daily price change
        aux = aux.pct_change()
        aux = aux.dropna()

        # Define the model and type of regression used to calculate the beta
        x_1 = np.array(aux[port.benchmark[0]]).reshape((-1, 1))
        y_1 = np.array(aux[symbol]).reshape((-1, 1))
        model = LinearRegression().fit(x_1, y_1)

        beta.append([symbol, float(model.coef_), model, [x_1, y_1]])

    # Calculates the portfolio beta
    image.beta(price_history_pivot, beta, port)

    # Converts `beta` into a `dataframe`. It keeps the same order as
    # `price_history_pivot` (sorted by `Code`)
    beta = [b[0:2] for b in beta]
    beta = pd.DataFrame(beta, columns=['Code', 'Beta'])
    beta = beta[beta['Code'] != port.benchmark[0]]

    # Get the exchange rate and sort it by `Code` so that it has the same order
    # as `beta` (sorted by `Code`)
    exchange_rate = acq.get_exchange_rate(df, port)
    exchange_rate = exchange_rate.sort_values(by=['Code'], ascending=True)

    # Create a dataframe to hold the portfolio beta
    port_beta = df.copy()
    port_beta = (
        port_beta
        .groupby(by=['Code', 'Name', 'Currency'])
        .agg(**{'QTY.': ('QTY.', 'sum'),
                'Amount': ('Amount', 'sum'),
                'Allocation (%)': ('Allocation (%)', 'sum')})
    )

    # Add relevant information
    port_beta.insert(
        2,
        'Current Rate',
        exchange_rate['Rate'].values
    )
    port_beta['Amount'] = (
        port_beta['Amount'] * port_beta['Current Rate']
    )

    # Change all currencies to KRW
    currencies = port_beta.index.get_level_values('Currency').unique().tolist()
    currencies.remove('KRW')
    for currency in currencies:
        port_beta = port_beta.rename(index={currency: 'KRW'})

    # Recalculates the allocation
    port_beta['Allocation (%)'] = (
        port_beta['Amount']
        .groupby(level='Currency')
        .apply(lambda x: 100*x/x.sum())
    )

    # Add relevant information
    port_beta['Beta'] = beta['Beta'].values
    port_beta['Weighted Beta'] = (
        port_beta['Allocation (%)'] * port_beta['Beta'] / 100
    )

    # Sort by weighted beta
    port_beta = (
        port_beta
        .sort_values(by=['Weighted Beta'], ascending=False)
    )

    # Calculates the value of the portfolio beta and add it to the dataframe
    pb = port_beta['Weighted Beta'].sum()
    print_df = port_beta.copy()
    print_df.loc[('', '', ''), :] = np.nan
    print_df.loc[('', f'Portfolio beta: {pb:+.2f}', ''), :] = np.nan
    print_df = (
        print_df.style
        .format(precision=2,
                na_rep='',
                thousands=",",
                formatter={'QTY.': '{:.0f}',
                           'Beta': '{:+.2f}',
                           'Weighted Beta': '{:+.2f}'})
        .set_properties(
            subset=['Allocation (%)',
                    'Weighted Beta',
                    'Current Rate'], **{'width': '70px'}
        )
    )

    # Exports table
    image.export(print_df, port.parent_dir, 'table', 'portfolio_beta')
