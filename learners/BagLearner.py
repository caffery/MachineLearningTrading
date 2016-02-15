"""
A simple wrapper for Baggin learning.  
"""

import numpy as np
import learners.KNNLearner as knn

class BagLearner():
    
    def __init__(self, learner = knn.KNNLearner, kwargs = {"k":3}, bags = 20, boost = False):
        
        self.learner = learner
        self.kwargs = kwargs
        self.bags = bags
        self.boost = boost
        
        #Create the learners
        self.learners = [ learner( **kwargs ) for i in range(0, bags) ]

    def addEvidence(self,dataX,dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        
        #Get n_prime, number of samples within each bag
        n = dataX.shape[0]
        n_prime = 0.6 * n
        indexes = range(0, n)

        #Create the bags
        for i in range(0, self.bags):
            index_sample = np.random.choice(indexes, size=n_prime, replace=True)
            sample_x = dataX[index_sample, :]
            sample_y = dataY[index_sample]
            self.learners[i].addEvidence(sample_x, sample_y)

        
    def query(self,points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        
        estimates = np.zeros( shape=( points.shape[0], self.bags ) )
        
        #For each point, get the estimate of each bag        
        for i in range(0, self.bags):
            estimates[:, i] = self.learners[i].query(points)
            
        return np.mean(estimates, axis=1)
            
    
if __name__=="__main__":
    print "the secret clue is 'zzyzx'"
