# -*- coding: utf-8 -*-

# -- Sheet --

import smtplib
import pandas as pd
from yahoo_fin import stock_info as si
from datetime import datetime, timedelta
import os
import mysql.connector
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def get_stock_prices(stocks, days):
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=days)

    # Create an empty dataframe to store the stock prices
    stock_prices = pd.DataFrame()

    # Loop through the list of stocks and retrieve their historical prices
    for ticker in stocks:
        stock_data = si.get_data(ticker, start_date=start_date, end_date=end_date)
        stock_prices[ticker] = round(stock_data["close"], 2)

    # Set the formatter to add '|' around each cell
    formatter = lambda x: f'| {x:10.2f} '

    # Convert the DataFrame to a string with formatted cells
    stock_prices_str = stock_prices.to_string(index=True, header=True, formatters={col: formatter for col in stock_prices.columns})
    
    # Add the stock prices to the MySQL database
    cnx = mysql.connector.connect(
        host=os.environ['MYSQL_HOST'],
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        database=os.environ['MYSQL_DB']
    )
    cursor = cnx.cursor()
    for symbol in stock_prices.columns:
        for i, row in stock_prices.iterrows():
            date = i.date()
            open_price = row[symbol]
            high_price = row[symbol]
            low_price = row[symbol]
            close_price = row[symbol]
            adj_close_price = row[symbol]
            volume = 0
            query = "INSERT INTO stock_data (Date, Open, High, Low, Close, Adj_Close, Volume, Symbol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (date, open_price, high_price, low_price, close_price, adj_close_price, volume, symbol)
            cursor.execute(query, values)
    cnx.commit()
    cursor.close()
    cnx.close()
    
    return stock_prices_str


def send_email(recipient, subject, body):
    # Define the sender and recipient email addresses
    sender = os.environ["email"]  
    # Create the message
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    body = body
    msg.attach(MIMEText(body, 'plain'))

    # Log in to the Gmail SMTP server
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    smtp_username = os.environ["email"]
    smtp_password = os.environ["password"]


    smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
    smtp_connection.starttls()
    smtp_connection.login(smtp_username, smtp_password)

    # Send the email
    smtp_connection.sendmail(sender, recipient, msg.as_string())

    # Close the connection
    smtp_connection.quit()

blue_chips = ["AAPL", "MSFT", "AMZN", "META", "GOOGL", "JPM"]
days = 5

stock_prices = get_stock_prices(blue_chips, days)
print(stock_prices)

send_email(os.environ["email"],"Stock Prices",stock_prices)

