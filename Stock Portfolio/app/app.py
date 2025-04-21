import sqlite3
import yfinance as yf
def get_current_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        return stock.info['regularMarketPrice']
    except:
        return None
from flask import Flask, render_template, request
from flask import request, redirect
from _collections import defaultdict
app = Flask(__name__)


@app.route('/')
def index():
    conn = sqlite3.connect('../portfolio.db')
    c = conn.cursor()
    c.execute('SELECT * FROM transactions ORDER BY date DESC')
    transactions = c.fetchall()

    #Group by symbol and calculate net shares + total invested
    c.execute('SELECT symbol, shares, price, type FROM transactions')
    all_tx = c.fetchall()
    conn.close()

    portfolio = defaultdict(lambda: {'shares': 0, 'invested': 0.0})

    for symbol, shares, price, type_ in all_tx:
        if type_ == 'buy':
            portfolio[symbol]['shares'] += shares
            portfolio[symbol]['invested'] += shares * price
        elif type_ == 'sell':
            portfolio[symbol]['shares'] -= shares
            portfolio[symbol]['invested'] -= shares * price
    #Fetch current prices and calculate value and P/L
    summary = []
    for symbol, data in portfolio.items():
        current_price = get_current_price(symbol)
        current_value = current_price * data['shares'] if current_price else 0.0
        gain_loss = current_value - data['invested']
        summary.append({'symbol': symbol,
                        'shares': data['shares'],
                        'invested': data['invested'],
                        'current_price': current_price,
                        'current_value': current_value,
                        'gain_loss': gain_loss
                        })
    return render_template('index.html', transactions=transactions, summary=summary)

@app.route('/add', methods=['POST'])
def add_transaction():
    symbol = request.form['symbol'].upper()
    shares = int(request.form['shares'])
    price = float(request.form['price'])
    type = request.form['type']

    if shares <= 0 or shares > 1000:
        print('Invalid share value', shares)
        return "Invalid Share Quantity", 400
    if price <= 0 or price > 1000:
        print('Invalid price value', price)
        return "Invalid Price", 400

    conn = sqlite3.connect('../portfolio.db')
    c = conn.cursor()
    c.execute('INSERT INTO transactions (symbol, shares,price, type) VALUES (?,?,?,?)',
              (symbol, shares, price, type))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/api/price')
def get_price_api():
    symbol = request.args.get('symbol', '').upper()
    price = get_current_price(symbol)
    if price:
        return {'price': round(price, 2)}
    return {'price': None}

if __name__ == '__main__':
    app.run(debug=True)