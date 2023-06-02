"""
`export_image` handles the image exporting
"""

import dataframe_image as dfi
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def export(df, directory, subdirectory, name, format='.png', fontsize=12,
           table_conversion='chrome'):
    """
    `export` exports the dataframe `df` as an image to
    `./resources/directory/subdirectory` using the provided name, format,
    font size, and dataframe-image conversion method.

    Parameters
    ----------
    df : dataframe
        dataframe table that is converted to image.
    directory : str
        directory where the image is saved.
    subdirectory : str
        subdirectory where the image is saved.
    name : str
        name of the image saved.
    format : str, optional
        format of the image saved. The default is '.png'.
    fontsize : int32, optional
        font size of the image saved. The default is 12.
    table_conversion : str, optional
        dataframe-image conversion method. The default is 'matplotlib'.

    Returns
    -------
    None.

    """

    dfi.export(df,
               f'../../resources/{directory}/{subdirectory}/{name}{format}',
               fontsize=fontsize,
               table_conversion=table_conversion,
               dpi=100)


def save(plot, directory, subdirectory, name, format='.png', padding=0):
    """
    `save` saves a plot in the provided directory/subdirectory using the
    provided name

    Parameters
    ----------
    plot : AxesSubplot
        matplotlib object to be plotted.
    directory : str
        directory where the image is saved.
    subdirectory : str
        subdirectory where the image is saved.
    name : str
        name of the image.
    format : str, optional
        format of the image. The default is '.png'.

    Returns
    -------
    None.

    """

    if isinstance(plot, plt.Figure):
        fig = plot
        fig.tight_layout(pad=padding)
    elif isinstance(plot, sns.matrix.ClusterGrid):
        fig = plot
    elif isinstance(plot, plt.Axes):
        fig = plot.get_figure()
        fig.tight_layout(pad=padding)

    fig.savefig(
        f'../../resources/{directory}/{subdirectory}/{name}{format}',
        bbox_inches='tight',
        dpi=100)


def cumulative_amount(df, label, directory):
    """
    `cummulative_amount` plots a line-graph of the cumulative amount invested
    for all currencies.

    Parameters
    ----------
    df : dataframe
        cummulative amount invested.
    label : list
        list of multiplier for each currency. This is necessary when plotting
        different currencies on the same graph, so they are normalized.
    directory : str
        directory where the log file is located.

    Returns
    -------
    None.

    """

    sns.set_theme()

    # Plots graph
    plot = (
        df.cumsum()
        .plot(marker='o',
              figsize=(16, 7.12))
    )
    plt.legend(label)
    plt.ylabel('Normalized Invested Capital')

    # Exports graph
    save(plot, directory, 'graph', 'cumulative_amount')
    plt.close()


def cumulative_fee(df, label, directory):
    """
    `cumulative_fee` plots a line-graph of the cumulative fees paid for all
    currencies.

    Parameters
    ----------
    df : dataframe
        cummulative amount invested.
    label : list
        list of multiplier for each currency. This is necessary when plotting
        different currencies on the same graph, so they are normalized.
    directory : str
        directory where the log file is located.

    Returns
    -------
    None.

    """

    sns.set_theme()

    # Plots graph
    plot = (
        df.cumsum()
        .plot(marker='o',
              figsize=(16, 7.12))
    )
    plt.legend(label)
    plt.ylabel('Normalized Total Fee')

    # Exports graph
    save(plot, directory, 'graph', 'cumulative_fee')
    plt.close()


def allocation_variable(df, variable, directory):
    """
    `allocation_variable` plots a pie chart of the allocated amount per a
    variable input, such as industry, market, name, and type.

    Parameters
    ----------
    df : dataframe
        current assets in the portfolio.
    variable : str
        variable input, such as industry, market, name, and type.
    directory : str
        directory where the log file is located.

    Returns
    -------
    None.

    """

    # Plots chart
    plot = (
        df['Allocation (%)'].unstack().fillna(0)
        .plot.pie(subplots=True,
                  autopct=lambda p: '{:.2f}%'.format(p) if p > 0 else '',
                  figsize=(18, 6),
                  labeldistance=None)
    )

    # Positions legend box for each plot
    for plot in plot:
        plot.legend(
            bbox_to_anchor=(0.95, 0.5),
            loc="center left",
            fontsize=10
        )

    # Saves image
    save(plot, directory, 'graph', f'allocation_{variable.lower()}')
    plt.close()


def allocation_fee(df, variable, directory):
    """
    `allocation_fee` plots a pie chart of the allocated fees per a variable
    input, such as industry, market, name, and type.

    Parameters
    ----------
    df : dataframe
        current assets in the portfolio.
    variable : str
        variable input, such as industry, market, name, and type.
    directory : str
        directory where the log file is located.

    Returns
    -------
    None.

    """

    # Plots chart
    plot = (
        df['Total Fee (%)'].unstack().fillna(0)
        .plot.pie(subplots=True,
                  autopct=lambda p: '{:.2f}%'.format(p) if p > 0 else '',
                  figsize=(18, 6),
                  labeldistance=None,
                  normalize=True)
    )

    # Positions legend box for each plot
    for plot in plot:
        plot.legend(
            bbox_to_anchor=(0.95, 0.5),
            loc="center left",
            fontsize=10
        )

    # Saves image
    save(plot, directory, 'graph', f'fee_{variable.lower()}')
    plt.close()


def beta(df, beta, port):
    """
    `beta` plots a graphical representation of an asset volatility in relation
    to a benchmark.  This representation consists of two parts: i) scatter
    plot and ii) line plot. The scatter plot shows the benchmark's daily price
    variation by the asset's daily price variation. The line plot is the linear
    fit of the scatter plot, and the proper beta value.

    Parameters
    ----------
    df : dataframe
        portfolio allocatio per name.
    beta : list
        contains the asset's name, code, and price history.
    port : Portfolio
        instance of the class Portfolio.

    Returns
    -------
    None.

    """

    # Parameters to make a subplot. The subplot is 3 rows by n columns, where
    # n depends on the number of assets
    plot_columns = 3
    plot_rows = (
        (len(df.columns) // plot_columns) +
        (len(df.columns) % plot_columns)
    )
    plot_position = 1

    # Make figure with size proportional to numberof plot_columns (3) and
    # plot_rows (depends on the number of assets)
    fig = plt.figure(figsize=(5*plot_columns, 4*plot_rows))

    for b in beta:
        name = b[0]
        model = b[2]
        x_1, y_1 = b[3][0], b[3][1]
        x_2 = np.linspace(-0.1, 0.1, 1000)
        y_2 = (x_2 * model.coef_ + model.intercept_).reshape((-1, 1))

        ax = fig.add_subplot(plot_rows, plot_columns, plot_position)
        ax.set_ylim(-0.11, 0.11)
        ax.set_xlim(-0.11, 0.11)
        ax.scatter(x_1, y_1, color='gray')
        ax.plot(x_2, y_2, color='black')
        ax.set_xlabel('Benchmark price change')
        ax.set_ylabel('Asset price change')
        ax.set_title(name)

        # Increment the position in the subplot
        plot_position += 1

    # Exports graph
    save(fig, port.parent_dir, 'graph', 'beta_all', padding=3)
    plt.close()


def correlation(corr_matrix, names, port):
    """
    `correlation` plots the portfolio's correlation matrix

    Parameters
    ----------
    corr_matrix : DataFrame
        Correlation between every combination of two assets in the portfolio.
    names : list
        Names of all assets in the portfolio.
    port : Portfolio
        Instance of the class Portfolio.

    Returns
    -------
    None.

    """

    # Calculates the figure size depending on the number of assets
    def fig_size():
        return 0.8 * len(names) + 2.4

    # Chart
    fig = sns.clustermap(corr_matrix,
                         cmap='RdYlGn',
                         vmax=1.0,
                         vmin=-1.0,
                         mask=False,
                         linewidths=2.5,
                         annot=True,
                         dendrogram_ratio=(0.3, 0.3),
                         fmt='.2f',
                         figsize=(fig_size(), fig_size()))
    sns.set_style('darkgrid')
    sns.set(font_scale=1)
    ax = fig.ax_heatmap
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.setp(fig.ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
    plt.setp(fig.ax_heatmap.xaxis.get_majorticklabels(), rotation=90)

    # Exports graph
    save(fig, port.parent_dir, 'graph', 'correlation_matrix')
    plt.close()


def price_history(norm_price_history, equal_weight_portfolio,
                  weighted_portfolio, port):
    """
    `price_history` plots the price history of each individual asset in a
    portfolio, of the portfolio considering the current allocation, and of
    a dummy portfolio in which all assets have the same weight

    Parameters
    ----------
    norm_price_history : DataFrame
        Price history of each individual asset in a portfolio normalized by
        the initial close price.
    equal_weight_portfolio : Series
        Price history of a dummy portfolio in which all assets have the same
        allocation.
    weighted_portfolio : Series
        Price history of the given portfolio considering the current
        allocation.
    port : Portfolio
        Instance of the class Portfolio.

    Returns
    -------
    None.

    """

    plot = (
        norm_price_history.plot(alpha=0.5, figsize=(18, 8))
    )
    equal_weight_portfolio.plot(color='black', label='Equal-weight Portfolio')
    weighted_portfolio.plot(color='blue', label='Current Portfolio')
    plt.legend()
    plt.ylabel("Normalized price history")

    # Exports graph
    save(plot, port.parent_dir, 'graph', 'price_history')
    plt.close()


def monte_carlo(portfolio_sims, port):
    """
    `monte_carlo` plots the Monte Carlo simulation of the portfolio.

    Parameters
    ----------
    portfolio_sims : DataFrame
        Simulation results.
    port : Portfolio
        Instance of the class Portfolio.

    Returns
    -------
    None.

    """

    # Plot chart
    plot = (
        portfolio_sims.plot(figsize=(18, 8))
    )
    plt.axhline(y=1, color='black', linestyle='-', label='1')
    plt.ylabel('Portfolio Return')
    plt.xlabel('Days')
    plt.title('Monte Carlo Simulation')
    plt.legend().set_visible(False)

    # Save graph
    save(plot, port.parent_dir, 'graph', 'monte_carlo')
    plt.close()


def efficient_frontier(range_return, random_portfolio, efficient_portfolio,
                       efficient_portfolio_cond, min_vol_portfolio,
                       min_vol_portfolio_cond, max_sharpe_portfolio,
                       max_sharpe_portfolio_cond, current_portfolio,
                       port):
    """
    `efficient_frontier` plots the efficient frontier analysis of a portfolio.
    The following elements are included:

        i) scatter plot of randomly generated portfolios (random weights) and
           their respective volatility and return
        ii) line plot of the portfolio efficient frontier with and without
            condition. A condition is a minimum weight values that must be
            (randomly) assigned to each asset
        iii) scatter plot of the portfolio with minimum volatility with and
             without condition
        iv) scatter plot of the portfolio with maximum Sharpe Ratio with and
            without condition
        v) current portfolio

    Parameters
    ----------
    range_return : Array of float64
        Range of the portfolio return over which the efficient frontier is
        calculated.
    random_portfolio : Array of float64
        Resulting annualized return, annualized volatility, and Sharpe Ratio
        of a randomly generated portfolio. The length of the array is the
        number of simulations.
    efficient_portfolio : list of OptimizeResult
        Portfolio allocation that minimized volatility for a given target
        return.
    efficient_portfolio_cond : list of OptimizeResult
        Portfolio allocation, with a minimum allocation for all assets, that
        minimized volatility for a given target return.
    min_vol_portfolio : list
        Return (index 0) and volatility (index 1) of the portfolio that shows
        the lowest volatility.
    min_vol_portfolio_cond : list
        Return (index 0) and volatility (index 1) of the portfolio, with a
        minimum allocation for all assets, that shows the lowest volatility.
    max_sharpe_portfolio : list
        Return (index 0) and volatility (index 1) of the portfolio that shows
        the highest Sharpe ratio.
    max_sharpe_portfolio_cond : list
        Return (index 0) and volatility (index 1) of the portfolio, with a
        minimum allocation for all assets, that shows the highest Sharpe ratio.
    current_portfolio : list
        Return (index 0) and volatility (index 1) of the portfolio considering
        the current allocation
    port : Portfolio
        Instance of the class portfolio.

    Returns
    -------
    None.

    """

    # Plot chart
    plot = plt.figure(figsize=(12, 8))

    # Scatter plot of randomly generated portfolios
    plt.scatter(random_portfolio[1, :],
                random_portfolio[0, :],
                c=random_portfolio[2, :],
                marker='o',
                cmap='RdYlGn',
                edgecolors='black',
                linewidths=0.5,
                label='Randomly generated portfolios')

    # Line plot of portfolios in the efficient frontier without condition
    plt.plot([p['fun']*np.sqrt(260) for p in efficient_portfolio],
             range_return*260,
             linestyle='-',
             label='Efficient frontier')

    # Line plot of portfolios in the efficient frontier with condition
    plt.plot([p['fun']*np.sqrt(260) for p in efficient_portfolio_cond],
             range_return*260,
             linestyle='--',
             label='Efficient frontier (5%)')

    # Scatter plot with minimum volatility portfolio without condition
    plt.plot(min_vol_portfolio[1]*np.sqrt(260),
             min_vol_portfolio[0]*260,
             'kP',
             label='Portfolio with min. volatility')

    # Scatter plot with minimum volatility portfolio with condition
    plt.plot(min_vol_portfolio_cond[1]*np.sqrt(260),
             min_vol_portfolio_cond[0]*260,
             'kP')

    # Scatter plot with maximum sharpe ratio portfolio without condition
    plt.plot(max_sharpe_portfolio[1]*np.sqrt(260),
             max_sharpe_portfolio[0]*260,
             'k*',
             label='Portfolio with max. Sharpe ratio')

    # Scatter plot with maximum sharpe ratio portfolio without condition
    plt.plot(max_sharpe_portfolio_cond[1]*np.sqrt(260),
             max_sharpe_portfolio_cond[0]*260,
             'k*')

    # Scatter plot with the corrent portfolio weight
    plt.plot(current_portfolio[1]*np.sqrt(260),
             current_portfolio[0]*260,
             'ks',
             label='Current portfolio')

    plt.grid(True)
    plt.xlabel('Annualized Volatility')
    plt.ylabel('Annualized Return')
    plt.colorbar(label='Sharpe Ratio')
    plt.title('Efficient Frontier')
    plt.legend()

    # Exports graph
    save(plot, port.parent_dir, 'graph', 'efficient_frontier')
    plt.close()
