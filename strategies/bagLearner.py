"""MC2-P1: Market simulator."""

import pandas as pd
import numpy as np
import os
from util import get_data, plot_data
from portfolio.analysis import get_portfolio_value, get_portfolio_stats, plot_normalized_data
from learners import BagLearner
from indicators import Bollinger, Momentum, Volatility


class BagLearnerStrategy():
    
    def __init__(self, learner = knn.KNNLearner, kwargs = {"k":3}, bags = 20, boost = False):
        
        #Create Learner
        self.learner = BagLearner.BagLearner(learner, kwargs, bags, boost)
        
        #Create training set
        self.training_set = pd.DataFrame()
    
    def AddIndicator(self, indicator):
        self.training_set = self.training_set.join(indicator, how='inner')        
        
    def AddPrediction(self, prediction):
        prediction.columns = ['Prediction']
        self.training_set = self.training_set.join(prediction, how='inner')
        
    def OptimizeStrategy(self):       
        #All columns not marked as Prediction are indicators
        indicators = np.array(data_set.columns != 'Prediction')
        
        #Learn
        trainX = self.training_set.iloc[:, indicators].as_matrix()
        trainY = self.training_set['Prediction'].as_matrix()
        self.learner.addEvidence(trainX, trainY)  
        
    def GenerateTradeSignals(self, ):
        
    
def main():
    # Define input parameters
    start_date = '2007-12-31'
    end_date = '2015-12-31'
    
    #Get quotations
    stock_symbol = ["IBM"]
    dates =  pd.date_range(start_date, end_date)
    stock_prices = get_data(stock_symbol, dates, addSPY=False)
    stock_prices.dropna(inplace=True)
    
    #Learning and test set dates
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

    #Get data to be predicted and indicators
    future_return = stock_prices / stock_prices.shift( 5 ) - 1

    #Create the data sets
    data_set = pd.DataFrame(future_return, columns=['Predictor'] )
    data_set = data_set.joint( bollinger_ind.getIndicator() )
    data_set = data_set.joint( momentum_ind.getIndicator() )
    data_set = data_set.joint( volatility_ind.getIndicator() )     
    learning_set = data_set.ix[learning_dates]
    testing_set = data_set.ix[test_dates]
    
    #Create the Strategy and learn it
    strategy = BagLearnerStrategy()    
    strategy.AddPrediction( learning_set['Predictor']  ) 
    #Add all indicators in data set
    for indicator in learning_set.columns[ learning_set.columns != 'Predictor' ]:
        strategy.AddIndicator( learning_set[ indicator ] )
    strategy.OptimizeStrategy()
    
    #Preduct for the testing set
    test_set = future_return.ix[test_dates]
    test_set = test_set.join( )
    
    
    
def test_run():
   
    
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
