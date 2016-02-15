"""
A simple wrapper for K Nearest Neighbor.  
"""

import numpy as np
        
class KNNLearner(object):

    def __init__(self, k = 3):
        self.k = k #Number of neighbors
        pass # move along, these aren't the drones you're looking for

    def addEvidence(self,dataX,dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """        
        #Save the evidence in a dictionary for later O(n) searching        
        self.data_x = dataX
        self.data_y = dataY
                        
    def query(self, points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        #Create output array
        estimates = np.zeros( points.shape[0] )
        
        #This is not the optimal way to do it. We could use KDTrees from scipy
        #for an efficient spacial search. The instructions for this assigment 
        #prevent us from using this library 
        for i, p in enumerate( points ):
            #Euclidean dist of p against all other points in the dataset
            distances = np.linalg.norm( p - self.data_x, ord = 2, axis = 1) 
            K_neighbors_index = np.argsort( distances )[0:self.k]
            K_neighbors_y = self.data_y[ K_neighbors_index ]
            estimates[i] = np.mean( K_neighbors_y )
            
        return estimates     


if __name__=="__main__":
    print "the secret clue is 'zzyzx'"
