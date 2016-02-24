"""
A simple wrapper for Bagging learning.  
"""

import numpy as np
import learners.KNNLearner as knn

class BagLearner():
    
    def __init__(self, learner = knn.KNNLearner, kwargs = {"k":3}, bags = 20, boost = False):
        
        self.learner = learner
        self.kwargs = kwargs
        self.bags = bags
        self.boost = boost
        self.bag_learnt = 0 #Indicates how many bags have learnt
        
        #Create the learners
        self.learners = [ learner( **kwargs ) for i in range(0, bags) ]

    def addEvidence(self, dataX, dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        #Get n_prime, number of samples within each bag
        n = dataX.shape[0]
        indexes = range(0, n)
        n_prime = 0.6 * n       
        
        #Create the first bag
        index_sample = np.random.choice(indexes, size=n_prime, replace=True)
        sample_x = dataX[index_sample, :]
        sample_y = dataY[index_sample]
        self.learners[0].addEvidence(sample_x, sample_y)
        self.bag_learnt += 1
        
        #Create the other bags sequentially depending wether we use boosting or not
        for i in range(1, self.bags):
            if self.boost:
                #For boosting, each samples is weighted according to the classification error
                errors = np.abs( self.query( dataX ) - dataY )
                weights = errors / np.sum( errors )
                #Choose n_prime random samples according to the weighting scheme
                index_sample = np.random.choice(indexes, size=n_prime, replace=True, p=weights)
            else:
                #For normal bagging, weighting scheme is uniform
                index_sample = np.random.choice(indexes, size=n_prime, replace=True)
                
            sample_x = dataX[index_sample, :]
            sample_y = dataY[index_sample]
            #Learn this sub dataset
            self.learners[i].addEvidence(sample_x, sample_y)                
            #Mark this bags as learnt
            self.bag_learnt += 1
            
    def query(self, points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        
        estimates = np.zeros( shape=( points.shape[0], self.bag_learnt ) )
        
        #For each point, get the estimate of each bag        
        for i in range(0, self.bag_learnt):
            estimates[:, i] = self.learners[i].query(points)
            
        return np.mean(estimates, axis=1)
            
    
if __name__=="__main__":
    print "the secret clue is 'zzyzx'"
