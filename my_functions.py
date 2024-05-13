import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import pandas as pd
import os


async def parse_exchange_rate_and_store(context) -> None:
    """This function parses exchange rate of USD-UAH and stores the value in relative database."""

    # Fetch HTML content from the website
    url = 'https://www.google.com/finance/quote/USD-UAH'
    response = requests.get(url)
    html_content = response.text

    # Find the element containing the exchange rate
    soup = BeautifulSoup(html_content, 'html.parser')
    div_element = soup.find('div', {'data-source': 'USD', 'data-target': 'UAH'})
    if not div_element:
        print("Div element with data-source='USD' and data-target='UAH' not found.")
        return

    # Find the span element within this div
    span_element = div_element.find('span')
    if not span_element:
        print("Span element not found within the div.")
        return

    # Extract the exchange rate value
    exchange_rate = span_element.get_text(strip=True)

    # Get the current date and time
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Connect to SQLite database
    conn = sqlite3.connect('exchange_rate.db')
    cursor = conn.cursor()

    # Store values
    cursor.execute('''CREATE TABLE IF NOT EXISTS exchange_rates (time TEXT PRIMARY KEY,rate REAL)''')
    cursor.execute("INSERT INTO exchange_rates (time, rate) VALUES (?, ?)", (current_time, exchange_rate))
    conn.commit()
    conn.close()


def create_excel_file() -> None:
    """This function creates .xlsx file with data from exchange_rate table in SQLite."""

    # Get the current date
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Create connection to SQLite database
    conn = sqlite3.connect('exchange_rate.db')
    df = pd.read_sql_query(f"SELECT * FROM exchange_rates WHERE time LIKE '{current_date}%'", conn)
    conn.close()

    # Check if the file exists and delete it if it does
    if os.path.exists(r'USD-UAH exchange rates.xlsx'):
        os.remove(r'USD-UAH exchange rates.xlsx')

    # Write data to Excel file with column names
    df.to_excel('USD-UAH exchange rates.xlsx', index=False, header=True)
