"""
`acquisition` handles the data acquisition

"""

import datetime as dt

import pandas as pd
import yfinance as yf
from easymoney.money import EasyPeasy


def get_price_latest(ticker, port):
    """
     `get_price_latest` gets the latest price from Yahoo Finance. Becuase of
     different time zones it is common not to find the current price for all
     the assets. To avoid this missing data a time windows of two days is used.

    Parameters
    ----------
    ticker : list
        list of tickers.
    port : Portfolio
        instance of type Portfolio.

    Returns
    -------
    aux_df : DataFrame
        latest close price for all assets in the portfolio.

    """

    today = dt.datetime.today()

    try:
        aux_df = (pd.read_csv(
            f'../../resources/{port.parent_dir}/price/{today.strftime("%Y-%m-%d")}_latest.csv'))

    except FileNotFoundError:
        lower_limit = today - dt.timedelta(days=5)
        upper_limit = lower_limit + dt.timedelta(days=5)

        # Empty list to store the data from Yahoo Finance
        aux_list = []

        # Loop through all tickers in --ticker--
        for t in ticker:
            r = (
                yf.Ticker(t).history(start=lower_limit,
                                     end=upper_limit,
                                     auto_adjust=True)
            )

            # Add the current ticker to --Symbol-- column
            r['Symbol'] = t

            # Append
            aux_list.append(r)

        # Concatenate into aux_df
        aux_df = pd.concat(aux_list)

        # Remove possible duplicates, but keep the most recent one (last)
        aux_df = (
            aux_df.drop_duplicates('Symbol', keep='last')
        )

        # Reorganize the dataframe
        aux_df = aux_df.reset_index()
        aux_df = aux_df[['Date',
                         'Close',
                         'Symbol']]

        # Chage `Date` to datetime format
        aux_df['Date'] = pd.to_datetime(aux_df['Date'],
                                        format='%Y-%m-%d %H:%M:%S%z', utc=True)

        # Save aux_df as .csv. The file name is today's date plus _latest
        file_name = (
            f'../../resources/{port.parent_dir}/price/{today.strftime("%Y-%m-%d")}_latest.csv'
        )
        aux_df.to_csv(file_name, index=False, date_format='%Y-%m-%d')

    return aux_df


def get_price_history(ticker, port):
    """
    `get_price_history` gets the price history of all assets in the portfolio
    from Yahoo Finance.

    Parameters
    ----------
    ticker : list
        list of all assets in the portfolio.
    port : Portfolio
        instance of the class Portfolio.

    Returns
    -------
    aux_df : DataFrame
        price history of all assets in the portfolio.

    """

    today = dt.datetime.today().date()

    try:
        aux_df = pd.read_csv(
            f'../../resources/{port.parent_dir}/price/{today.strftime("%Y-%m-%d")}_historical.csv')

    except FileNotFoundError:
        # Check if period is a list of date-formated strings OR an int
        check_period(port)

        # Empty list to store the data from Yahoo Finance
        aux_list = []

        # Loop through all ticker in --ticker--
        for t in ticker:
            if isinstance(port.period, list):
                r = (
                    yf.Ticker(t).history(
                        start=dt.datetime.fromisoformat(port.period[0]),
                        end=dt.datetime.fromisoformat(port.period[1]),
                        auto_adjust=True
                    )
                )
            elif isinstance(port.period, int):
                start = today.replace(year=today.year - port.period)
                end = today
                r = (
                    yf.Ticker(t).history(
                        start=start,
                        end=end,
                        auto_adjust=True
                    )
                )

            # Add the current ticker to --Symbol-- column
            r['Symbol'] = t

            # Append
            aux_list.append(r)

        # Concatenate into aux_df
        aux_df = pd.concat(aux_list)

        # Reorganize the dataframe
        aux_df = aux_df.reset_index()
        aux_df = aux_df[['Date',
                         'Close',
                         'Symbol']]

        # Chage `Date` to datetime format
        aux_df['Date'] = pd.to_datetime(aux_df['Date'],
                                        format='%Y-%m-%d %H:%M:%S%z', utc=True)

        # Save aux_df as .csv. The file name is today's date plus _latest
        file_name = (
            f'../../resources/{port.parent_dir}/price/{today.strftime("%Y-%m-%d")}_historical.csv'
        )
        aux_df.to_csv(file_name, index=False, date_format='%Y-%m-%d')

    return aux_df


def get_exchange_rate(df, port):
    """
    `get_exchange_rate` gets the exchange rate from EasyPeasy

    Parameters
    ----------
    df : DataFrame
        breakdown of all current assets in the portfolio.
    port : Portfolio
        instance of type Portfolio.

    Returns
    -------
    aux_df : DataFrame
        exchange rate.

    """

    today = dt.datetime.today()

    try:
        aux_df = pd.read_csv(
            f'../../resources/{port.parent_dir}/rate/{today.strftime("%Y-%m-%d")}_rate.csv')

    except FileNotFoundError:
        ep = EasyPeasy()

        # Get the list of ticker from df
        ticker = (
            df.index.get_level_values(level='Code').tolist()
        )

        # Get the list of currencies from df
        currency_list = (
            df.index.get_level_values(level='Currency').tolist()
        )

        # Empty list to store the data from Yahoo Finance
        aux_list = []

        # Loop through all ticker and currencies in --ticker-- and
        # --currency_list--
        for t, currency in zip(ticker, currency_list):
            # Check if the current currency is KRW. If yes, then simply assign
            # r = 1
            if currency == 'KRW':
                r = 1
            # For currencies other than KRW, download the exchange rate
            else:
                r = (
                    ep.currency_converter(
                        amount=1,
                        from_currency=currency,
                        to_currency='KRW',
                        pretty_print=False)
                )

            # Append
            aux_list.append([r, t])

        # Make list into dataframe
        aux_df = (
            pd.DataFrame(
                aux_list,
                columns=['Rate',
                         'Code']
            )
        )

        # Save aux_df as .csv. The file name is today's date plus _latest
        file_name = (
            f'../../resources/{port.parent_dir}/rate/{today.strftime("%Y-%m-%d")}_rate.csv'
        )
        aux_df.to_csv(file_name, index=False)

    return aux_df


def check_period(port):
    """
    `check_period` checks the format of the historical price data in the
    configuration file. There are two options: 1) period and 2) years.

    1) period: it should be a list of dates in which the first element is the
    initial date and the second element is the final date. The dates should
    follow the ISO date format (YYYY-MM-DD).
    2) years: it should be an int that represents tot total number os years,
    counting from today.

    Parameters
    ----------
    port : Portfolio
        instance of type Portfolio.

    Raises
    ------
    SyntaxError
        If the period is invalid or does not follow the expected format.

    Returns
    -------
    None.

    """

    period = port.period

    if isinstance(period, list):
        if len(period) != 2:
            msg = (
                "Period should be a list of size two. The first element "
                "should be the start date and the second element should be "
                "the end date. Please note that the date should follow the "
                "ISO date format (YYYY-MM-DD).")
            raise SyntaxError(msg)

        for p in period:
            try:
                dt.datetime.fromisoformat(p)
            except ValueError:
                msg = (
                    "Period does not follow the ISO date format (YYYY-MM-DD). "
                    "Please, modify the `.config` file accordingly.")
                raise SyntaxError(msg)

    elif not isinstance(period, int):
        msg = (
            "Period does not follow the `years` format. Please, modify the "
            "`.config` file with the correct format.")
        raise SyntaxError(msg)
