"""
`file_system` handles the creation of the required file system.

working_directory
├───src
│   └───financial_report
│       └───[folders omitted for brevity]
├───resources
│   └───parent_directory
│       ├───graph
│       │   └───[graphs are saved here]
│       ├───header
│       │   └───[header is saved here]
│       ├───logo
│       │   └───[logo is saved here]
│       ├───other
│       │   └───[other files are saved here]
│       ├───price
│       │   └───[price data are saved here]
│       ├───rate
│       │   └───[currency rate data are saved here]
│       ├───table
│       │   └───[tables are saved here]
│       ├───buy_sell_dividend_log.xlsx
│       └───financial_report.pdf
"""

import json
import os
import shutil
from pathlib import Path

import gdown
from dotenv import load_dotenv
from portfolio import portfolio
from requests.exceptions import RequestException


def create(parent_directory):
    """
    `create` creates a parent directory and the necessary file system inside of
    it

    Parameters
    ----------
    parent_directory : str
        name of the parent directory.

    Returns
    -------
    None.

    """
    Path(f'../../resources/{parent_directory}').mkdir(parents=True,
                                                      exist_ok=True)

    file_system = [
        'graph', 'header', 'logo', 'other', 'price', 'rate', 'table'
    ]

    for folder in file_system:
        (
            Path(f'../../resources/{parent_directory}/{folder}')
            .mkdir(parents=True, exist_ok=True)
        )


def download_rawData(port):
    """
    `download_rawData` downloads the input file from Google Drive, provided the
    sharable link is available and the access is granted

    Parameters
    ----------
    port : Portfolio
        Instance of the class Portfolio.

    Raises
    ------
    FileNotFoundError
        Raises exception when the input file can not be downloaded from Google
        Drive AND an older version of the file is not present in the given
        directory.

    Returns
    -------
    None.

    """

    # Load environmental variables
    load_dotenv(dotenv_path=f'../../resources/{port.parent_dir}/.env',
                override=True)
    url = os.environ.get("doc_url")

    # Download
    output_dir = f'../../resources/{port.parent_dir}/{port.input_file}'
    try:
        gdown.download(url, output_dir, quiet=False)
    except (ValueError, RequestException):
        msg = (
            "Could not download the `buy_sell_dividend_log.xlsx` from the "
            "specified Google Drive. There are two possible reasons: 1) the "
            "environment variables were not set properly, or 2) the "
            "configuration file was not set correclty. Please check the "
            "`.env` and `.config` and try again. ")

        if os.path.isfile(f'../../resources/{port.parent_dir}/{port.input_file}'):
            extra_msg = (
                f"It will proceed with the file `{port.input_file}` located "
                f"at the `{port.parent_dir}` folder."
            )
            print(msg + extra_msg)
        else:
            extra_msg = (
                f"It will abort since the input file `{port.input_file}` was "
                f"not located at the `{port.parent_dir}` folder."
            )
            print(msg + extra_msg)
            raise FileNotFoundError('Missing input file.')


def get_portfolios():
    """
    `get_portfolios` returns a list of portfolios.

    Returns
    -------
    list
        List of folders inside the `resources` directory.

    """

    portfolios = next(os.walk('../../resources'))[1]
    return portfolios


def save_config(port_dir, data):
    """
    `save_config` saves a config file

    Parameters
    ----------
    port_dir : str
        path to the portfolio folder.
    data : str
        JSON string of the portfolio configuration file.

    Returns
    -------
    None.

    """

    with open(f'../../resources/{port_dir}/.config.template', 'w') as f:
        f.write(data)


def load_config(port_dir):
    """
    `load_config` loads the configuration file located at the given directory.
    In case the configuration file does not exist, a template file is created
    instead, so the user con configure it.

    Parameters
    ----------
    port_dir : str
        Portfolio folder inside `resources` (e.g.: `dummy portfolio`).

    Raises
    ------
    FileNotFoundError
        A FileNotFoundError is raised in case the configuration file is not
        present.

    Returns
    -------
    data : dict
        Dictionary representation of the configuration file.

    """

    try:
        with open(f'../../resources/{port_dir}/.config', 'r') as f:
            data = json.load(f)

        return data

    except FileNotFoundError:
        portfolio.export(port_dir)
        msg = (
            'There is no configuration file for this portfolio, so a template '
            'configuration file was created. Please, fill in the `.config` '
            'file and try again.'
        )
        print(msg)
        raise FileNotFoundError('Missing configuration file.')


def check_env(port_dir):
    """
    `check_env` checks if the environment variables file is present at the
    given directory. In case the environment variables file does not exist, a
    template file is created instead, so the user can configure it.

    Parameters
    ----------
    port_dir : str
        Portfolio folder inside `resources` (e.g.: `dummy portfolio`).

    Raises
    ------
    FileNotFoundError
        A FileNotFoundError is raised in case the configuration file is not
        present.

    Returns
    -------
    None.

    """

    if not os.path.exists(f'../../resources/{port_dir}/.env'):
        src = '../../.env.template'
        dst = f'../../resources/{port_dir}/.env.template'
        shutil.copy(src, dst)

        msg = (
            'There is no environment variable file for this portfolio, so a '
            'template environment variable file was created. Please, fill in '
            'the `.env` file and try again.')
        print(msg)

        raise FileNotFoundError('Missing environment variable file.')


def load_template():

    with open('./utils/template.html', 'r') as f:
        return f.read()


def set_workingDir(file):
    """
    `set_workingDir` changes the current working directory to the parent
    directory of the given file.

    Parameters
    ----------
    file : str
        File whose parent directory will be the working directory.

    Returns
    -------
    None.

    """

    working_dir = os.path.dirname(os.path.abspath(file))
    os.chdir(working_dir)
