"""MC2-P1: Market simulator."""

import pandas as pd
import numpy as np
import os
from util import get_data, plot_data
from portfolio.analysis import get_portfolio_value, get_portfolio_stats, plot_normalized_data
from learners import BagLearner
from indicators import Bollinger, Momentum, Volatility

def test_run():
    """Driver function."""
    # Define input parameters
    start_date = '2007-12-31'
    end_date = '2015-12-31'
    
    #Get quotations
    stock_symbol = ["IBM"]
    dates =  pd.date_range(start_date, end_date)
    stock_prices = get_data(stock_symbol, dates, addSPY=False)
    stock_prices.dropna(inplace=True)
    
    #Learning and test set dates
    #Get only valid dates with non NaN values
    n_dates = stock_prices.shape[0]
    learning_dates = stock_prices.index.values[0:int(n_dates * 0.60)]
    test_dates = stock_prices.index.values[int(n_dates * 0.60):]
    
    #print stock_prices.ix[learning_dates,]
    print "Learning set from ", learning_dates[0], " to ", learning_dates[-1]
    print "Test set from ", test_dates[0], " to ", test_dates[-1]
    
    #Get indicators
    bollinger_ind = Bollinger.Bollinger()
    momentum_ind = Momentum.Momentum()
    volatility_ind = Volatility.Volatility()    
    bollinger_ind.addPriceSeries( stock_prices )
    momentum_ind.addPriceSeries( stock_prices )
    volatility_ind.addPriceSeries( stock_prices )
    
    #Get data to be predicted
    future_return = stock_prices / stock_prices.shift( 5 ) - 1
    future_return.columns = ['Prediction']
    
    #Merge in a dataframe, combining the three predictors
    data_set = future_return.join(bollinger_ind.getIndicator(), how='inner' )
    data_set = data_set.join(momentum_ind.getIndicator(), how='inner')
    data_set = data_set.join(volatility_ind.getIndicator(), how='inner')    
    data_set.dropna(inplace=True)
    #print learning_set   
        
    #Learning
    learner = BagLearner.BagLearner()
    learning_set = data_set.ix[learning_dates]
    trainX = learning_set.iloc[:, 1:4].as_matrix()
    trainY = learning_set['Prediction'].as_matrix()
    learner.addEvidence(trainX, trainY)
    
    #Testing
    testing_set = data_set.ix[test_dates]
    testX = testing_set.iloc[:, 1:4].as_matrix()
    testY = testing_set['Prediction'].as_matrix()
    predY = learner.query( testX ) # get the predictions
        
    #Build dataframe to show results    
    results = pd.DataFrame( predY, columns = ['PredictedY'], index = test_dates )
    results['RealizedY'] = testY
    results['Error'] = (testY - predY)
    rmse = np.sqrt(((testY - predY) ** 2).sum()/testY.shape[0])
    
    plot_data(results[ ['PredictedY', 'RealizedY'] ] , title="Realized vs Predicted", xlabel="Date", ylabel="Price", filename=None)
    plot_data( results['Error'], title="Prediction error", xlabel="Date", ylabel="Error", filename=None)
   
    print rmse
    
if __name__ == "__main__":
    test_run()
