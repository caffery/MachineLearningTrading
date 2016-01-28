"""MLT - MC2 - P2 Bollinger Bands Strategy"""
import os
import pandas as pd
import matplotlib.pyplot as plt

from portfolio.analysis import get_portfolio_stats, get_portfolio_value, plot_normalized_data
from util import get_data
import marketsim

def bollinger_indicator(quotation_serie, window_length = 20, dev_factor=2):
    """Bollinger band indicator
    
    Return a dataframe containing the stock quotation as well as the moving
    average and the standard deviation (bollinger bands).
    
    Parameters
    ----------
        quotation_serie: Series with stock prices
        window_length: Number of samples for the moving average
        dev_factor: Number of standard deviation around the moving average
    
    Returns
    -------
        bollinger_indicator: data frame with the moving average and the 
        standard deviation band    
    """
    #Compute rolling mean and std    
    ma = pd.rolling_mean(quotation_serie, window = window_length)
    sd = pd.rolling_std(quotation_serie, window = window_length)
    
    #Create bollinger band
    bollinger_indicator = pd.DataFrame(index = quotation_serie.index, 
                                       columns = ["Price", "MA", "UpperBand", "LowerBand"] )
    
    bollinger_indicator["Price"] = quotation_serie    
    bollinger_indicator["MA"] = ma    
    bollinger_indicator["UpperBand"] = ma + sd *  dev_factor
    bollinger_indicator["LowerBand"] = ma - sd *  dev_factor    
    
    return bollinger_indicator
    
def bollinger_strategy( bollinger_df ):
    """Bollinger Band strategy
    
    Given a bollinger band indicator, generate the trading signals
    
    Parameters
    ----------
        bollinger_df: Bollinger indicator, as returned by bollinger_indicator
        function.
    
    Returns
    -------
        trading_signal: Time series with the trading signal. Signals can be
        of type Long entry, long, long exit, short entry, short, short exit, hold.
    
    """
    
    #Add a column with the trading signal
    signal = pd.Series(index=bollinger_df.index, dtype=str, name="TradingSignal")
    indicator = bollinger_df #Alias for bollinger data frame
    state = "HOLD"
    
    yesterday = bollinger_df.index[0]
    for date in bollinger_df.index[1:]:        
               
        #Transitions of the state machine
        if state == "HOLD":
            if (indicator["Price"][yesterday] > indicator["UpperBand"][yesterday] ) \
            and (indicator["Price"][date] <= indicator["UpperBand"][date] ):
                state = "SHORT_ENTRY"
            elif (indicator["Price"][yesterday] < indicator["LowerBand"][yesterday]) \
            and  (indicator["Price"][date] >= indicator["LowerBand"][date] ) :
                state = "LONG_ENTRY"
            else:
                state = "HOLD"
                    
        elif state == "LONG_ENTRY" or state == "LONG":
            if (indicator["Price"][date] >= indicator["MA"][date] ):
                state = "LONG_EXIT"  
            else:
                state = "LONG"

        elif state == "SHORT_ENTRY" or state == "SHORT":
            if (indicator["Price"][date] <= indicator["MA"][date] ):
                state = "SHORT_EXIT"
            else:
                state = "SHORT"
                
        elif state == "LONG_EXIT":
            if (indicator["Price"][yesterday] > indicator["UpperBand"][yesterday]) \
            and (indicator["Price"][date] <= indicator["UpperBand"][date] ):
                state = "SHORT_ENTRY"
            else:
                state = "HOLD"
                
        elif state == "SHORT_EXIT":
            if (indicator["Price"][yesterday] < indicator["LowerBand"][yesterday]) \
            and (indicator["Price"][date] >= indicator["LowerBand"][date] ):
                state = "LONG_ENTRY"
            else:
                state = "HOLD"
                
        else:
            raise "Unknown state"
            
        #Update trading state 
        signal[date] = state
        yesterday = date
    
    return signal
    
def generate_trades(stock, cash, bollinger_df, bollinger_strg):
    """Generate trading orders according to the bollinger strategy
    
    Parameters
    ----------
        bollinger_df: Bollinger indicator, as returned by bollinger_indicator
        function.
        bollinger_strg: Trading signal with the bollinger strategy
    
    Returns
    -------
        Dataframe with the trading orders of the strategy
    
    """    
    orders = pd.DataFrame(columns = ["Date","Symbol","Order","Shares"] )
    
    #For each date    
    quantity = 0.0 #number of stocks 
    for date in bollinger_strg.index:
        signal = bollinger_strg[date]

        #LONG ENTRY generates a buying signal        
        if signal == "LONG_ENTRY":
            quantity = int( float( cash ) / bollinger_df["Price"][date] )
            order = {'Date' : date, 'Symbol' : stock, 'Order' : "BUY", 'Shares' : quantity}
            orders = orders.append(order, ignore_index=True)
        #LONG_EXIT generates a sell signal of the same quantity of stock
        elif signal == "LONG_EXIT":
            order = {'Date' : date, 'Symbol' : stock, 'Order' : "SELL", 'Shares' : quantity}
            orders = orders.append(order, ignore_index=True)
        #SHORT_ENTRY generates a sell signal
        elif signal == "SHORT_ENTRY":
            quantity = int( float( cash ) / bollinger_df["Price"][date] )
            order = {'Date' : date, 'Symbol' : stock, 'Order' : "SELL", 'Shares' : quantity}
            orders = orders.append(order, ignore_index=True)
        #SHORT_EXIT generates a buy signal of the same quantity of stock
        elif signal == "SHORT_EXIT":
            order = {'Date' : date, 'Symbol' : stock, 'Order' : "BUY", 'Shares' : quantity}
            orders = orders.append(order, ignore_index=True)
        else:
            pass 
    
    return orders
    
    
def plot_bollinger_strategy( bollinger_df, bollinger_strg, outputfile="output/bollinger.png" ):
    """Plot of a bollinger strategy
    
    Given a bollinger band indicator, plot the stock price along with bollinger 
    bands and trading signals.
    
    Parameters
    ----------
        bollinger_df: Bollinger indicator, as returned by bollinger_indicator
        function.
        bollinger_strg: Trading signal with the bollinger strategy
        outputfile: output file name to save the plot in a file
    
    Returns
    -------
        None
    
    """    
    #Get trading signal dates
    long_entries = bollinger_strg[ bollinger_strg == "LONG_ENTRY" ] .index
    short_entries = bollinger_strg[ bollinger_strg == "SHORT_ENTRY" ] .index
    exits = bollinger_strg[ (bollinger_strg == "LONG_EXIT") | (bollinger_strg == "SHORT_EXIT")] .index
        
    #Plot bollinger bands
    plt.plot( bollinger_df.index.to_pydatetime(), bollinger_df )    
    plt.xlabel('Date')
    plt.ylabel('Prices')
    plt.title('Bollinger bands')
    plt.grid(b=True, which='both', color='0.65',linestyle='-')
    plt.gcf().autofmt_xdate() #Pretty print of dates on x axis
    
    #Plot of trading signal
    plt.plot( long_entries.to_pydatetime(), bollinger_df["Price"][long_entries],  marker='^', color='b', ls='', label="Long Entry" )  
    plt.plot( short_entries.to_pydatetime(), bollinger_df["Price"][short_entries], marker='v', color='r', ls='', label="Short Entry" )
    plt.plot( exits.to_pydatetime(), bollinger_df["Price"][exits],  marker='o', color='g', ls='', label="Exit")
    plt.legend(loc='lower left' )
    
    #Save and show the plot
    if outputfile is not None:
        plt.savefig(outputfile)
    plt.show()
    
    
def test_run():
    """Driver function."""
    
    # Define input parameters
    start_date = '2007-12-31'
    end_date = '2009-12-31'
    stock_symbol = ["IBM"]
       
    #initial cash for the strategy
    start_val = 10000
    
    #Get stock quotation
    dates =  pd.date_range(start_date, end_date)
    stock_prices = get_data(stock_symbol, dates)
    
    #Get bollinger indicator and trading signals    
    bollinger = bollinger_indicator(stock_prices[ stock_symbol[0] ])    
    trading_signal = bollinger_strategy( bollinger )

    #Get orders and save to csv order file
    orders = generate_trades(stock_symbol[0], start_val, bollinger, trading_signal)
    orders_file = os.path.join("orders", "bollinger.csv")    
    orders.to_csv(orders_file, index=False)
    
    #Plot strategy
    plot_bollinger_strategy( bollinger, trading_signal )
    
    #Measure performance of strategy
    #Process orders
    portvals = marketsim.compute_portvals(start_date, end_date, orders_file, start_val)
    portvals = portvals[ "_VALUE" ]
    
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
