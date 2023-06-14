# financial-report

**financial-report** analyzes your investment transactions (buy/sell operations and dividends received) and compiles them into a neat financial report! At the end of each month you will receive the report directly to your email, so you can track your investment progress and make better, educated decisions.

The summary items are:

1. Current Portfolio
    1. Total Amount Invested
    2. Portfolio Composition
    3. Dividends
    4. Capital Gain
    5. Asset Allocation
        1. Name
        2. Type
        3. Industry
        4. Market
    6. Technical Analysis
        1. Portfolio Beta
        2. Correlation Matrix
        3. Price History
        4. Efficient Frontier
2. Past Portfolio
    1. Portfolio Composition
    2. Capital Gain
3. Fees
    1. Total Fees
    2. Fee Allocation
        1. Name
        2. Type Industry
        3. Market     


## Input

The input file is a `.xlsx` file populated with the transactions history of the portfolio. The following fields should be entered when a transation is recorded:

>**IMPORTANT:** Keep this file updated for an accurate analyzes.

![image](https://user-images.githubusercontent.com/59410219/155932911-a04481b6-465e-4950-a39e-1a9096ac9751.png)

1. Date (YYYY-MM-DD): transaction date in the year-month-day format
2. Time (HH:MM): transaction time in the hour:minute format
3. Type : stock ou ETF
4. Industry: industry in which the security operates (North American Industry Classification System (NAICS) https://www.naics.com/search/)
5. Market: market in which the security operates
6. Code: code or ticker that identifies the security
7. Code 2: backup code or ticker that identifies the security
8. Name: name of the security
9. Operation: buy, sell, or dividend
10. QTY.: quantity bought, sold, or received as dividend
11. Currency: currency in which the transaction was made
12. Unit Price: unit price of the transaction
13. Amount: total amount of the transaction without fees
14. Broker Fee: broker fee charged for the transaction
15. Tax Fee: tax fee charged for the transaction
16. Exchange Rate: exchange rate used in the transaction having KRW as reference

**financial-report** will automatically download the input file from Google Drive, provided access has been granted and the document ID is available.

To alow access to the input file go to your Google Drive page, click the `Share` and choose `Anyone with the link`. Aditionally, you can set the role to `Viewer` to ensure that the file is protected against write operations.
<img src="https://github.com/wagnojunior/financial-report/assets/59410219/2066d9e3-bda2-4f48-be4a-ad165966c4fd" width="500" />


To check the document ID open the file you just shared and refer to the its URL; the document ID is located there.
<img src="https://github.com/wagnojunior/financial-report/assets/59410219/bcde15da-d3f7-446c-a57b-b2fcafeadb0c" width="500" />


Now, populate the `.env` file with the appropriete information, like below:
```
# SMPT server API token
api_token="ENTER_YOUR_API_TOKEN_HERE"

# Google docs ID and URL
doc_id="ENTER_YOUR_DOC_ID_HERE"
doc_url="https://drive.google.com/uc?id=${doc_id}"
```

## Output

The output file is a `.pdf` report with a summary of the investment portfolio. 

![image](https://user-images.githubusercontent.com/59410219/155928274-211c6cf1-5871-43ec-87d8-071d04b3047e.png)

1. Cover page

![image](https://user-images.githubusercontent.com/59410219/155928611-5102bc8b-b3d5-4671-b86a-c40e8ce6648b.png)

2. Table of Contents

![image](https://user-images.githubusercontent.com/59410219/155932669-b407fda4-f81b-41ef-b7e1-7e080053f539.png)


## File system

The source code creates the necessary folders inside the `resources` directory in case they are not present. Each parent directory (e.g.: `parent_directory_1`, `parent_directory_2`) represents a portfolio, and the directory\`s name is regarded as the portfolio\`s name. The folders `header` and `logo` should be populated with the customized header (portrait and landscape) and logo for each portfolio, respectively. The folder `other` can be used for any other files, such as `.svg` source file of the header and logo. The remaining folders are populated automatically with graphs, tables, price history, and exchange rate. There is no limit to the number of portfolios.

```python
financial-report
├───src
│   └───financial_report
│       └───[folders omitted for brevity]
├───resources
│   ├───parent_directory_1
│   │   ├───graph
│   │   │   └───[graphs are saved here]
│   │   ├───header
│   │   │   └───[header is saved here]
│   │   ├───logo
│   │   │   └───[logo is saved here]
│   │   ├───other
│   │   │   └───[other files are saved here]
│   │   ├───price
│   │   │   └───[price data are saved here]
│   │   ├───rate
│   │   │   └───[currency rate data are saved here]
│   │   ├───table
│   │   │   └───[tables are saved here]
│   │   ├───buy_sell_dividend_log_1.xlsx
│   │   ├───financial_report_1.pdf
│   │   └───.config.template
│   │
│   ├───parent_directory_2
│   │   ├───[graph, header, logo, other, price, rate, table]
│   │   ├───buy_sell_dividend_log_2.xlsx
│   │   ├───financial_report_2.pdf
│   │   └───.config.template
```

## Configuration file

A template configuration file `.config.template` is created in case it is not present inside the `parent_directory` folder. In this file it is possible to customize many things related to the financial report, technical analysis, and report distribution through email. Each portfolio shoudl have its own configuration file.

>**IMPORTANT:** Rename the configuration file from `.config.template` to `.config`.

```python{line_numbers}
{
    "users": [
        {
            "email": "dummy_1@dummy.com",
            "name": "Dummy Name 1"
        },
        {
            "email": "dummy_2@dummy.com",
            "name": "Dummy Name 2"
        }
    ],
    "input_file": "dummy transaction.xlsx",
    "output_file": "Financial Report Dummy",
    "parent_dir": "dummy portfolio",
    "page_width": 210,
    "page_height": 297,
    "cover_title": "DUMMY FINANCIAL REPORT",
    "cover_subtitle": "Dummy Company\nA subsidiary of Dummy Corp.",
    "header_landscape": "header_landscape.png",
    "header_portrait": "header_portrait.png",
    "logo": "logo.png",
    "benchmark": [
        "^GSPC",
        "S&P500"
    ],
    "day_shift": -1,
    "period": [
        "2015-01-01",
        "2023-05-22"
    ],
    "num_sim": 500,
    "time_sim": 1300,
    "risk_free": 0.0021
}
```

The configuration file can be divided into four sections:

1. User: list of users to whom the `financial_report.pdf` file is sent. There is no limit to the number of users, though the SMTP server might have some limitation.
    1. User email address: email address of the user
    2. User name: name of the user

2. Portfolio name and data: 
    1. Input file name: `.xlsx` file populated with the transactions history
    2. Output file name: `.pdf` report with a summary of the investment portfolio.
    3. Parent directory: name of the portfolio

3. Report: style and customizations
    1. Page widht and height: use default values for A4 size
    2. Cover title: title shown on the cover page
    3. Cover subtitle 1 and 2: subtitles shown on the cover page
    4. Header on landscape and portrait orientations: header shown on every page. Make sure to distinguish between *landscape* and *portrait* by properly naming the files `###_landscape.png` and `###_portrait`, respectively
    5. Logo: logo shown on the cover page and on the email HTML content (can be customized by editing the source code)

4. Technical analysis
    1. Benchmark: asset that serves as baseline for comparison (e.g.: S&P500)
    2. Day shift: useful when comparing assets from markets that operate on very different timezones (e.g.: NYE S&P500 and KOSPI). -1: advance the stock (not the benchmark) by one day; 0: does not shift the stock; +1: delay the stock (not the benchmark) by one day
    3. Period: period over which the historical data is analysed (e.g.: 5 years)
    4. Number of simulations: number of Monte Carlo simulation (e.g.: 500)
    5. Time of simulation: time in days of Monte Carlo simulation (e.g.: 1Y=260D)
