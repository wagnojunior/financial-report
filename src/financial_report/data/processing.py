"""
`processing` handles the data processing.
"""

import numpy as np
import pandas as pd
from data import acquisition as acq
from report import image


def raw_data(port):
    """
    `raw_data` reads the buy/sell/dividend log file which is defined by
    the given file name and located at the given directory. The log file should
    be a `xlsx` file and it should follow the specified template.

    Parameters
    ----------
    port : Portfolio
        instance of class Portfolio

    Returns
    -------
    aux : dataframe
        buy/sell/dividend log file.

    """

    in_dir = f'../../resources/{port.parent_dir}/{port.input_file}'

    aux = (
        pd.read_excel(in_dir,
                      header=[0],
                      skiprows=0,
                      converters={'QTY.': int,
                                  'Unit Price': float,
                                  'Amount': float,
                                  'Broker Fee': float,
                                  'Tax Fee': float,
                                  'Exchange Rate': float})
    )
    aux['Date (YYYY-MM-DD)'] = pd.DatetimeIndex(aux['Date (YYYY-MM-DD)'])

    return aux


def raw_data_buy(raw_data):
    """
    `raw_data_buy` returns a dataframe populated by *buy* operations only.

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.

    Returns
    -------
    aux : dataframe
        buy log file.

    """

    aux = raw_data[raw_data['Operation'] == 'Buy']

    return aux


def raw_data_sell(raw_data):
    """
    `raw_data_sell` returns a dataframe populated by *sell* operations only.

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.

    Returns
    -------
    aux : dataframe
        sell log file.

    """

    aux = raw_data[raw_data['Operation'] == 'Sell']

    return aux


def raw_data_buy_sell(raw_data):
    """
    `raw_data_buy_sell` returns a dataframe populated by *buy/sell* operations.

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.

    Returns
    -------
    aux : dataframe
        buy/sell log file.

    """

    aux = raw_data[raw_data['Operation'] != 'Dividend']

    return aux


def raw_data_dividend(raw_data):
    """
    `raw_data_dividend` returns a dataframe populated by *dividend* operations
    only.

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.

    Returns
    -------
    aux : dataframe
        dividend log file.

    """

    aux = raw_data[raw_data['Operation'] == 'Dividend']

    return aux


def raw_data_negative(raw_data):
    """
    `raw_data_negative` returns a dataframe with negative `QTY.` values for
    sold assets.

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.

    Returns
    -------
    aux : dataframe
        buy/sell/dividend log file with negative `QTY` for sold assets.

    """

    aux = raw_data_buy_sell(raw_data).copy()

    aux.loc[(aux['Operation'] == 'Sell'), 'QTY.'] *= -1

    return aux


def liquidation_list(raw_data):
    """
    `liquidation_list` returns a list of assets that were completely liquidated

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.

    Returns
    -------
    aux : list
        list of assets that were completely liquidated.

    """

    aux = (
        raw_data_negative(raw_data)
        .groupby(by=['Code'])
        .agg({'QTY.': 'sum',
              'Amount': 'sum'})
    )

    aux = (
        aux[aux['QTY.'] == 0]
        .index
        .values
        .tolist()
    )

    return aux


def n_liquidation_list(raw_data):
    """
    `n_liquidation_list` returns a list of assets that were NOT completely
    liquidated

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.

    Returns
    -------
    aux : list
        list of assets that were NOT completely liquidated.

    """

    aux = (
        raw_data_negative(raw_data)
        .groupby(by=['Code'])
        .agg({'QTY.': 'sum',
              'Amount': 'sum'})
    )

    aux = (
        aux[aux['QTY.'] != 0]
        .index
        .values
        .tolist()
    )

    return aux


def raw_data_past(raw_data):
    """
    `raw_data_past` returns a dataframe with *buy*, *sell*, and *dividend*
    operations of past assets

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.

    Returns
    -------
    aux : dataframe
        buy/sell/dividend log file of past assets.

    """

    aux = (
        raw_data[raw_data['Code'].isin(liquidation_list(raw_data))]
    )

    return aux


def raw_data_past_buy_sell(raw_data):
    """
    `raw_data_past_buy_sell` returns a dataframe with *buy* and *sell*
    operations of past assets

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.

    Returns
    -------
    aux : dataframe
        buy/sell log file of past assets.

    """

    aux = raw_data_buy_sell(raw_data)

    aux = (
        aux[aux['Code'].isin(liquidation_list(raw_data))]
    )

    return aux


def raw_data_current(raw_data):
    """
    `raw_data_current` returns a dataframe with buy/sell/dividend operations
    of current assets

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.

    Returns
    -------
    aux : dataframe
        buy/sell/dividend log file of current assets.

    """

    aux = (
        raw_data[raw_data['Code'].isin(n_liquidation_list(raw_data))]
    )

    return aux


def raw_data_current_buy_sell(raw_data):
    """
    `raw_data_current_buy_sell` returns a dataframe with buy/sell operations of
    current assets

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.

    Returns
    -------
    aux : dataframe
        buy/sell log file of current assets.

    """

    aux = raw_data_buy_sell(raw_data)

    aux = (
        aux[aux['Code'].isin(n_liquidation_list(raw_data))]
    )

    return aux


def all_assets(raw_data, port):
    """
    `all_assets` returns and exports a dataframe with all the portfolio's
    assets

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    my_all_assets : dataframe
        all assets in the portfolio.

    """

    my_raw_data_buy = (
        raw_data_buy(raw_data)
    )

    # Defines the lambda function to calculate a weighted average
    def wa(x):
        return np.average(x,
                          weights=(
                              my_raw_data_buy.loc[x.index,
                                                  'Amount']))

    # Defines a group dictionary
    group = ['Type',
             'Industry',
             'Market',
             'Code',
             'Code 2',
             'Name',
             'Currency']

    # All assets include current and past assets
    my_all_assets = (
        my_raw_data_buy
        .groupby(by=group)
        .agg({'QTY.': 'sum',
             'Amount': 'sum'}))

    # Adds column with average purchase price
    my_all_assets['Avg. Price'] = (
        my_all_assets['Amount'] /
        my_all_assets['QTY.']
    )

    # Adds column with weighted average exchange rate
    my_all_assets['Avg. Rate'] = (
        my_raw_data_buy
        .groupby(by=group)
        .agg(**{'Ave. Rate': ('Exchange Rate', wa)})
    )

    print_df = my_all_assets.copy().reset_index(level=['Code 2'], drop=True)
    print_df = (
        print_df.style
        .format(precision=2,
                thousands=",",
                formatter={'QTY.': '{:.0f}'})
    )

    # Exports image
    image.export(print_df, port.parent_dir, 'table', 'all_assets')

    # Returns the dataframe
    return my_all_assets


def total_invested(raw_data, port):
    """
    `total_invested` returns and exports a dataframe with portfolio's total
    amount invested

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    my_total_invested : dataframe
        total amount invested in the portfolio.

    """

    my_total_invested = (
        raw_data_current_buy_sell(raw_data)
        .groupby(by=['Currency'])
        .agg({'Amount': 'sum',
              'Broker Fee': 'sum',
              'Tax Fee': 'sum'})
    )

    # Add relevant information
    my_total_invested['Total Fee'] = (
        my_total_invested['Broker Fee'] + my_total_invested['Tax Fee']
    )
    my_total_invested['Total Fee (%)'] = (
        100 * my_total_invested['Total Fee'] / my_total_invested['Amount']
    )

    print_df = my_total_invested.copy()
    print_df = (
        print_df.style
        .format(precision=2,
                thousands=",")
    )

    # Exports image
    image.export(print_df, port.parent_dir, 'table', 'total_invested')

    return my_total_invested


def cumulative_amount(raw_data, port):
    """
    `cumulative_amount` saves a line-graph of the cumulative amount invested
    for all currencies. The values are normalized by the initial invested
    amount, so all currencies are visible on the graph

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    None.

    """

    my_cumulative_amount = (
        raw_data_negative(raw_data)
        .rename(columns={'Date (YYYY-MM-DD)': 'Year-Month'})
    )

    # Generates a year_month string to group the dataframe
    y_m = my_cumulative_amount['Year-Month'].dt.strftime('%y-%m')

    my_cumulative_amount = (
        my_cumulative_amount
        .groupby(by=[y_m, 'Currency'])
        .agg({'Amount': 'sum'})
        .unstack().fillna(0)
    )

    # Get the multiplier for each currency
    multiplier = (
        my_cumulative_amount
        .replace(0, np.nan)
        .fillna(method='bfill')
        .iloc[0, :].values
    )
    currency = list(my_cumulative_amount.columns.levels[1])
    label = [
        f'{curr}: multiplier={mult:+,.2f}'
        for curr, mult in zip(currency, multiplier)
    ]

    # Normalize according to the first month
    my_cumulative_amount = (
        my_cumulative_amount / multiplier
    )

    # Replace nan for zero. This is necessary because
    # my_cumulative_amount/multiplier may return nan if both are zero
    my_cumulative_amount = my_cumulative_amount.fillna(0)

    # Saves graph
    image.cumulative_amount(my_cumulative_amount, label, port.parent_dir)


def current_assets(raw_data, port):
    """
    `current_assets` returns and exports a dataframe with the portfolio's
    current assets

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    my_current_assets : dataframe
        current assets in the portfolio.

    """

    my_raw_data_current_buy_sell = (
        raw_data_current_buy_sell(raw_data)
    )

    # Defines the lambda function to calculate weighted average
    def wa(x):
        return np.average(x,
                          weights=(
                              my_raw_data_current_buy_sell.loc[x.index,
                                                               'Amount']))
    group = ['Type',
             'Industry',
             'Market',
             'Code',
             'Code 2',
             'Name',
             'Currency']

    # Current assets exclude items that were purchased and entirely sold
    my_current_assets = (
        my_raw_data_current_buy_sell
        .groupby(by=group)
        .agg(**{'QTY.': ('QTY.', 'sum'),
                'Avg. Rate': ('Exchange Rate', wa),
                'Amount': ('Amount', 'sum')})
    )

    # Adds column with average purchase price
    my_current_assets['Avg. Price'] = (
        my_current_assets['Amount'] /
        my_current_assets['QTY.']
    )

    # Removes irrelevant information
    my_current_assets = (
        my_current_assets.drop(['Amount'],
                               axis=1)
    )

    # Gets the latest Close Price from `my_current_assets`
    symbol_list = (
        my_current_assets.index.get_level_values(level='Code').tolist()
    )
    price_history = acq.get_price_latest(symbol_list, port)

    # Adds relevant information
    my_current_assets['Close Price'] = (
        price_history['Close'].values
    )
    my_current_assets['Amount'] = (
        my_current_assets['QTY.'] * my_current_assets['Close Price']
    )

    print_df = my_current_assets.copy().reset_index(level=['Code 2'],
                                                    drop=True)
    print_df = (
        print_df.style
        .format(precision=2,
                thousands=",",
                formatter={'QTY.': '{:.0f}'})
    )

    # Exports image
    image.export(print_df, port.parent_dir, 'table', 'current_assets')

    return my_current_assets


def allocation_variable(current_assets, variable, port):
    """
    `allocation_variable` returns and exports a dataframe with the portfolio's
    allocation per a variable input, such as industry, market, name, and type.

    Parameters
    ----------
    current_assets : dataframe
        current assets in the portfolio.
    variable : str
        variable input, such as industry, market, name, and type.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    my_allocation_variable : dataframe
        portfolio allocation by a variable input.

    """

    group = ['Type',
             'Industry',
             'Market',
             'Code',
             'Code 2',
             'Name',
             'Currency']

    my_allocation_variable = (
        current_assets
        .groupby(by=group)
        .agg({'QTY.': 'sum',
              'Amount': 'sum'})
    )

    my_allocation_variable['Allocation (%)'] = (
        my_allocation_variable['Amount']
        .groupby(level='Currency')
        .apply(lambda x:  100*x / x.sum())
    )

    print_df = my_allocation_variable.copy()
    print_df = (
        print_df
        .groupby(by=[variable, 'Currency'])
        .agg({'QTY.': 'sum',
              'Amount': 'sum',
              'Allocation (%)': 'sum'})
        .sort_values(by=['Currency',
                         'Allocation (%)'],
                     ascending=[True,
                                False])
    )

    # Defines aux dataframe. This has to be done before applying the style
    aux = print_df.copy().reset_index()

    print_df = (
        print_df.style
        .format(precision=2,
                na_rep='',
                thousands=",",
                formatter={'QTY.': '{:.0f}'})
        .set_properties(
            subset=['Allocation (%)'], **{'width': '70px'})
    )

    # Exports dataframe
    image.export(print_df, port.parent_dir, 'table',
                 f'allocation_{variable.lower()}')

    # Mask to combine low values together. Assets that have an allocation
    # of less than 5% are grouped together under the nane `Other`.
    # If only one item has an allocation less than 5, then do not group
    mask = aux['Allocation (%)'] < 5
    if sum(mask) > 1:
        aux.loc[mask, [variable]] = 'Other'

    aux = (
        aux
        .groupby(by=[variable, 'Currency'])
        .agg({'QTY.': 'sum',
              'Amount': 'sum',
              'Allocation (%)': 'sum'})
        .sort_values(by=['Currency',
                         'Allocation (%)'],
                     ascending=[True,
                                False])
        .reset_index()
    )

    # After renaming items lower than 5% in the column <variable>, the
    # index can be reset
    aux = (
        aux.set_index([variable, 'Currency'])
    )

    # Saves image
    image.allocation_variable(aux, variable, port.parent_dir)

    return my_allocation_variable


def past_assets(raw_data, port):
    """
    `past_assets` returns and exports a dataframe with the portfolio's past
    assets, that is assets that were completely liquidated.

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    my_past_assets : dataframe
        past assets in the portfolio.

    """

    my_raw_data_past_buy_sell = (
        raw_data_past_buy_sell(raw_data)
    )

    my_raw_data_past_buy = (
        my_raw_data_past_buy_sell[
            my_raw_data_past_buy_sell['Operation'] == 'Buy']
    )

    if len(my_raw_data_past_buy.index) == 0:
        data = {'There are no past assets in this portfolio': []}
        my_past_assets = pd.DataFrame(data)

        # Exports image
        image.export(my_past_assets,
                     port.parent_dir,
                     'table',
                     'past_assets')

        return my_past_assets

    my_raw_data_past_sell = (
        my_raw_data_past_buy_sell[
            my_raw_data_past_buy_sell['Operation'] == 'Sell']
    )

    # Defines the lambda function to calculate weighted average
    def wa(x):
        return np.average(x,
                          weights=(
                              my_raw_data_past_buy.loc[x.index, 'Amount']))

    group = ['Type',
             'Industry',
             'Market',
             'Code',
             'Code 2',
             'Name',
             'Currency']

    my_past_assets = (
        my_raw_data_past_buy
        .groupby(by=group)
        .agg(**{'QTY.': ('QTY.', 'sum'),
                'Avg. Rate': ('Exchange Rate', wa),
                'Amount': ('Amount', 'sum')})
    )

    # Adds column with average purchase price
    my_past_assets['Avg. Price'] = (
        my_past_assets['Amount'] /
        my_past_assets['QTY.']
    )

    # Removes irrelevant information
    my_past_assets = (
        my_past_assets.drop(['Amount'],
                            axis=1)
    )

    aux = (
        my_raw_data_past_sell
        .groupby(by=group)
        .agg(**{'QTY.': ('QTY.', 'sum'),
                'Amount': ('Amount', 'sum')})
    )

    # Adds selling price
    my_past_assets['Selling Price'] = (
        aux['Amount'] / aux['QTY.']
    )

    # Adds Amount
    my_past_assets['Amount'] = (
        my_past_assets['QTY.'] * my_past_assets['Selling Price']
    )

    print_df = my_past_assets.copy()
    print_df = (
        print_df.style
        .format(precision=2,
                thousands=",",
                formatter={'QTY.': '{:.0f}'})
    )

    # Exports image
    image.export(print_df, port.parent_dir, 'table', 'past_assets')

    return my_past_assets


def assets_dividend(raw_data, all_assets, port):
    """
    `assets_dividend` returns and exports a dataframe with the portfolio's
    dividend history. The dividend yield is calculated for the last twelve
    months (LTM)

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.
    all_assets : dataframe
        all assets in the portfolio.
    port : Portfolio
        instance of class Portfolio.

    Returns
    ------
    my_assets_dividend : dataframe
        dividend history of the portfolio.

    """

    my_raw_data_dividend = (
        raw_data_dividend(raw_data)
    )

    # Dividend yield is calculated for the last twenve months (LTW)
    my_assets_dividend = (
        my_raw_data_dividend[
            my_raw_data_dividend[
                'Date (YYYY-MM-DD)'] > (pd.Timestamp('today') -
                                        pd.DateOffset(years=1))].copy()
    )

    # Adda columns with relevant information
    my_assets_dividend['Total Fee'] = (
        my_assets_dividend['Broker Fee'] +
        my_assets_dividend['Tax Fee']
    )

    my_assets_dividend['Total Fee per Share'] = (
        my_assets_dividend['Total Fee'] /
        my_assets_dividend['QTY.']
    )

    my_assets_dividend['Net DPS'] = (
        my_assets_dividend['Unit Price'] -
        my_assets_dividend['Total Fee per Share']
    )

    group = ['Type',
             'Industry',
             'Market',
             'Code',
             'Code 2',
             'Name',
             'Currency']

    my_assets_dividend = (
        my_assets_dividend
        .groupby(by=group)
        .agg(**{'QTY.': ('QTY.', 'sum'),
                'Dividend': ('Amount', 'sum'),
                'DPS': ('Unit Price', 'sum'),
                'Broker Fee': ('Broker Fee', 'sum'),
                'Tax Fee': ('Tax Fee', 'sum'),
                'Total Fee': ('Total Fee', 'sum'),
                'Total FPS': ('Total Fee per Share', 'sum'),
                'Net DPS': ('Net DPS', 'sum')})
    )

    # Geta a list of codes of the assets in `assets_dividend`
    list_assets_dividend = (
        my_assets_dividend
        .index
        .get_level_values('Code')
        .tolist()
    )

    # Use the `list_assets_dividend` to filter the average price from the
    # `all_assets` dataframe
    aux = (
        all_assets[
            all_assets
            .index
            .isin(
                list_assets_dividend,
                level='Code')]
    )

    my_assets_dividend['Avg. Price'] = (
        aux['Avg. Price']
    )

    my_assets_dividend['Dividend Yield (%)'] = (
        100 *
        my_assets_dividend['Net DPS'] /
        my_assets_dividend['Avg. Price']
    )

    my_assets_dividend = (
        my_assets_dividend
        .drop(['Broker Fee',
               'Tax Fee',
               'Total FPS'],
              axis=1)
        .sort_index(level=['Currency',
                           'Name'])
        .sort_values(by=['Currency',
                         'Dividend Yield (%)'],
                     ascending=[True,
                                False])
    )

    print_df = my_assets_dividend.copy()
    print_df = (
        print_df.reset_index(level=['Type',
                                    'Industry',
                                    'Market',
                                    'Code 2'],
                             drop=True)
    )

    print_df = (
        print_df.style
        .format(precision=2,
                na_rep='',
                thousands=",",
                formatter={'QTY.': '{:.0f}',
                           'Dividend Yield': '{:+.2f}'})
        .set_properties(
            subset=['Dividend Yield (%)'], **{'width': '70px'})
    )

    # Exports image
    image.export(print_df, port.parent_dir, 'table', 'assets_dividend')

    return my_assets_dividend


def passive_portfolio(current_assets, port):
    """
    `passive_portfolio` returns and exports a dataframe with the portfolio's
     passive assets

    Parameters
    ----------
    current_assets : dataframe
        current assets in the portfolio.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    my_passive_portfolio : dataframe
        passive assets in the portfolio.

    """

    try:
        my_passive_portfolio = (
            current_assets.loc[pd.IndexSlice['ETF', :], :]
        )

    except KeyError:
        data = {'There are no active assets in this portfolio': []}
        my_passive_portfolio = pd.DataFrame(data)

        # Exports image
        image.export(my_passive_portfolio,
                     port.parent_dir,
                     'table',
                     'passive_portfolio')

        return my_passive_portfolio

    print_df = my_passive_portfolio.copy()
    print_df = (
        print_df.style
        .format(precision=2,
                thousands=",",
                formatter={'QTY.': '{:.0f}'})
    )

    # Exports image
    image.export(print_df, port.parent_dir, 'table',
                 'passive_portfolio')

    return my_passive_portfolio


def active_portfolio(current_assets, port):
    """
    `active_portfolio` exports and returns a dataframe with the portfolio's
    active assets

    Parameters
    ----------
    current_assets : dataframe
        current assets in the portfolio.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    my_active_portfolio : dataframe
        active assets in the portfolio.

    """

    try:
        my_active_portfolio = (
            current_assets.loc[pd.IndexSlice['Stock', :], :]
        )

    except KeyError:
        data = {'There are no active assets in this portfolio': []}
        my_active_portfolio = pd.DataFrame(data)

        # Exports image
        image.export(my_active_portfolio,
                     port.parent_dir,
                     'table',
                     'active_portfolio')

        return my_active_portfolio

    print_df = my_active_portfolio.copy()
    print_df = (
        print_df.style
        .format(precision=2,
                thousands=",",
                formatter={'QTY.': '{:.0f}'})
    )

    # Exports image
    image.export(print_df, port.parent_dir, 'table',
                 'active_portfolio')

    return my_active_portfolio


def breakdown_past_assets(raw_data, port):
    """
    `breakdown_past_assets` exports and returns a dataframe with the breakdown
    of the portfolio's past assets. The breakdown is composed of the quantity,
    amount, average price, total fees, averaga currency rate, and capital gain
    of each assets in the portfolio that were completely liquidaded.

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    my_breakdown_past_assets : dataframe
        breakdown of past assets in the portfolio.

    """

    my_raw_data_past = (
        raw_data_past(raw_data)
    )

    # Defines the lambda function to calculate weighted average
    def wa(x):
        return np.average(x,
                          weights=(
                              my_raw_data_past.loc[x.index,
                                                   'Amount']))

    group = ['Type',
             'Industry',
             'Market',
             'Code',
             'Code 2',
             'Name',
             'Operation',
             'Currency']

    # Reorganizes dataframe
    my_breakdown_past_assets = (
        my_raw_data_past
        .groupby(by=group)
        .agg(**{'QTY.': ('QTY.', 'sum'),
                'Amount': ('Amount', 'sum'),
                'Broker Fee': ('Broker Fee', 'sum'),
                'Tax Fee': ('Tax Fee', 'sum'),
                'Avg. Rate': ('Exchange Rate', wa)})
    )

    # Inserts average price at position 2
    my_breakdown_past_assets.insert(
        2,
        'Avg. Price',
        my_breakdown_past_assets['Amount'] /
        my_breakdown_past_assets['QTY.']
    )

    # Inserst total fee at position 5
    my_breakdown_past_assets.insert(
        5,
        'Total Fee',
        my_breakdown_past_assets['Broker Fee'] +
        my_breakdown_past_assets['Tax Fee']
    )

    # Unstacks
    my_breakdown_past_assets = (
        my_breakdown_past_assets
        .unstack(level='Operation')
        .fillna(0)
    )

    # my_breakdown_past_assets` is empty in case there are no past assets in
    # a portfolio. Any operations on this dataframe will raise a `KeyError`
    # error, which is handled by creating and exporting a dataframe with a
    # message
    try:
        # After unstacking dtype int64 are converted to float64
        # Converts `QTY.` back to int64
        my_breakdown_past_assets[('QTY.')] = (
            my_breakdown_past_assets[('QTY.')].astype(np.int64)
        )

    except KeyError:
        data = {'There are no past assets in this portfolio': []}
        my_breakdown_past_assets = pd.DataFrame(data)

        # Exports image
        image.export(my_breakdown_past_assets,
                     port.parent_dir,
                     'table',
                     'breakdown_past_assets')

        return my_breakdown_past_assets

    # Defines the function to calculate the capital gain/loss.
    # The difference between the `sell_price` and `buy_price is
    # divided by the `sell_rate`, thus converting back to the original
    # currency.
    # Because of that, the rate for the fees is not necessary
    def calc_capital_gain_loss(buy_price, sell_price, div_price, buy_fee,
                               sell_fee, div_fee, buy_rate, sell_rate):
        return (
            (sell_price * sell_rate - buy_price * buy_rate) / sell_rate +
            div_price - buy_fee - sell_fee - div_fee
        )

    # Tries for the case where there is dividend
    try:
        my_breakdown_past_assets['Capital Gain'] = (
            calc_capital_gain_loss(
                my_breakdown_past_assets[('Amount', 'Buy')],
                my_breakdown_past_assets[('Amount', 'Sell')],
                my_breakdown_past_assets[('Amount', 'Dividend')],
                my_breakdown_past_assets[('Broker Fee', 'Buy')] +
                my_breakdown_past_assets[('Tax Fee', 'Buy')],
                my_breakdown_past_assets[('Broker Fee', 'Sell')] +
                my_breakdown_past_assets[('Tax Fee', 'Sell')],
                my_breakdown_past_assets[('Broker Fee', 'Dividend')] +
                my_breakdown_past_assets[('Tax Fee', 'Dividend')],
                my_breakdown_past_assets[('Avg. Rate', 'Buy')],
                my_breakdown_past_assets[('Avg. Rate', 'Sell')])
        )

    # Catches KeyError if there is no dividend
    except KeyError as e:

        if str(e) == 'Dividend':
            my_breakdown_past_assets['Capital Gain'] = (
                calc_capital_gain_loss(
                    my_breakdown_past_assets[('Amount', 'Buy')],
                    my_breakdown_past_assets[('Amount', 'Sell')],
                    0,
                    my_breakdown_past_assets[('Broker Fee', 'Buy')] +
                    my_breakdown_past_assets[('Tax Fee', 'Buy')],
                    my_breakdown_past_assets[('Broker Fee', 'Sell')] +
                    my_breakdown_past_assets[('Tax Fee', 'Sell')],
                    0,
                    my_breakdown_past_assets[('Avg. Rate', 'Buy')],
                    my_breakdown_past_assets[('Avg. Rate', 'Sell')])
            )

    my_breakdown_past_assets['Capital Gain (%)'] = (
        100 * my_breakdown_past_assets[('Capital Gain', '')] /
        my_breakdown_past_assets[('Amount', 'Buy')]
    )

    # Resets the index and sort it
    my_breakdown_past_assets = (
        my_breakdown_past_assets
        .drop(['Broker Fee',
               'Tax Fee'],
              axis=1)
        .sort_values(by=['Currency',
                         'Capital Gain (%)'],
                     ascending=[True,
                                False])
    )

    print_df = my_breakdown_past_assets.copy()
    print_df = (
        print_df
        .reset_index(level=['Type',
                            'Industry',
                            'Market',
                            'Code 2'], drop=True)
        .rename(columns={'Dividend': 'Div.'}, level=1)
    )

    # Applies style
    print_df = (
        print_df.style
        .format(precision=2,
                na_rep='',
                thousands=",",
                formatter={('QTY.', 'Buy'): '{:d}',
                           ('QTY.', 'Div.'): '{:d}',
                           ('QTY.', 'Sell'): '{:d}',
                           ('Capital Gain', ''): '{:+,.2f}',
                           ('Capital Gain (%)', ''): '{:+,.2f}'}
                )
        .set_properties(
            subset=['Capital Gain (%)'], **{'width': '70px'}
        )
        .set_table_styles(
            [dict(selector="th", props=[('max-width', '250px')])]
        )
    )

    # Exports image
    image.export(print_df, port.parent_dir, 'table', 'breakdown_past_assets')

    return my_breakdown_past_assets


def breakdown_current_assets(raw_data, current_assets, port):
    """
    `breakdown_current_assets` exports and returns a dataframe with the
    breakdown of the portfolio's current assets. The breakdown is composed of
    the quantity, amount, average price, total fees, averaga currency rate, and
    capital gain of each assets in the portfolio.

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.
    current_assets : dataframe
        current assets in the portfolio.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    my_breakdown_current_assets : dataframe
        breakdown of current assets in the portfolio.

    """

    my_raw_data_current = (
        raw_data_current(raw_data)
    )

    # Defines the lambda function to calculate weighted average
    def wa(x):
        return np.average(x,
                          weights=(
                              my_raw_data_current.loc[x.index,
                                                      'Amount']))

    group = ['Type',
             'Industry',
             'Market',
             'Code',
             'Code 2',
             'Name',
             'Operation',
             'Currency']

    # Reorganizes dataframe
    my_breakdown_current_assets = (
        my_raw_data_current
        .groupby(by=group)
        .agg(**{'QTY.': ('QTY.', 'sum'),
                'Amount': ('Amount', 'sum'),
                'Broker Fee': ('Broker Fee', 'sum'),
                'Tax Fee': ('Tax Fee', 'sum'),
                'Avg. Rate': ('Exchange Rate', wa)}
             )
    )

    # Inserts average price at position 2
    my_breakdown_current_assets.insert(
        2,
        'Avg. Price',
        my_breakdown_current_assets['Amount'] /
        my_breakdown_current_assets['QTY.']
    )

    # Inserts total fee at position 5
    my_breakdown_current_assets.insert(
        5,
        'Total Fee',
        my_breakdown_current_assets['Broker Fee'] +
        my_breakdown_current_assets['Tax Fee']
    )

    # Unstacks
    my_breakdown_current_assets = (
        my_breakdown_current_assets
        .unstack(level='Operation')
        .fillna(0)
    )

    # Gets the current exchange rate and adds to my_breakdown_current_assets
    exchange_rate = acq.get_exchange_rate(my_breakdown_current_assets,
                                          port)
    my_breakdown_current_assets['Current Rate'] = (
        exchange_rate['Rate'].values
    )

    # Adds the Current Amount from the `current_assets`
    my_breakdown_current_assets['Current Amount'] = (
        current_assets['Amount'].values
    )

    # After unstacking dtype int64 are converted to float64
    # Converts `QTY.` back to int64
    my_breakdown_current_assets[('QTY.')] = (
        my_breakdown_current_assets[('QTY.')].astype(np.int64)
    )

    # Defines the function to calculate the capital gain/loss
    # The difference between the --current_price-- and --buy_price-- is
    # divided by the --current_rate--, thus converting back to the original
    # currency.
    # Because of that, the rate for the fees is not necessary
    def calc_capital_gain_loss(buy_price, current_price, div_price,
                               buy_fee, div_fee, buy_rate, current_rate):
        return (
            (current_price * current_rate - buy_price * buy_rate) /
            current_rate +
            div_price - buy_fee - div_fee
        )

    # Tries for the case where there is dividend
    try:
        my_breakdown_current_assets['Capital Gain'] = (
            calc_capital_gain_loss(
                my_breakdown_current_assets[('Amount', 'Buy')],
                my_breakdown_current_assets[('Current Amount', '')],
                my_breakdown_current_assets[('Amount', 'Dividend')],
                my_breakdown_current_assets[('Broker Fee', 'Buy')] +
                my_breakdown_current_assets[('Tax Fee', 'Buy')],
                my_breakdown_current_assets[('Broker Fee', 'Dividend')] +
                my_breakdown_current_assets[('Tax Fee', 'Dividend')],
                my_breakdown_current_assets[('Avg. Rate', 'Buy')],
                my_breakdown_current_assets[('Current Rate', '')]
            )
        )

    # Catches KeyError if there is no dividend
    except KeyError:
        my_breakdown_current_assets['Capital Gain'] = (
            calc_capital_gain_loss(
                my_breakdown_current_assets[('Amount', 'Buy')],
                my_breakdown_current_assets[('Current Amount', '')],
                0,
                my_breakdown_current_assets[('Broker Fee', 'Buy')] +
                my_breakdown_current_assets[('Tax Fee', 'Buy')],
                0,
                my_breakdown_current_assets[('Avg. Rate', 'Buy')],
                my_breakdown_current_assets[('Current Rate', '')])
        )

    my_breakdown_current_assets['Capital Gain (%)'] = (
        100 * my_breakdown_current_assets[('Capital Gain', '')] /
        my_breakdown_current_assets[('Amount', 'Buy')]
    )

    # Resets the index and sort it
    my_breakdown_current_assets = (
        my_breakdown_current_assets
        .drop(['Broker Fee',
               'Tax Fee'],
              axis=1)
        .sort_values(by=['Currency',
                         'Capital Gain (%)'],
                     ascending=[True,
                                False])
    )

    print_df = my_breakdown_current_assets.copy()
    print_df = (
        print_df.reset_index(level=['Type',
                                    'Industry',
                                    'Market',
                                    'Code 2'], drop=True)
        .rename(columns={'Dividend': 'Div.'}, level=1)
    )

    print_df = (
        print_df.style
        .format(precision=2,
                na_rep='',
                thousands=",",
                formatter={('QTY.', 'Buy'): '{:d}',
                           ('QTY.', 'Div.'): '{:d}',
                           ('Current Rate', ''): '{:,.2f}',
                           ('Capital Gain', ''): '{:+,.2f}',
                           ('Capital Gain (%)', ''): '{:+,.2f}'}
                )
        .set_properties(
            subset=['Capital Gain (%)',
                    'Current Rate'], **{'width': '70px'}
        )
        .set_table_styles(
            [dict(selector="th", props=[('max-width', '250px')])]
        )
    )

    # Exports image
    image.export(print_df, port.parent_dir, 'table',
                 'breakdown_current_assets')

    return my_breakdown_current_assets


def total_fee(raw_data, port):
    """
    `total_fee` exports and returns a dataframe with the portfolio's total fees
    paid

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    my_total_fee : dataframe
        total fees paid.

    """

    my_total_fee = (
        raw_data
        .groupby(by=['Currency'])
        .agg({'Amount': 'sum',
              'Broker Fee': 'sum',
              'Tax Fee': 'sum'})
    )

    my_total_fee['Total Fee'] = (
        my_total_fee['Broker Fee'] + my_total_fee['Tax Fee']
    )
    my_total_fee['Total Fee (%)'] = (
        100 * my_total_fee['Total Fee'] / my_total_fee['Amount']
    )

    print_df = (
        my_total_fee.style
        .format(precision=2,
                na_rep='',
                thousands=",")
    )

    # Exports image
    image.export(print_df, port.parent_dir, 'table', 'total_fee')

    return my_total_fee


def cumulative_fee(raw_data, port):
    """
    `cumulative_fee` saves a line-graph of the cumulative amount paid in fees
    for all currencies.

    Parameters
    ----------
    raw_data : dataframe
        buy/sell/dividend log file.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    None.

    """

    # Copies `raw_data_negative` and renames it for better aesthetics
    my_cumulative_amount = (
        raw_data_negative(raw_data)
        .rename(columns={'Date (YYYY-MM-DD)': 'Year-Month'})
    )

    my_cumulative_amount['Total Fee'] = (
        my_cumulative_amount['Broker Fee'] +
        my_cumulative_amount['Tax Fee']
    )

    # Generates a year_month string to group the dataframe
    y_m = my_cumulative_amount['Year-Month'].dt.strftime('%y-%m')

    my_cumulative_amount = (
        my_cumulative_amount
        .groupby(by=[y_m, 'Currency'])
        .agg({'Total Fee': 'sum'})
        .unstack().fillna(0)
    )

    # Gets the multiplier for each currency
    multiplier = (
        my_cumulative_amount
        .replace(0, np.nan)
        .fillna(method='bfill')
        .iloc[0, :].values
    )
    currency = list(my_cumulative_amount.columns.levels[1])
    label = [
        f'{curr}: multiplier={mult:+,.2f}'
        for curr, mult in zip(currency, multiplier)
    ]

    # Normalizes according to the first month
    my_cumulative_amount = (
        my_cumulative_amount / multiplier
    )

    # Replaces nan for zero. This is necessary because
    # my_cumulative_amount / multiplier may return nan if both are zero
    my_cumulative_amount = my_cumulative_amount.fillna(0)

    # Saves graph
    image.cumulative_fee(my_cumulative_amount, label, port.parent_dir)


def fee_variable(raw_data, variable, port):
    """
    `fee_variable` returns and exports a dataframe with the portfolio's fee
    allocation per a variable input, such as industry, market, name, and type

    Parameters
    ----------
    current_assets : dataframe
        current assets in the portfolio.
    variable : str
        variable input, such as industry, market, name, and type.
    port : Portfolio
        instance of class Portfolio.

    Returns
    -------
    my_fee_variable : dataframe
        portfolio fee allocation per a variable input.

    """

    group = ['Type',
             'Industry',
             'Market',
             'Code',
             'Code 2',
             'Name',
             'Currency']

    my_fee_variable = (
        raw_data
        .groupby(by=group)
        .agg({'Amount': 'sum',
              'Broker Fee': 'sum',
              'Tax Fee': 'sum'})
    )

    my_fee_variable['Total Fee'] = (
        my_fee_variable['Broker Fee'] + my_fee_variable['Tax Fee']
    )

    my_fee_variable['Total Fee (%)'] = (
        100 * my_fee_variable['Total Fee'] / my_fee_variable['Amount']
    )

    # Sorts index by currency and total fee
    my_fee_variable = (
        my_fee_variable
        .sort_values(by=['Currency',
                         'Total Fee (%)'],
                     ascending=[True,
                                False]
                     )
    )

    print_df = my_fee_variable.copy()
    print_df = (
        print_df
        .groupby(by=[variable, 'Currency'])
        .agg({'Amount': 'sum',
              'Broker Fee': 'sum',
              'Tax Fee': 'sum',
              'Total Fee': 'sum',
              'Total Fee (%)': 'sum'})
        .sort_values(by=['Currency',
                         'Total Fee (%)'],
                     ascending=[True,
                                False])
    )

    # Defines aux dataframe. This has to be done before applying the style
    aux = print_df.copy().reset_index()

    print_df = (
        print_df.style
        .format(precision=2,
                na_rep='',
                thousands=",")
        .set_properties(
            subset=['Total Fee (%)'], **{'width': '70px'})
    )

    # Exports dataframe
    image.export(print_df, port.parent_dir, 'table', f'fee_{variable.lower()}')

    # Mask to combine low values together. Assets that have an allocation
    # of less than 5% are grouped together under the nane `Other`
    # If only one item has an allocation less than 5, then do not group
    mask = aux['Total Fee (%)'] < 0.15
    if sum(mask) > 1:
        aux.loc[mask, [variable]] = 'Other'

    aux = (
        aux
        .groupby(by=[variable, 'Currency'])
        .agg({'Amount': 'sum',
              'Broker Fee': 'sum',
              'Tax Fee': 'sum',
              'Total Fee': 'sum',
              'Total Fee (%)': 'sum'})
        .sort_values(by=['Currency',
                         'Total Fee (%)'],
                     ascending=[True,
                                False])
        .reset_index()
    )

    # After renaming items lower than 5% in the column `variable`, the
    # index can be reset
    aux = (
        aux.set_index([variable, 'Currency'])
    )

    # Saves image
    image.allocation_fee(aux, variable, port.parent_dir)

    return my_fee_variable


def price_history_pivot(df, port):
    """
    `price_history_pivot` returns a dataframe with the price history of all
    assets in a portfolio. The assets are sorted by `Code`, and a day shift
    is applied, if applicable.

    Parameters
    ----------
    df : dataframe
        portfolio allocation per name.
    port : Portfolio
        instance of the class Portfolio.

    Returns
    -------
    price_history_pivot : dataframe
        price history of the portfolio.

    """

    # Sort the dataframe so all assets are in the expected order
    df = df.sort_values(by=['Code'], ascending=True)

    # Get the list of symbols and names from `df`
    symbols_1 = df.index.get_level_values(level='Code').tolist()
    symbols_2 = df.index.get_level_values(level='Code 2').tolist()
    names = df.index.get_level_values(level='Name').tolist()

    # Add the benchmark's symbol and name to the lists
    symbols_1.append(port.benchmark[0])
    symbols_2.append(port.benchmark[0])
    names.append(port.benchmark[1])

    # Get the price history
    price_history = (
        acq.get_price_history(symbols_2, port)
    )

    # The price history uses `Code 2`, which is incompatible with the
    # `exchange_rate` that uses `Code`. To avoid issues, replace `Code 2` with
    # `Code`
    for s1, s2 in zip(symbols_1, symbols_2):
        price_history = price_history.replace(to_replace=s2, value=s1)

    # Pivot table of `price_history` is automatically sorted by `Code`
    price_history_pivot = (
        price_history
        .pivot(index='Date',
               columns='Symbol',
               values='Close')
        .reset_index()
    )
    price_history_pivot = price_history_pivot.set_index('Date')

    # Apply day shift if this option is set. If an asset has a comma in its
    # name, it means that it is a Korean asset and can be shifted
    for column in price_history_pivot:
        if (port.day_shift != 0) and ('.' in column):
            price_history_pivot[column] = (
                price_history_pivot[column].shift(port.day_shift)
            )

    return price_history_pivot
