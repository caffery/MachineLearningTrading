"""MC2-P1: Market simulator."""

import pandas as pd
import os

from util import get_data, plot_data
from portfolio.analysis import get_portfolio_value, get_portfolio_stats, plot_normalized_data

def compute_portvals(start_date, end_date, orders_file, start_val):
    """Compute daily portfolio value given a sequence of orders in a CSV file.

    Parameters
    ----------
        start_date: first date to track
        end_date: last date to track
        orders_file: CSV file to read orders from
        start_val: total starting cash available

    Returns
    -------
        portvals: portfolio value for each trading day from start_date to end_date (inclusive)
    """
    
    #Read order file
    orders = pd.read_csv( orders_file, parse_dates = [0])
    
    #Get symbols making up the portfolio
    stock_symbols = list( set( orders["Symbol"] ) )
    dates =  pd.date_range(start_date, end_date)
    
    #Read stock prices
    stock_prices = get_data(stock_symbols, dates)
    
    #Create a portfolio keeping track of positions, 
    #_CASH column indicates cash position,  _VALUE total portfolio value
    #_LEVERAGE the leverage of portfolio when we allow for short selling
    symbols = stock_symbols[:] #Shallow copy of the list
    symbols.append("_CASH")
    symbols.append("_VALUE")
    symbols.append("_LEVERAGE")
    
    #Index contains only business days, same dates as stock prices
    portfolio = pd.DataFrame(index=stock_prices.index, columns = symbols )
    portfolio.fillna(0) 
    portfolio["_CASH"][0]  = start_val
    portfolio["_VALUE"][0]  = start_val
    
    #Snapshot of a portfolio at any time. To avoid using numerical indexes
    portfolio_snapshot = dict.fromkeys ( symbols, 0 )
    portfolio_snapshot["_CASH"] = start_val
    portfolio["_VALUE"] = start_val
    
    #Now calcualte portfolio day by day
    for date in portfolio.index:
        #Check transactions for the day
        day_orders = orders[ orders["Date"] == date ] 
            
        for ord in day_orders.iterrows():
            symbol = ord[1][ "Symbol"]            
            stock_price = stock_prices[ symbol ][ date ]
            shares = ord[1]["Shares" ]
            side = ord[1]["Order"]
            
            if side == "BUY":
                portfolio_snapshot[ "_CASH" ] -= stock_price * shares
                portfolio_snapshot[ symbol ] += shares           
            elif side == "SELL":
                portfolio_snapshot[ "_CASH" ] += stock_price * shares
                portfolio_snapshot[ symbol ] -= shares
            else:
                raise "Order not recognized."
        
        #Compute portfolio value
        portfolio_snapshot[ "_VALUE" ] = portfolio_snapshot[ "_CASH" ]
        shorts = longs = 0
        for symbol in stock_symbols:      
            stock_price = stock_prices[ symbol ][ date ]
            shares = portfolio_snapshot[ symbol ]
            notional = stock_price*shares
            if shares > 0:
                longs += notional
            else:
                shorts += notional
                
            portfolio_snapshot[ "_VALUE" ] += notional
        
        #Compute leverage
        leverage = (longs+shorts)/(longs-shorts + portfolio_snapshot[ "_CASH" ] )
        portfolio_snapshot[ "_LEVERAGE" ] = leverage
        
        #Assert we never achieve a leverage > 2.0
        if leverage > 2:
            raise "Leverage > 2.0 achieved"
                    
        #Update portfolio from the daily snapshot
        #TODO: Is this causing performance issues?
        for symbol in portfolio.keys():
            portfolio[ symbol ][ date ] = portfolio_snapshot[ symbol ]
        
    return portfolio


def test_run():
    """Driver function."""
    # Define input parameters
    start_date = '2011-01-05'
    end_date = '2011-01-20'
    #orders files: orders2.csv  orders.csv  orders-short.csv
    orders_file = os.path.join("orders", "orders.csv")
    start_val = 1000000

    # Process orders
    portvals = compute_portvals(start_date, end_date, orders_file, start_val)
    portvals = portvals[ "_VALUE" ]
    #if isinstance(portvals, pd.DataFrame):
    #    portvals = portvals[portvals.columns[0]]  # if a DataFrame is returned select the first column to get a Series
       
    # Get portfolio stats
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = get_portfolio_stats(portvals)

    # Simulate a $SPX-only reference portfolio to get stats
    prices_SPX = get_data(['^GSPC'], pd.date_range(start_date, end_date))
    prices_SPX = prices_SPX[['^GSPC']]  # remove SPY
    portvals_SPX = get_portfolio_value(prices_SPX, [1.0])
    cum_ret_SPX, avg_daily_ret_SPX, std_daily_ret_SPX, sharpe_ratio_SPX = get_portfolio_stats(portvals_SPX)

    # Compare portfolio against $SPX
    print "Data Range: {} to {}".format(start_date, end_date)
    print
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Sharpe Ratio of $SPX: {}".format(sharpe_ratio_SPX)
    print
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Cumulative Return of $SPX: {}".format(cum_ret_SPX)
    print
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Standard Deviation of $SPX: {}".format(std_daily_ret_SPX)
    print
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Average Daily Return of $SPX: {}".format(avg_daily_ret_SPX)
    print
    print "Final Portfolio Value: {}".format(portvals[-1])

    # Plot computed daily portfolio value
    df_temp = pd.concat([portvals, prices_SPX['^GSPC']], keys=['Portfolio', '^GSPC'], axis=1)
    plot_normalized_data(df_temp, title="Daily portfolio value and $SPX")


if __name__ == "__main__":
    test_run()
