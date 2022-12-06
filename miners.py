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
        self.__state_log:list = []

    def __condense_support_count(self, transaction_count:int) -> None:
        self.__reqsupcount = int(self.__sup * transaction_count)

    def __reset_metadata(self) -> None:
        self.__state_log = []

    def __sub_priori(self, transaction_table:pd.DataFrame, support_counts:dict, depth:int=1) -> dict:
        depth += 1

        supported_fields = list(filter(lambda x: support_counts[x] > self.__reqsupcount, support_counts)) # Trim support_count with support threshold
        self.__state_log.append({ field: support_counts[field] for field in supported_fields })
        # TODO: Combining supported fields follows a more subtle logic
        itemset_checklist = list(combinations(supported_fields, depth))
        print(itemset_checklist)

        next_support_counts = dict()

        for itemset in itemset_checklist:
            print('itemset:', itemset)
            tunnelvision = transaction_table[list(itemset)]

            good_matches_count = 0

            for index in tunnelvision.index:
                transaction = tunnelvision.loc[index]
                spotless:bool = True

                for item in itemset:
                    if not transaction[item]:
                        spotless = False

                if spotless:
                    good_matches_count += 1

            next_support_counts[itemset] = good_matches_count

        print(next_support_counts)

        if len(next_support_counts) > 0:
            return self.__sub_priori(transaction_table=transaction_table, support_counts=next_support_counts, depth=depth)

        return support_counts

    def apriori(self, transaction_table:pd.DataFrame) -> dict:
        """
        words
        """
        # print(f"support: {self.__sup * 100}%")
        # print(f"confidence: {self.__conf * 100}%")
        self.__condense_support_count(transaction_table.shape[0])
        self.__reset_metadata()

        support_table = transaction_table.sum(axis=0).to_dict()
        
        print(support_table)
        
        frequent_itemset = self.__sub_priori(transaction_table=transaction_table, support_counts=support_table)
        
        print('Frequent Itemset:', frequent_itemset)
        print('State Log:', self.__state_log)

        return frequent_itemset

    def fp_growth(self, transaction_table:np.DataFrame) -> dict:
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