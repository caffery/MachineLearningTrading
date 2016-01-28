"""MLT - MC2 - P2 Bollinger Bands Strategy"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import util

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
    stock_prices = util.get_data(stock_symbol, dates)
    
    #Get bollinger indicator and trading signals    
    bollinger = bollinger_indicator(stock_prices[ stock_symbol[0] ])    
    trading_signal = bollinger_strategy( bollinger )

    #Get trading signal dates
    long_entries = trading_signal[ trading_signal == "LONG_ENTRY" ] .index
    short_entries = trading_signal[ trading_signal == "SHORT_ENTRY" ] .index
    exits = trading_signal[ (trading_signal == "LONG_EXIT") | (trading_signal == "SHORT_EXIT")] .index
        
    #Plot bollinger bands
    plt.plot( bollinger.index.to_pydatetime(), bollinger )    
    plt.xlabel('Date')
    plt.ylabel('Prices')
    plt.title('Bollinger bands')
    plt.grid(b=True, which='both', color='0.65',linestyle='-')
    plt.gcf().autofmt_xdate() #Pretty print of dates on x axis
    
    #Plot of trading signal
    plt.plot( long_entries.to_pydatetime(), bollinger["Price"][long_entries],  marker='^', color='b', ls='', label="Long Entry" )  
    plt.plot( short_entries.to_pydatetime(), bollinger["Price"][short_entries], marker='v', color='r', ls='', label="Short Entry" )
    plt.plot( exits.to_pydatetime(), bollinger["Price"][exits],  marker='o', color='g', ls='', label="Exit")
    plt.legend(loc='lower left' )
    
    #Save and show the plot
    plt.savefig("output/bollinger.png")
    plt.show()

if __name__ == "__main__":
    test_run()
