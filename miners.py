import pandas as pd
import numpy as np
from itertools import combinations

class AssociationRuleMiner():
    """
    An encapsulation of association rule mining techniques,
    given the following:

        support threshold (in percentage)
        confidence threshold (in percentage)
    """
    def __init__(self, support_threshold:float|str, confidence_threshold:float|str) -> None:
        if isinstance(support_threshold, str):
            support_threshold = float(support_threshold[:-1]) / 100.0

        if isinstance(confidence_threshold, str):
            confidence_threshold = float(confidence_threshold[:-1]) / 100.0

        self.__sup:float = support_threshold
        self.__conf:float = confidence_threshold
        self.__reqsupcount:int = 0

    def __condense_support_count(self, transaction_count:int) -> None:
        self.__reqsupcount = int(self.__sup * transaction_count)

    def __sub_priori(self, transaction_table:pd.DataFrame, support_counts:dict, depth:int=1) -> np.ndarray:
        print(f"support: {self.__sup * 100}%")
        print(f"confidence: {self.__conf * 100}%")
        depth += 1
        
        supported_fields = support_counts[support_counts.support_count > self.__reqsupcount].index
        itemset_checklist = list(combinations(supported_fields, depth))
        print(itemset_checklist)

        next_support_counts = dict()

        for itemset in itemset_checklist:
            tunnelvision = transaction_table[list(itemset)]

            good_matches_count = 0

            for index in range(tunnelvision.shape[0]):
                transaction = tunnelvision.loc[index]
                spotless:bool = True

                for item in itemset:
                    if transaction[item] == False:
                        spotless = False
            
                if spotless:
                    good_matches_count += 1
            
            next_support_counts[itemset] = good_matches_count
        
        print(next_support_counts)

    def apriori(self, transaction_table:pd.DataFrame) -> list:
        """
        words
        """
        
        self.__condense_support_count(transaction_table.shape[0])

        support_table = transaction_table.sum(axis=0).to_frame("support_count")
        self.__sub_priori(transaction_table=transaction_table, support_counts=support_table)

    def fp_growth(self, transaction_table:np.ndarray) -> list:
        """
        words
        """

ass_miner = AssociationRuleMiner(support_threshold=0.2, confidence_threshold=0.5)
test_data = pd.DataFrame(data = [
            [  True,    True,    True,    False ],
            [  False,    False,    True,    False ],
            [  True,    False,    True,    True ],
            [  True,    False,    False,    False ],
            [  True,    False,    False,    True ]
], columns=[ 'I1', 'I2', 'I3', 'I4' ])

ass_miner.apriori(transaction_table=test_data)
