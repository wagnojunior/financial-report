import time
from datetime import datetime as dt

from fpdf import FPDF, TitleStyle
from PIL import Image

CONV = 0.2645833333  # convertion factor from px to mm for a dpi of 96
RESIZE_GRAPH = 0.5  # resize factor for graphs
RESIZE_TABLE = 0.7  # resize factor for tables


class MYPDF(FPDF):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.WIDTH = port.page_width
        self.HEIGHT = port.page_height

    def header(self):
        # Checks the page orientation
        if self.epw < self.eph:
            self.image(
                f'../../resources/{self.port.parent_dir}/header/{self.port.header_portrait}',
                0, 0, self.port.page_width
            )
        else:
            self.image(
                f'../../resources/{self.port.parent_dir}/header/{self.port.header_landscape}',
                0, 0, self.port.page_height
            )
        self.ln(10)

    def footer(self):
        if self.page_no() != 1:
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(128)
            self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')


def add_cover(cover_txt_1, cover_txt_2, pdf, port):
    """
    `add_cover` adds a cover to the `pdf` instance with the provided texts and
    port.logo

    Parameters
    ----------
    cover_txt_1 : str
        first cover text.
    cover_txt_2 : str
        second cover text.
    pdf : MYPDF
        pdf instance.
    port.parent_dir : str
        port.parent_dir where the port.logo is located.
    port.logo : str
        port.logo image.

    Returns
    -------
    None.

    """

    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_y(pdf.eph/2)
    pdf.cell(w=0, h=None, txt=cover_txt_1, align='C')

    pdf.ln(30)
    pdf.set_font('Helvetica', 'b', 16)
    pdf.multi_cell(w=0, h=None, txt=cover_txt_2, align='C')

    pdf.ln(70)
    pdf.image(
        f'../../resources/{port.parent_dir}/logo/{port.logo}', w=pdf.epw)


def render_toc(pdf, outline):
    """
    `render_toc` renders the table of content to the `pdf` instance

    Parameters
    ----------
    pdf : MYPDF
        pdf instance.
    outline : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0)
    pdf.ln(5)
    pdf.cell(w=None, h=None, txt="Table of Contents")

    pdf.set_font('Helvetica', size=10)
    pdf.ln(10)

    for section in outline:
        link = pdf.add_link()
        pdf.set_link(link, page=section.page_number)

        # Generates the first part of the entry, which is the section name.
        # The entry is indented a multiple of 4 spaces, depending on the
        # level
        entry = f'{" " * section.level * 4}{section.name} '

        # Gets the width of the entry, which is the width of the section
        # name plus the width of the indentation, plus the width of the page
        # number
        entry_width = (
            pdf.get_string_width(entry)
        )
        entry_width = (
            entry_width +
            pdf.get_string_width(f'" "{section.page_number}')
        )

        # Append the necessary number of dots to the --entry--
        dot_width = pdf.get_string_width('.')
        dot_number = (pdf.epw - entry_width)/dot_width
        entry += (
            f'{"." * int(dot_number)}'
        )

        # Print --entry-- to the TOC
        pdf.cell(w=0, h=None, txt=entry, ln=0, align='L', link=link)

        # Print the page number
        entry = f' {section.page_number}'
        pdf.cell(w=0, h=None, txt=entry, ln=1, align='R', link=link)

        pdf.ln(3)


def add_page(path, resize_factor, pdf):
    """
    `add_page` adds a page of the given size to the `pdf` instance with an
    image located at `path`

    Parameters
    ----------
    path : str
        path to the image.
    resize_factor : float64
        value by which the image is resized.
    pdf : MYPDF
        pdf instance.

    Returns
    -------
    None.

    """

    try:
        image = Image.open(path)
        image_width, image_height = image.size

        # Convert px to mm considering 96 dpi
        image_width = image_width * CONV * resize_factor
        image_height = image_height * CONV * resize_factor

        if image_width >= min(pdf.eph, pdf.epw):
            pdf.add_page(orientation='L')
        else:
            pdf.add_page(orientation='P')

    except (AttributeError, FileNotFoundError):
        pdf.add_page(orientation='P')


# Add title to pdf page
def add_date(date, pdf):
    if date:
        today = time.strftime('%Y/%m/%d')

        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(r=128, g=128, b=128)
        pdf.cell(w=0, h=None, txt=f'{today}', align='R')


# Add subtitle
def add_subtitle(subtitle, pdf):
    if(subtitle != ''):
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(r=0, g=0, b=0)
        pdf.ln(4)
        pdf.write(5, subtitle)


# Add comment below title
def add_comment(comment, pdf):
    if(comment != ''):
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(r=0, g=0, b=0)
        pdf.ln(7)
        pdf.write(5, comment)


# Add image below comment (size in percentage)
def add_image(path, size, pdf):
    # Get the dimensions of the image
    image = Image.open(path)
    image_width, image_height = image.size

    # Convert px to mm considering 96 dpi
    image_width = image_width * CONV
    image_height = image_height * CONV

    # Add image with a fraction of its size. Because all images are resized
    # as a proportion of its size, the font size of all images are the same
    pdf.ln(10)
    pdf.image(path, w=size*image_width)


# Add title, subtitle, comment, and image
def add_standard_report(date, subtitle, comment, path, size, pdf):
    # add_date(date, pdf)
    add_subtitle(subtitle, pdf)
    add_comment(comment, pdf)
    add_image(path, size, pdf)


def set_style(pdf):
    """
    `set_style` sets the style of the pdf instance

    Parameters
    ----------
    pdf : MYPDF
        pdf instance.

    Returns
    -------
    None.

    """

    pdf.set_section_title_styles(

        # Level 0 titles:
        TitleStyle(
            font_family='Helvetica',
            font_style="B",
            font_size_pt=14,
            color=0,
            t_margin=5,
            l_margin=0
        ),

        # Level 1 subtitles:
        TitleStyle(
            font_family='Helvetica',
            font_style="B",
            font_size_pt=12,
            color=0,
            underline=False,
            t_margin=5,
            l_margin=0,
        ),

        # Level 2 subtitles:
        TitleStyle(
            font_family='Helvetica',
            font_style="B",
            font_size_pt=10,
            color=0,
            underline=False,
            t_margin=5,
            l_margin=0,
        ),
    )


def run(port):

    pdf = MYPDF(port)

    # Add cover page
    add_page('', -1, pdf)
    add_cover(port.cover_title, port.cover_subtitle, pdf, port)

    # Add blank page after cover
    add_page('', -1, pdf)

    # Add TOC
    add_page('', -1, pdf)
    pdf.insert_toc_placeholder(render_toc, pages=1)

    # Add Current Portfolio
    add_page(
        f'../../resources/{port.parent_dir}/graph/cumulative_amount.png',
        RESIZE_GRAPH,
        pdf)
    pdf.start_section('1. Current Portfolio', level=0)

    # Add Total Amount Invested
    pdf.start_section('1.1. Total Amount Invested', level=1)
    add_standard_report(
        False,
        'This table is composed of the total amount invested grouped by '
        'currency',
        '- Amount: total amount invested without considering dividends\n'
        '- Broker Fee: total amount paid in fees to the broker\n'
        '- Tax Fee: total amount paid in taxes\n'
        '- Total Fee: total amount paid in fees and taxes\n'
        '- Total Fee (%): percentage total fees',
        f'../../resources/{port.parent_dir}/table/total_invested.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/cumulative_amount.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Portfolio Composition
    add_page(
        f'../../resources/{port.parent_dir}/table/current_assets.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('1.2. Portfolio Composition', level=1)
    add_standard_report(
        True,
        'This table is composed of all assets grouped by '
        'type, industry, market, code, name, and currency.',
        '- QTY.: quantity\n'
        '- Avg. Rate: average exchange rate having KRW as reference\n'
        '- Avg. Price: average price\n'
        '- Close Price: previous close price\n'
        '- Amount: total amount based on the previous close price\n',
        f'../../resources/{port.parent_dir}/table/current_assets.png',
        RESIZE_TABLE,
        pdf
    )

    # Add Dividends
    add_page(
        f'../../resources/{port.parent_dir}/table/assets_dividend.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('1.3. Dividends', level=1)
    add_standard_report(
        True,
        'This table is composed of dividends for the last twelve '
        'months (LTM).',
        '- QTY.: quantity \n'
        '- Dividend: total dividend received \n'
        '- DPS: dividend per share \n'
        '- Total fee: includes broker fee and tax \n'
        '- Net DPS: dividend per share minus the total fee \n'
        '- Avg. Price: average price \n'
        '- Dividend Yield (%): net DPS divided by the average price',
        f'../../resources/{port.parent_dir}/table/assets_dividend.png',
        RESIZE_TABLE,
        pdf)

    # Add Breakdown
    add_page(
        f'../../resources/{port.parent_dir}/table/breakdown_current_assets.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('1.4. Capital Gain', level=1)
    add_standard_report(
        True,
        'This table is composed of the capital gain of all assets grouped by '
        'code, name, and currency for buy and dividend operations.',
        '- QTY.: quantity bought and received as dividend\n'
        '- Amount: amount bought and received as dividend\n'
        '- Avg. Price: average price paid for and received as dividend\n'
        '- Total Fee: total fee paid for buy and dividend operations\n'
        '- Avg. Rate: average exchange rate for buy and dividend operations\n'
        '- Current Rate: current exchange rate having KRW as reference\n'
        '- Current Amount: total amount based on the previous close price\n'
        '- Capital Gain: capital gain considering dividends, fee, and the '
        'exchange rate\n'
        '- Capital Gain (%): percentage capital gain\n',
        f'../../resources/{port.parent_dir}/table/breakdown_current_assets.png',
        RESIZE_TABLE,
        pdf
    )

    # Add Asset Allocation
    add_page(
        f'../../resources/{port.parent_dir}/table/allocation_name.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('1.5. Asset Allocation', level=1)

    # Add Allocation by Name
    pdf.start_section('1.5.1. Name', level=2)
    add_standard_report(
        True,
        'This table is composed of the asset allocation by name for the '
        'Current Assets grouped by currency.',
        '- QTY.: quantity\n'
        '- Amount: total amount based on the previous close prcice\n'
        '- Allocation (%): percentage asset allocation by name and grouped '
        'by currency',
        f'../../resources/{port.parent_dir}/table/allocation_name.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/allocation_name.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Allocation by Type
    add_page(
        f'../../resources/{port.parent_dir}/table/allocation_type.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('1.5.2. Type', level=2)
    add_standard_report(
        True,
        'This table is composed of the asset allocation by type for the '
        'Current Assets grouped by currency.',
        '- QTY.: quantity\n'
        '- Amount: total amount based on the previous close prcice\n'
        '- Allocation (%): percentage asset allocation by name and grouped '
        'by currency',
        f'../../resources/{port.parent_dir}/table/allocation_type.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/allocation_type.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Allocation by Industry
    add_page(
        f'../../resources/{port.parent_dir}/table/allocation_industry.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('1.5.3. Industry', level=2)
    add_standard_report(
        True,
        'This table is composed of the asset allocation by industry for the '
        'Current Assets grouped by currency.',
        '- QTY.: quantity\n'
        '- Amount: total amount based on the previous close prcice\n'
        '- Allocation (%): percentage asset allocation by industry and '
        'grouped by currency',
        f'../../resources/{port.parent_dir}/table/allocation_industry.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/allocation_industry.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Allocation by Market
    add_page(
        f'../../resources/{port.parent_dir}/table/allocation_market.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('1.5.4. Market', level=2)
    add_standard_report(
        True,
        'This table is composed of the asset allocation by market for the '
        'Current Assets grouped by currency.',
        '- QTY.: quantity\n'
        '- Amount: total amount based on the previous close prcice\n'
        '- Allocation (%): percentage asset allocation by market and grouped '
        'by currency',
        f'../../resources/{port.parent_dir}/table/allocation_market.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/allocation_market.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Technical Analysis
    add_page(
        f'../../resources/{port.parent_dir}/table/portfolio_beta.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('1.6. Technical Analysis', level=1)

    # Add Portfolio Beta
    pdf.start_section('1.6.1. Portfolio Beta', level=2)
    add_standard_report(
        True,
        'This table shows the Beta of each constituent asset in the Current '
        'Portfolio, as well as the Beta of thr portfolio as a whole.',
        '- QTY.: quantity\n'
        '- Amount: total amount based on the previous close price\n'
        '- Current Rate: exchange rate from the original currency to KRW\n'
        '- Allocation (%): percentage asset allocation by name\n'
        f'- Beta: beta having {port.benchmark[1]} ({port.benchmark[0]}) as '
        'benchmark\n'
        '- Weighted beta: beta weighted by the allocation',
        f'../../resources/{port.parent_dir}/table/portfolio_beta.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/beta_all.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Correlation Matrix
    add_page(
        f'../../resources/{port.parent_dir}/graph/correlation_matrix.png',
        RESIZE_GRAPH,
        pdf)
    pdf.start_section('1.6.2. Correlation Matrix', level=2)
    add_standard_report(
        True,
        'This figure shows the correlation between two aseets in the Current '
        'Portfolio',
        '',
        f'../../resources/{port.parent_dir}/graph/correlation_matrix.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Price History
    add_page(
        f'../../resources/{port.parent_dir}/graph/price_history.png',
        RESIZE_GRAPH,
        pdf)
    pdf.start_section('1.6.3. Price History', level=2)
    add_standard_report(
        True,
        'This figure shows the normalized price history of each constituent '
        'asset in the Current Portfolio.',
        '- Equal-weight portfolio: a theoretical portfolio in which each '
        'asset has the same weight\n'
        '- Current portfolio: the current portfolio with updated weights',
        f'../../resources/{port.parent_dir}/graph/price_history.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Monte Carlo Simulation
    add_page(
        f'../../resources/{port.parent_dir}/graph/monte_carlo.png',
        RESIZE_GRAPH,
        pdf)
    pdf.start_section('1.6.4. Monte Carlo Simulation', level=2)
    add_standard_report(
        True,
        'This table is composed of the statistical summary of the Monte Carlo '
        'simulation',
        f'- Number of simulations: {port.num_sim}\n'
        f'- Simulation period: {port.time_sim} days ({port.time_sim/260} years)',
        f'../../resources/{port.parent_dir}/table/monte_carlo.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/monte_carlo.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Efficient Frontier
    add_page(
        f'../../resources/{port.parent_dir}/graph/efficient_frontier.png',
        RESIZE_GRAPH,
        pdf)
    pdf.start_section('1.6.5. Efficient Frontier', level=2)
    add_standard_report(
        True,
        'This table is composed of the optimized asset allocation according '
        'to the Efficient Frontier theory.',
        '- Min. Volatility: optimized portfolio that generates the smallest '
        'annualized volatility\n'
        '- Min. Volatility (5%): optimized portfolio with at least 5% '
        'allocation that generates the smallest annualized volatility\n'
        '- Max. Sharpe Ratio: optimized portfolio that generates the maximum '
        'Sharpe Ratio\n'
        '- Max. Sharpe Ratio (5%): optimized portfolio with at least 5% '
        'allocation that generates the maximum Sharpe Ratio',
        f'../../resources/{port.parent_dir}/table/efficient_frontier.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/efficient_frontier.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Past Portfolio
    add_page(
        f'../../resources/{port.parent_dir}/table/past_assets.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('2. Past Portfolio', level=0)

    # Add Portfolio Composition
    pdf.start_section('2.1. Portfolio Composition', level=1)
    add_standard_report(
        True,
        'This table is composed of all past assets grouped by '
        'type, industry, market, code, name, and currency.',
        '- QTY.: quantity\n'
        '- Avg. Rate: average exchange rate having KRW as reference\n'
        '- Avg. Price: average price\n'
        '- Selling Price: selling price\n'
        '- Amount: total amount based on the selling price\n',
        f'../../resources/{port.parent_dir}/table/past_assets.png',
        RESIZE_TABLE,
        pdf
    )

    # Add Portfolio Composition
    add_page(
        f'../../resources/{port.parent_dir}/table/breakdown_past_assets.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('2.2. Capital Gain', level=1)
    add_standard_report(
        True,
        'This table is composed of the capital gain of all past assets '
        'grouped by code, name, and currency for buy, sell, and dividend '
        'operations.',
        '- QTY.: quantity bought, sold, and received as dividend\n'
        '- Amount: amount bought, sold, and received as dividend\n'
        '- Avg. Price: average price paid, sold, and received as dividend\n'
        '- Total Fee: total fee paid for buy, sell and dividend operations\n'
        '- Avg. Rate: average exchange rate for buy, sell, and dividend '
        'operations\n'
        '- Capital Gain: capital gain considering dividends, fee, and the '
        'exchange rate\n'
        '- Capital Gain (%): percentage capital gain\n',
        f'../../resources/{port.parent_dir}/table/breakdown_past_assets.png',
        RESIZE_TABLE,
        pdf
    )

    # Add Fees
    add_page(
        f'../../resources/{port.parent_dir}/graph/cumulative_fee.png',
        RESIZE_GRAPH,
        pdf)
    pdf.start_section('3. Fees', level=0)

    # Add Total Fees
    pdf.start_section('3.1. Total Fees', level=1)
    add_standard_report(
        False,
        'This table is compsed of the total amount of fees by currency',
        '- Amount: total amount invested including past assets and dividends\n'
        '- Broker Fee: total amount paid in fees to the broker\n'
        '- Tax Fee: total amount paid in taxes\n'
        '- Total Fee: total amount paid to the broker and in taxes\n'
        '- Total Fee (%): percentage total fees',
        f'../../resources/{port.parent_dir}/table/total_fee.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/cumulative_fee.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Fee
    add_page(
        f'../../resources/{port.parent_dir}/table/fee_name.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('3.2. Fee Allocation', level=1)

    # Add Fee by Name
    pdf.start_section('3.2.1. Name', level=2)
    add_standard_report(
        True,
        'This table is composed of the fee allocation by name for the '
        '*** grouped by currency.',
        '- Amount: total amount based on the ave. price and considering '
        'dividends\n'
        '- Broker Fee: total amount paid in fees to the broker\n'
        '- Tax Fee: total amount paid in taxes\n'
        '- Total Fee: total amount paid in fees and taxes\n'
        '- Total Fee (%): percentage total fees per currency',
        f'../../resources/{port.parent_dir}/table/fee_name.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/fee_name.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Fee by Type
    add_page(
        f'../../resources/{port.parent_dir}/table/fee_type.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('3.2.2. Type', level=2)
    add_standard_report(
        True,
        'This table is composed of the fee allocation by type for the '
        '*** grouped by currency.',
        '- Amount: total amount based on the ave. price and considering '
        'dividends\n'
        '- Broker Fee: total amount paid in fees to the broker\n'
        '- Tax Fee: total amount paid in taxes\n'
        '- Total Fee: total amount paid in fees and taxes\n'
        '- Total Fee (%): percentage total fees per currency',
        f'../../resources/{port.parent_dir}/table/fee_type.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/fee_type.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Fee by Industry
    add_page(
        f'../../resources/{port.parent_dir}/table/fee_industry.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('3.2.3. Industry', level=2)
    add_standard_report(
        True,
        'This table is composed of the fee allocation by industry for the '
        '*** grouped by currency.',
        '- Amount: total amount based on the ave. price and considering '
        'dividends\n'
        '- Broker Fee: total amount paid in fees to the broker\n'
        '- Tax Fee: total amount paid in taxes\n'
        '- Total Fee: total amount paid in fees and taxes\n'
        '- Total Fee (%): percentage total fees per currency',
        f'../../resources/{port.parent_dir}/table/fee_industry.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/fee_industry.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add Fee by Market
    add_page(
        f'../../resources/{port.parent_dir}/table/fee_market.png',
        RESIZE_TABLE,
        pdf)
    pdf.start_section('3.2.4. Market', level=2)
    add_standard_report(
        True,
        'This table is composed of the fee allocation by market for the '
        '*** grouped by currency.',
        '- Amount: total amount based on the ave. price and considering '
        'dividends\n'
        '- Broker Fee: total amount paid in fees to the broker\n'
        '- Tax Fee: total amount paid in taxes\n'
        '- Total Fee: total amount paid in fees and taxes\n'
        '- Total Fee (%): percentage total fees per currency',
        f'../../resources/{port.parent_dir}/table/fee_market.png',
        RESIZE_TABLE,
        pdf
    )
    add_standard_report(
        False,
        '',
        '',
        f'../../resources/{port.parent_dir}/graph/fee_market.png',
        RESIZE_GRAPH,
        pdf
    )

    # Add blank page
    pdf.add_page()

    # Save the pdf file
    pdf.output(
        f"../../resources/{port.parent_dir}/{port.output_file}_{dt.today().date().strftime('%Y-%m')}.pdf"
    )
