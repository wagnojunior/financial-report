import datetime as dt
import json

from utils import file_system as fs


class Portfolio():
    def __init__(self, users, input_file, output_file, parent_dir, page_width,
                 page_height, cover_title, cover_subtitle, header_landscape,
                 header_portrait, logo, benchmark, day_shift, period, num_sim,
                 time_sim, risk_free):
        self.users = users
        self.input_file = input_file
        self.output_file = output_file
        self.parent_dir = parent_dir
        self.page_width = page_width
        self.page_height = page_height
        self.cover_title = cover_title
        self.cover_subtitle = cover_subtitle
        self.header_landscape = header_landscape
        self.header_portrait = header_portrait
        self.logo = logo
        self.benchmark = benchmark
        self.day_shift = day_shift
        self.period = period
        self.num_sim = num_sim
        self.time_sim = time_sim
        self.risk_free = risk_free

    def to_dict(self):
        return {
            "users": self.users,
            "input_file": self.input_file,
            "output_file": self.output_file,
            "parent_dir": self.parent_dir,
            "page_width": self.page_width,
            "page_height": self.page_height,
            "cover_title": self.cover_title,
            "cover_subtitle": self.cover_subtitle,
            "header_landscape": self.header_landscape,
            "header_portrait": self.header_portrait,
            "logo": self.logo,
            "benchmark": self.benchmark,
            "day_shift": self.day_shift,
            "period": self.period,
            "num_sim": self.num_sim,
            "time_sim": self.time_sim,
            "risk_free": self.risk_free
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, data):
        return cls(
            users=data["users"],
            input_file=data["input_file"],
            output_file=data["output_file"],
            parent_dir=data["parent_dir"],
            page_width=data["page_width"],
            page_height=data["page_height"],
            cover_title=data["cover_title"],
            cover_subtitle=data["cover_subtitle"],
            header_landscape=data["header_landscape"],
            header_portrait=data["header_portrait"],
            logo=data["logo"],
            benchmark=data["benchmark"],
            day_shift=data["day_shift"],
            period=data["period"],
            num_sim=data["num_sim"],
            time_sim=data["time_sim"],
            risk_free=data["risk_free"]
        )

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls.from_dict(data)


def export(port_dir):
    """
    `export` exports a dummy congifuration file in the given directory. Note
    that the configuration file `.config` may be hidden.

    Attributes
    ----------
    users : list
        Email and Name of the users who own this portfolio.
    input_file : str
        Name of the excel file where all the transactions are saved.
    output_file : str
        Name of the output report file.
    parent_dir : str
        Name of the folder inside `resources` where the data is saved.
    page_width : int
        Width of the report file.
    page_height : int
        Height of the report file.
    cover_title : str
        Title of the report file.
    cover_subtitle : str
        Subtitle of the report file.
    header_landscape : str
        Name of the header image for landscape orientation.
    header_portrait : str
        Name of the header image for portrait orientation.
    logo : str
        Name of the logo image for the report file.
    benchmark : list of str
        Benchmark stock [`Ticker`, `Name`].
    day_shift : int
        Day shift applied during technical analysis. Useful when comparing
        stocks from different markets (e.g.: NYE S&P500 and KOSPI).
        -1: advance the stock (not the benchmark) by one day
        (e.g.:
         S&P500: 01/03, 02/03, 03/03, ...,
         KOSPI:  02/03, 03/03, 04/03, ...)
        0: does not shift the stock
        +1: delay the stock (not the benchmark) by one day
        (e.g.:
         S&P500: 01/03, 02/03, 03/03, ...,
         KOSPI:  28/02, 01/03, 02/03, ...).
    period : list of datetime
        Time period used in the Price History analysis.
    num_sim : int
        Number of simulations used in the Monte Carlo analysis.
    time_sim : int
        Time, in days, used in the Monte Carlo analysis.
    risk_free : float64
        Risk free rate used in the Efficient Frontier analysis

    Parameters
    ----------
    port_dir : str
        Folder name that defines a portfolio.

    Returns
    -------
    None.

    """

    users = [
        {'email': 'dummy_1@dummy.com', 'name': 'Dummy Name 1'},
        {'email': 'dummy_2@dummy.com', 'name': 'Dummy Name 2'}
    ]
    input_file = 'dummy transaction.xlsx'
    output_file = 'Financial Report Dummy'
    parent_dir = 'dummy portfolio'
    page_width = 210
    page_height = 297
    cover_title = "DUMMY FINANCIAL REPORT"
    cover_subtitle = "Dummy Company\n" + "A subsidiary of Dummy Corp."
    header_landscape = 'header_landscape.png'
    header_portrait = 'header_portrait.png'
    logo = 'logo.png'

    # Technical analysis
    # [CODE, NAME]
    benchmark = ['^GSPC', 'S&P500']
    # -1:shift upwards | 0:does not shift | +1:shift downwards
    day_shift = -1
    # [start, finish]
    period = [dt.datetime(2015, 1, 1).date().isoformat(),
              dt.datetime.today().date().isoformat()]
    # number of Monte Carlo simulations
    num_sim = 500
    # time in days of Monte Carlo simulation (1Y=260D)
    time_sim = 1300
    # risk free rate
    risk_free = 0.0021

    port = Portfolio(users, input_file, output_file, parent_dir, page_width,
                     page_height, cover_title, cover_subtitle,
                     header_landscape, header_portrait, logo, benchmark,
                     day_shift, period, num_sim, time_sim, risk_free).to_json()

    fs.save_config(port_dir, port)


def importt(port_dir):
    """
    `import` imports a configuration file from the given directory, and returns
    a Portfolio instance.

    Parameters
    ----------
    port_dir : str
        Name of the folder where the portfolio data is saved.

    Returns
    -------
    Portfolio
        Portfolio instance corresponding to the loaded configuration file.

    """

    data = fs.load_config(port_dir)
    return Portfolio.from_dict(data)
