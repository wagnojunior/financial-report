from data import processing as proc
from portfolio import (beta, correlation, efficient_frontier, monte_carlo,
                       portfolio, price_history)
from report import generator as gen
from utils import email
from utils import file_system as fs


def run():

    fs.set_workingDir(__file__)

    portfolios = fs.get_portfolios()

    for port_dir in portfolios:
        # Create the file system
        fs.create(port_dir)

        # Loads a portfolio configuration and checks if environment
        # variables are set for this portfolio
        port = portfolio.importt(port_dir)
        fs.check_env(port_dir)

        # Download input file from Google Drive
        fs.download_rawData(port)

        # Call methods
        raw_data = proc.raw_data(port)
        all_assets = proc.all_assets(raw_data, port)
        current_assets = proc.current_assets(raw_data, port)
        _ = proc.total_invested(raw_data, port)
        _ = proc.cumulative_amount(raw_data, port)
        allocation_name = (
            proc.allocation_variable(current_assets,
                                     'Name',
                                     port)
        )
        _ = (
            proc.allocation_variable(current_assets,
                                     'Type',
                                     port)
        )
        _ = (
            proc.allocation_variable(current_assets,
                                     'Industry',
                                     port)
        )
        _ = (
            proc.allocation_variable(current_assets,
                                     'Market',
                                     port)
        )
        _ = (
            proc.assets_dividend(raw_data,
                                 all_assets,
                                 port)
        )
        _ = (
            proc.breakdown_current_assets(raw_data,
                                          current_assets,
                                          port)
        )
        _ = proc.total_fee(raw_data, port)
        _ = proc.cumulative_fee(raw_data, port)
        _ = proc.fee_variable(raw_data, 'Name', port)
        _ = proc.fee_variable(raw_data, 'Type', port)
        _ = proc.fee_variable(raw_data, 'Industry', port)
        _ = proc.fee_variable(raw_data, 'Market', port)
        _ = proc.past_assets(raw_data, port)
        _ = (
            proc.breakdown_past_assets(raw_data, port)
        )
        _ = proc.passive_portfolio(current_assets, port)
        _ = proc.active_portfolio(current_assets, port)

        # Beta
        beta.run(allocation_name, port)

        # Correlation matrix
        correlation.run(allocation_name, port)

        # Price history
        price_history.run(allocation_name, port)

        # Monte Carlo simulation
        monte_carlo.run(allocation_name, port)

        # Efficient frontier
        efficient_frontier.run(allocation_name, port)

        # Generates the report
        gen.run(port)

        # Send email
        email.send(port)


if __name__ == '__main__':
    run()
