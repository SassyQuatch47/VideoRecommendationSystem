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

    def __mine_from_freq_itemset(self, frequent_itemset:dict, frequency_tables:list = None, transaction_table:pd.DataFrame=None) -> dict:
        
        assoc_rules = dict()

        if frequency_tables is None:
            if transaction_table is None:
                raise ValueError('for mining associations from frequent itemsets, neither frequency_tables nor a transaction_table are provided.')
            frequency_tables = [[]]
            # TODO: generate frequencies from transaction_table
        
        # print(frequent_itemset)
        for item in frequent_itemset:
        
            item_support_count = frequent_itemset[item]
            # print('item:', item, ":sup:", item_support_count)

            # hypothesis_size = 1
            # ------------------------------------------------------------------------------
            hypothesis_set = list(combinations(item, r=1))
            # print(f'hypothesis set[{1}]:', hypothesis_set)
                
            for hypothesis in hypothesis_set:
                try:
                    hypothesis_support_count = frequency_tables[0][hypothesis[0]]
                except KeyError:
                    hypothesis_support_count = 0
                # print(f'{hypothesis}:', hypothesis_support_count)
                try:
                    confidence = item_support_count / hypothesis_support_count
                except ZeroDivisionError:
                    confidence = 0
                # print('hypothesis:', hypothesis, ":sup:", hypothesis_support_count, ":conf:", confidence)
                
                if confidence > self.__conf:
                    inference = [ element for element in item if element not in hypothesis ]
                    assoc_rules[hypothesis] = inference
                    # print(f'{hypothesis} => {inference}')
            # ------------------------------------------------------------------------------

            # hypothesis_size > 1
            # ------------------------------------------------------------------------------
            for hypothesis_size in range(2, len(item)):
                hypothesis_set = list(combinations(item, r=hypothesis_size))
                # print(f'hypothesis set[{hypothesis_size}]:', hypothesis_set)
                
                for hypothesis in hypothesis_set:
                    try:
                        hypothesis_support_count = frequency_tables[hypothesis_size - 1][hypothesis]
                        confidence = item_support_count / hypothesis_support_count
                    except KeyError:
                        print('ERR: Key failure')
                    finally:
                        # print('hypothesis:', hypothesis, "sub:", hypothesis_support_count, ":conf:", confidence)
                        
                        if confidence > self.__conf:
                            inference = [ element for element in item if element not in hypothesis ]
                            assoc_rules[hypothesis] = inference
                            # print(f'{hypothesis} => {inference}')
            # ------------------------------------------------------------------------------

        return assoc_rules

    def __gen_apriori_candidates(self, supported_fields:list) -> list:
        candidates = list()

        support_size = len(supported_fields)

        if support_size == 0:
            return candidates

        if isinstance(supported_fields[0], str):
            supported_fields = [ (field,) for field in supported_fields ]

        for left_index in range(support_size - 1):
            left_field = supported_fields[left_index]
            right_start = left_index + 1

            # print('left:', left_field)
            for right_index in range(right_start, support_size):
                right_field = supported_fields[right_index]
                
                # print('right:', right_field)
                # difference_left = [ element for element in left_field if element not in right_field ]
                # difference_right = [ element for element in right_field if element not in left_field ]
                difference = [ element for element in right_field if element not in left_field ]
                # print('difference', difference)

                if len(difference) < 2:
                    candidates.append(( *left_field, *difference ))

        # print('candidates:', candidates)
        return candidates

    def __sub_priori(self, transaction_table:pd.DataFrame, support_counts:dict, depth:int=1) -> dict:
        depth += 1

        self.__state_log.append(support_counts)
        supported_fields = list(filter(lambda x: support_counts[x] > self.__reqsupcount, support_counts)) # Trim support_count with support threshold
        itemset_checklist = self.__gen_apriori_candidates(supported_fields=supported_fields)
        # print(itemset_checklist)

        next_support_counts = dict()

        for itemset in itemset_checklist:
            # print('itemset:', itemset)
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

            if good_matches_count > self.__reqsupcount:
                next_support_counts[itemset] = good_matches_count

        # print(next_support_counts)

        if len(next_support_counts) > 0:
            return self.__sub_priori(transaction_table=transaction_table, support_counts=next_support_counts, depth=depth)

        return support_counts

    def apriori(self, transaction_table:pd.DataFrame) -> dict:
        """
        words
        """
        print(f"with support: {self.__sup * 100}%")
        print(f"with confidence: {self.__conf * 100}%")
        self.__condense_support_count(transaction_table.shape[0])
        self.__reset_metadata()

        support_table = transaction_table.sum(axis=0).to_dict()
        
        # print(support_table)
    
        frequent_itemset = self.__sub_priori(transaction_table=transaction_table, support_counts=support_table)

        # print('Frequent Itemset:', frequent_itemset)
        if len(frequent_itemset) < 1:
            print('low frequnecy (support too high)')
            return {}

        if not isinstance(list(frequent_itemset.keys())[0], list|tuple|dict):
            print('single element frequencies found. Discarding results (support too high)')
            return {}
            # frequent_itemset = { (item,):frequent_itemset[item] for item in frequent_itemset }
        # print('State Log:', self.__state_log)

        associations = self.__mine_from_freq_itemset(frequent_itemset=frequent_itemset, frequency_tables=self.__state_log)
        
        if len(associations) < 1:
            print('no associations found (confidence too high)')

        # print('associations:', associations)
        
        return associations

    def fp_growth(self, transaction_table:pd.DataFrame) -> dict:
        """
        words
        """
