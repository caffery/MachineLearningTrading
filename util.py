"""MLT: Utility code."""
import os
import pandas as pd
import pandas.io.data
import matplotlib.pyplot as plt

def symbol_to_path(symbol, base_dir=os.path.join(".", "data")):
    """Return CSV file path given ticker symbol."""
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))


def get_data(symbols, dates, addSPY=True):
    """Read stock data (adjusted close) for given symbols from CSV files.
    TODO: We should always download the file from the database   
    """
    df = pd.DataFrame(index=dates)
    if addSPY and 'SPY' not in symbols:  # add SPY for reference, if absent
        symbols = ['SPY'] + symbols

    for symbol in symbols:
        #Check the csv file exist, otherwise download from Yahoo! Finance
        #TODO: We should rewrite this code, if the file exists but with other dates
        #it will fail
        if not os.path.isfile( symbol_to_path(symbol) ):
            date_init = dates[0].to_datetime()
            date_end = dates[-1].to_datetime()
            download_data(symbol, [date_init, date_end])
        
        #Read only dates and Adj Close column        
        df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                parse_dates=True, usecols=['Date', 'Adj Close'], na_values=['nan'])
        df_temp = df_temp.rename(columns={'Adj Close': symbol})
        
        #Join this symbol to the global data frame        
        df = df.join(df_temp)
        if symbol == 'SPY':  # drop dates SPY did not trade
            df = df.dropna(subset=["SPY"])

    return df


def plot_data(df, title="Stock prices", xlabel="Date", ylabel="Price", filename=None):
    """Plot stock prices with a custom title and meaningful axis labels."""
    ax = df.plot(title=title, fontsize=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    if filename is not None:
        plt.savefig(filename)
        
    plt.show()
    

def download_data(symbol, dates):
    """Download historical prices from Yahoo Finance website and save
    the data into CSV files."""
    historical = pd.io.data.DataReader(symbol, 'yahoo', dates[0], dates[1])
    historical.to_csv( symbol_to_path(symbol) )        
    
        
    
    