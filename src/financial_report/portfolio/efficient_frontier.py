import numpy as np
import pandas as pd
import scipy.optimize as sco
from data import acquisition as acq
from data import processing as proc
from report import image


def get_portfolio_performance(weight, mean_daily_return, cov_matrix):
    """
    `get_portfolio_performance` returns the expected portfolio return and
    volatility for a given portfolio, in which the allocation of each asset
    is defined by the corresponding weight

    Parameters
    ----------
    weight : Array of float64
        allocation of each asset in the portfolio. The allocation value of all
        assets should sum up to 100.
    mean_daily_return : Series
        mean daily return for all assets in the portfolio. This value is
        calculated from the historical data.
    cov_matrix : DataFrame
        covariance matrix of all assets in the portfolio combined two by two.

    Returns
    -------
    portfolio_return : float64
        expected return for the portfolio with the given allocation.
    portfolio_volatility : float64
        expected volatility for the portfolio with the given allocation.

    """

    portfolio_return = np.sum(mean_daily_return*weight)
    portfolio_volatility = np.sqrt(
        np.dot(weight.T, np.dot(cov_matrix, weight))
    )

    return portfolio_return, portfolio_volatility


def get_portfolio_volatility(weight, mean_daily_return, cov_matrix):
    """
    `get_portfolio_volatility` returns the expected portfolio volatility for
    a given weight

    Parameters
    ----------
    weight : Array of float64
        allocation of each asset in the portfolio. The allocation value of all
        assets should sum up to 100.
    mean_daily_return : Series
        mean daily return for all assets in the portfolio. This value is
        calculated from the historical data.
    cov_matrix : DataFrame
        covariance matrix of all assets in the portfolio combined two by two.

    Returns
    -------
    float64
        expected portfolio volatility.

    """

    return get_portfolio_performance(weight,
                                     mean_daily_return,
                                     cov_matrix)[1]


def get_sharpe_ratio(weight, mean_daily_return, cov_matrix, risk_free):
    """
    `get_sharpe_ratio` returns the negative Sharpe Ratio of a portfolio for
    a given weight and risk free rate. The Sharpe Ratio must be negative
    because it must be maximized using a minimization function

    Parameters
    ----------
    weight : Array of float64
        allocation of each asset in the portfolio. The allocation value of all
        assets should sum up to 100.
    mean_daily_return : Series
        mean daily return for all assets in the portfolio. This value is
        calculated from the historical data.
    cov_matrix : DataFrame
        covariance matrix of all assets in the portfolio combined two by two.
    risk_free : float
        risk free rate used to calculate the Sharpe ratio.

    Returns
    -------
    float64
        Sharpe ratio.

    """

    port_ret, port_vol = (
        get_portfolio_performance(weight, mean_daily_return, cov_matrix)
    )

    # Calculate the annualized portfolio return and volatility
    port_ret = port_ret * 260
    port_vol = port_vol * np.sqrt(260)

    # Check if --port_ret-- is greater than --risk_free-- to make sure this
    # function only returns a negative value
    if port_ret > risk_free:
        return -(port_ret - risk_free) / port_vol
    else:
        return (port_ret - risk_free) / port_vol


def get_efficient_return(target_return, mean_daily_return, cov_matrix,
                         condition):
    """
    `get_efficient_return` returns the weights that minimizes the volatility
    of a portfolio for a specified target return

    Parameters
    ----------
    target_return : float64
        target return of the portfolio.
    mean_daily_return : Series
        mean daily return for all assets in the portfolio. This value is
        calculated from the historical data.
    cov_matrix : DataFrame
        covariance matrix of all assets in the portfolio combined two by two.
    condition : float64
        minimum allocation for all assets.

    Returns
    -------
    list of OptimizeResult
        Portfolio allocation that minimized volatility for a given target
        return.

    """

    num_assets = len(mean_daily_return.index)
    args = (mean_daily_return, cov_matrix)

    def get_portfolio_return(weight):
        return get_portfolio_performance(weight,
                                         mean_daily_return,
                                         cov_matrix)[0]

    # Set the constraints
    # 1: portfolio return must equal the target return
    # 2: the sum of the weight must be one
    constraints = (
        {'type': 'eq', 'fun': lambda x: get_portfolio_return(
            x) - target_return},
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'ineq', 'fun': lambda x: x - condition}
    )

    # Sequence of (min, max) pairs for each element in x (weight)
    # There are as many bounds as assets
    bounds = tuple((0, 1) for asset in range(num_assets))

    # Initial guess
    # The initial guess is 1/num_assets for all assets. For instance, if
    # there are five assets, then the initial guess for each one is 0.2
    guess = num_assets*[1./num_assets]

    return sco.minimize(get_portfolio_volatility,
                        guess,
                        args=args,
                        method='SLSQP',
                        bounds=bounds,
                        constraints=constraints)


def get_efficient_frontier(range_return, mean_daily_return, cov_matrix,
                           condition):
    """
    `get_efficient_frontier` returns the efficient portfolio for a spicified
    target return range, that is, the weights of a portfolio that minimizes
    volatility

    Parameters
    ----------
    range_return : Array of float64
        Range of the portfolio return over which the efficient frontier is
        calculated.
    mean_daily_return : Series
        mean daily return for all assets in the portfolio. This value is
        calculated from the historical data.
    cov_matrix : DataFrame
        covariance matrix of all assets in the portfolio combined two by two.
    condition : float64
        minimum allocation for all assets.

    Returns
    -------
    efficient_portfolio : list of OptimizeResult
        Portfolio allocation that minimized volatility for a given target
        return.

    """

    efficient_portfolio = []

    for r in range_return:
        efficient_portfolio.append(
            get_efficient_return(r, mean_daily_return,
                                 cov_matrix, condition)
        )

    return efficient_portfolio


def get_portfolio_min_volatility(mean_daily_return, cov_matrix, condition):
    """
    `get_portfolio_min_volatility` returns the portfolio weights that
    minimize the volatility. The function that is minimized is
    `get_portfolio_volatility`, in which the `mean_daily_return` and
    `cov_matrix` are the fixed parameters needed to completely specify the
    function

    Parameters
    ----------
    mean_daily_return : Series
        mean daily return for all assets in the portfolio. This value is
        calculated from the historical data.
    cov_matrix : DataFrame
        covariance matrix of all assets in the portfolio combined two by two.
    condition : float64
        minimum allocation for all assets.

    Returns
    -------
    list of OptimizeResult
        Portfolio allocation that minimized volatility for a given target
        return.

    """

    num_assets = len(mean_daily_return.index)
    args = (mean_daily_return, cov_matrix)

    # Set the constraints
    # 1: the sum of the weight must be one
    constraints = (
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'ineq', 'fun': lambda x: x - condition}
    )

    # Sequence of (min, max) pairs for each element in x (weight)
    # There are as many bounds as assets
    bounds = tuple((0, 1) for asset in range(num_assets))

    # Initial guess
    # The initial guess is 1/num_assets for all assets. For instance, if
    # there are five assets, then the initial guess for each one is 0.2
    guess = num_assets*[1./num_assets]

    return sco.minimize(get_portfolio_volatility,
                        guess,
                        args=args,
                        method='SLSQP',
                        bounds=bounds,
                        constraints=constraints)


def get_portfolio_max_sharpe(mean_daily_return, cov_matrix, risk_free,
                             condition):
    """
    `get_portfolio_max_sharpe` returns the portfolio weights that
    maximize the Sharpe Ratio. The function that is maximized is
    `get_sharpe_ratio`, in which the `mean_daily_return` and `cov_matrix` are
    the fixed parameters needed to completely specify the function

    Parameters
    ----------
    mean_daily_return : Series
        mean daily return for all assets in the portfolio. This value is
        calculated from the historical data.
    cov_matrix : DataFrame
        covariance matrix of all assets in the portfolio combined two by two.
    risk_free : float
        risk free rate used to calculate the Sharpe ratio.
    condition : float64
        minimum allocation for all assets.

    Returns
    -------
    list of OptimizeResult
        Portfolio allocation that maximizes the Sharpe ratio for a given target
        return.
    """

    num_assets = len(mean_daily_return.index)
    args = (mean_daily_return, cov_matrix, risk_free)

    # Set the constraints
    # 1: the sum of the weight must be one
    constraints = (
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'ineq', 'fun': lambda x: x - condition}
    )

    # Sequence of (min, max) pairs for each element in x (weight)
    # There are as many bounds as assets
    bounds = tuple((0, 1) for asset in range(num_assets))

    # Initial guess
    # The initial guess is 1/num_assets for all assets. For instance, if
    # there are five assets, then the initial guess for each one is 0.2
    guess = num_assets*[1./num_assets]

    return sco.minimize(get_sharpe_ratio,
                        guess,
                        args=args,
                        method='SLSQP',
                        bounds=bounds,
                        constraints=constraints)


def run(df, port):
    """
    `run` runs the calculation of the portfolio's efficient frontier. It
    exports a graph containing the following: i) randomly generated portfolios,
    ii) efficient frontier, iii) portfolio with minimum volatility, iv)
    portfolio with maximum Sharpe Ratio, and v) current portfolio. In addition,
    `run` exports a table containing the weights of items iii) to v)

    Parameters
    ----------
    df : DataFrame
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

    # Required data
    num_assets = len(df.index)
    mean_daily_return = daily_return.mean()
    cov_matrix = daily_return.cov()

    # Initialize an empty array to hold the random portfolios
    random_portfolio = np.zeros((3, port.num_sim))

    for i in range(port.num_sim):

        # Generate random weights to each asset
        weight = np.random.random(num_assets)
        weight /= np.sum(weight)

        # Calculate the performance of a random portfolio
        portfolio_return, portfolio_volatility = (
            get_portfolio_performance(weight, mean_daily_return, cov_matrix)
        )

        # random_portfolio[0, i]: annualized return
        # random_portfolio[1, i]: annualized volatility
        # random_portfolio[2, i]: sharpe ratio
        random_portfolio[0, i] = portfolio_return*260
        random_portfolio[1, i] = portfolio_volatility*np.sqrt(260)
        random_portfolio[2, i] = (
            (random_portfolio[0, i] - port.risk_free)/random_portfolio[1, i]
        )

    # Get efficient portfolios without condition
    range_return = np.linspace(-0.3, 0.3, 100)/260
    efficient_portfolio = (
        get_efficient_frontier(range_return, mean_daily_return, cov_matrix, -1)
    )

    # Get efficient portfolios with condition (at least 5% allocation)
    range_return = np.linspace(-0.3, 0.3, 100)/260
    efficient_portfolio_cond = (
        get_efficient_frontier(
            range_return, mean_daily_return, cov_matrix, 0.05)
    )

    # Scatter plot with minimum volatility portfolio without condition
    # min_volatility is the optimization object that holds the weights of the
    # portfolio with minimum volatility
    min_volatility = (
        get_portfolio_min_volatility(mean_daily_return, cov_matrix, -1)
    )
    ret_min, vol_min = (
        get_portfolio_performance(
            min_volatility['x'], mean_daily_return, cov_matrix)
    )
    min_vol_portfolio = [ret_min, vol_min]

    # Scatter plot with minimum volatility portfolio with condition
    # min_volatility is the optimization object that holds the weights of the
    # portfolio with minimum volatility
    min_volatility_cond = (
        get_portfolio_min_volatility(mean_daily_return, cov_matrix, 0.05)
    )
    ret_min_cond, vol_min_cond = (
        get_portfolio_performance(
            min_volatility_cond['x'], mean_daily_return, cov_matrix)
    )
    min_vol_portfolio_cond = [ret_min_cond, vol_min_cond]

    # Scatter plot with maximum sharpe ratio portfolio without condition
    # max_sharpe is the optimization object that holds the weights of the
    # portfolio with maximum sharpe ratio
    max_sharpe = (
        get_portfolio_max_sharpe(
            mean_daily_return, cov_matrix, port.risk_free, -1)
    )
    ret_max, vol_max = (
        get_portfolio_performance(
            max_sharpe['x'], mean_daily_return, cov_matrix)
    )
    max_sharpe_portfolio = [ret_max, vol_max]

    # Scatter plot with maximum sharpe ratio portfolio with condition
    # max_sharpe is the optimization object that holds the weights of the
    # portfolio with maximum sharpe ratio
    max_sharpe_cond = (
        get_portfolio_max_sharpe(
            mean_daily_return, cov_matrix, port.risk_free, 0.05)
    )
    ret_max_cond, vol_max_cond = (
        get_portfolio_performance(
            max_sharpe_cond['x'], mean_daily_return, cov_matrix)
    )
    max_sharpe_portfolio_cond = [ret_max_cond, vol_max_cond]

    # Get the exchange rate to convert the secondary currencies to the
    # primary currency (KRW)
    exchange_rate = (
        acq.get_exchange_rate(df, port)
        .sort_values(by=['Code'], ascending=[True])
    )

    # Scatter plot with the corrent portfolio weight
    allocation = (
        df
        .sort_values(by=['Code'], ascending=True)['Amount'].values *
        exchange_rate['Rate'].values
    )
    allocation = allocation / allocation.sum()
    ret_curr, vol_curr = (
        get_portfolio_performance(
            allocation, mean_daily_return, cov_matrix)
    )
    current_portfolio = [ret_curr, vol_curr]

    # MINIMUM VOLATILITY
    min_vol = np.round(min_volatility['x']*100, 2)

    # MINIMUM VOLATILITY WITH CONDITION
    min_vol_cond = np.round(min_volatility_cond['x']*100, 2)

    # MAXIMUM SHARPE RATIO
    max_sharpe = np.round(max_sharpe['x']*100, 2)

    # MAXIMUM SHARPE RATION WITH CONDITION
    max_sharpe_cond = np.round(max_sharpe_cond['x']*100, 2)

    # Combine all lists in a dataframe
    index = (
        df
        .sort_values(by=['Code'], ascending=True)
        .index.get_level_values(level='Name').tolist()
    )
    list_all = list(zip(min_vol,
                        min_vol_cond,
                        max_sharpe,
                        max_sharpe_cond,
                        allocation*100))
    columns = (['Min. Volatility',
                'Min. Volatility (5%)',
                'Max. Sharpe Ratio',
                'Max. Sharpe Ratio (5%)',
                'Current Portfolio'])
    df_all = (
        pd.DataFrame(data=list_all,
                     index=index,
                     columns=columns)
    )

    # Add extra information
    df_all.loc[''] = np.nan
    df_all.loc['Annualized Return'] = (
        [f'{ret_min*260*100:+,.2f}%',
         f'{ret_min_cond*260*100:+,.2f}%',
         f'{ret_max*260*100:+,.2f}%',
         f'{ret_max_cond*260*100:+,.2f}%',
         f'{ret_curr*260*100:+,.2f}%']
    )
    df_all.loc['Annualized  Volatility'] = (
        [f'{vol_min*np.sqrt(260)*100:+,.2f}%',
         f'{vol_min_cond*np.sqrt(260)*100:+,.2f}%',
         f'{vol_max*np.sqrt(260)*100:+,.2f}%',
         f'{vol_max_cond*np.sqrt(260)*100:+,.2f}%',
         f'{vol_curr*np.sqrt(260)*100:+,.2f}%']
    )

    df_print = (
        df_all.style
        .format(precision=2,
                na_rep='')
    )

    # Export image
    image.efficient_frontier(range_return, random_portfolio,
                             efficient_portfolio, efficient_portfolio_cond,
                             min_vol_portfolio, min_vol_portfolio_cond,
                             max_sharpe_portfolio, max_sharpe_portfolio_cond,
                             current_portfolio, port)
    image.export(df_print, port.parent_dir, 'table', 'efficient_frontier')
