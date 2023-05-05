import yfinance as yf
import sqlite3
import configparser

# Load configuration
conf = configparser.ConfigParser()
conf.read('config.ini')
companies = []


for key in conf['COMPANIES']:
    companies.append(conf['COMPANIES'][key])

# dB connection
con = sqlite3.connect('finance.db')
c = con.cursor()

# Create table if not exist
c.execute('''CREATE TABLE IF NOT EXISTS finance_data(company TEXT, date TEXT, open REAL, high REAL, low REAL, 
close REAL, volume INTEGER)''')

# iterate through companies and download data
for company in companies:
    ticker = yf.Ticker(company)
    data = ticker.history(period='max')
    for index, row in data.iterrows():
        c.execute("INSERT OR REPLACE INTO finance_data VALUES (?, ?, ?, ?, ?, ?, ?)",(company, str(index.date()), row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))

# Commit and close the connection
con.commit()
con.close()
print("Download code successfull")


from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__, template_folder='template')

# Define SQLite database connection
con = sqlite3.connect('finance.db', check_same_thread=False)
cur = con.cursor()

# route of the web page for resources
@app.route('/')
def index():
    # Render the HTML template for the web page
    return render_template('Finance_Data.html')



# Get all companies' stock data for a particular day
@app.route('/all_stock_data_for_date', methods=['GET'])
def get_all_stock_data_for_date():
    date = request.args.get('date')
    cur.execute(f"SELECT * FROM finance_data WHERE date='{date}'")
    rows = cur.fetchall()
    return render_template('Data_Show.html', rows=rows)

# Get all stock data for a particular company for a particular day
@app.route('/stock_data_for_company_and_date', methods=['GET'])
def get_stock_data_for_company_and_date():
    company = request.args.get('company')
    date = request.args.get('date')
    cur.execute(f"SELECT * FROM finance_data WHERE company='{company}' AND date='{date}'")
    rows = cur.fetchall()
    return render_template('Data_Show.html', rows=rows)

# Get all stock data for a particular company
@app.route('/stock_data_for_company', methods=['GET'])
def get_stock_data_for_company():
    company = request.args.get('company')
    cur.execute(f"SELECT * FROM finance_data WHERE company='{company}'")
    rows = cur.fetchall()
    return render_template('Data_Show.html', rows=rows)

# Update stock data for a company by date
@app.route('/update_stock_data_for_company_by_date', methods=['POST', 'PATCH'])
def update_stock_data_for_company_by_date():
    company = request.form.get("company")
    date = request.form.get("date")
    open_price = request.form.get("open")
    high_price = request.form.get("high")
    low_price = request.form.get("low")
    close_price = request.form.get('close')

    volume = request.form.get("volume")
    cur.execute(f"UPDATE finance_data SET open={open_price}, high={high_price}, low={low_price}, close={close_price}, volume={volume} WHERE company='{company}' AND date='{date}'")
    con.commit()
    return "Data updated successfully!!!!"

# Define the main function to run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=9999)

