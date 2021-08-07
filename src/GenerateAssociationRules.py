"""
Module for generating association rules from market-basket dataset
"""

import sys
import math
import string
import pandas as pd
import numpy as np
import json
from numpy import random
from collections import defaultdict, OrderedDict
from itertools import chain, combinations

class AssociationRuleGenerator:
    """
    Contains the entire codebase for performing top-k tuple extraction using iterative set expansion
    """
    def __init__(self, FILE, SUPP_THRES, CONF_THRES):
        """
        Constructor
        @params:
            :FILEPATH: path to integrated dataset
            :Itemsets: Dictionary containing itemsets as keys and support count as values
            :SUPP_THRES: support threshold to be checked against while generating itemsets and association rules
            :CONF_THRES: confidence threshold to be checked against while generating itemsets and association rules
            :SupportedItemsets: List of itemsets that meet min_supp threshold. Obtained via calling generate_supportem_itemsets
        """
        self.FILE = FILE
        self.Itemsets = defaultdict(lambda:0)
        self.Database = dict()
        self.AssociationRules = defaultdict(lambda:0.0)
        self.SUPP_THRES = SUPP_THRES
        self.CONF_THRES = CONF_THRES
        self.NumTransactions = 0
        self.AllItems = list()
        self.SupportedItemsets = list()        

        #Call preprocess function to populate Itemsets using Integrated dataset
        self.preprocess()
    
    def preprocess(self):
        """
        Populates self.Itemsets (or D per a-priori) using Integrated dataset
        @params:
            :None
        @returns:
            :None
        """
        df = pd.read_csv(self.FILE)
        df = df.fillna(0) #Fill Nans with 0s that can easily be removed later
        # Fetch list of all items based on column headers
        self.AllItems = list(df.columns.values)[1:]
        print("Printing ALL_Items: ----------------------")
        print(self.AllItems)
        print("Printing the dataframe:--------------------")
        print(df.head(5))
        dataframe = df.iloc[:3, :]
        itemdict = df.set_index('Candid').T.to_dict('list') #Transpose and generate python dict
        print("ItemDict: -----------------")
        print(itemdict)
        for key in itemdict.keys(): # Remove 0s, 0.0s and insert into Itemsets dict
            basket = itemdict[key]
            basket = [i for i in basket if (i != 0 or i != 0.0)]
            #Note: Frozensets are hashable so that is used instead of set (source: https://stackoverflow.com/questions/6310867/why-arent-python-sets-hashable)
            self.Database[key] = frozenset(basket)
        # print("Database: ----------------")
        # print(self.Database)
        self.NumTransactions = len(itemdict.keys())
        # # Test random numbers to see if they match raw rdata
        # print("Random num: ", np.random.randint(len(self.Database.keys())))
        # key = list(self.Database.keys())[np.random.randint(len(self.Database.keys()))]
        # print(key)
        # print(self.Database[key])
        # print(self.Itemsets)
    
    def generate_itemsets(self):
        """
        Implements apriori algorithm defined in Section 2.1 of the Agrawal and Srikant paper
        @params:
            :None
        @returns:
            :Itemset: Dictionary with itemsets as keys and support count as value
        """
        # Step 1. Generate L_1 itemsets by counting 1-item occurences in each transaction (line 1):
        L_kminus1 = list()
        for item in self.AllItems:
            one_itemset = frozenset([item])
            self.Itemsets[one_itemset] = 0
            for transaction in self.Database.keys():
                if item in self.Database[transaction]:
                    self.Itemsets[one_itemset] += 1
            # Check if itemset meets SUPP_THRES
            if self.Itemsets[one_itemset]/self.NumTransactions >= self.SUPP_THRES:
                L_kminus1.append(frozenset([item]))
        # Extend SupportedItemsets based on L_1
        self.SupportedItemsets.extend(L_kminus1)
        print("L_kminus1: {} items: {}\n".format(len(L_kminus1),L_kminus1))
        # Step 2. Generate all candidate itemsets and check against threshold
        for k in range(2, len(self.AllItems)+1):
            print("\n=====================")
            print("=== Iter: k = {} ====".format(k))
            print("=====================\n")
            # Termination condition: If L_(k-1) is empty list, return (line 2 termination)
            if not L_kminus1 :
                break
            # Call apriori-gen (line 3)
            C_k = self.apriori_gen(L_kminus1)
            # Increment counts of identified subsets (lines 5-7)
            L_kminus1 = list() 
            count = 0
            print("Now updating itemset support counts")
            for C_t in C_k:
                # print("\nC_t is: {}".format(C_t))
                for transaction in self.Database.keys():
                    if C_t.issubset(self.Database[transaction]):
                        # print("FOUND SUBSET: {} is a subset of {}".format(C_t,transaction))
                        self.Itemsets[(C_t)] += 1
                # print("\n")
                # Append to L_kminus1 if meets SUPP_THRES (line 9)
                if self.Itemsets[C_t]/self.NumTransactions >= self.SUPP_THRES:
                    # print("Identified supported itemset, count: {}, total: {}. supp: {}".format(self.Itemsets[tuple(C_t)], self.NumTransactions, self.Itemsets[tuple(C_t)]/self.NumTransactions))
                    count += 1
                    L_kminus1.append(C_t)
            print("Final count for supported sets for iter {}: {}".format(k, count))
            # Extend SupportedItemsets based on L_1 (Line 11)
            self.SupportedItemsets.extend(L_kminus1)
        #TODO: Change below
        return self.Itemsets
        # return self.SupportedItemsets 

    def apriori_gen(self, L_kminus1):
        """
        Implements the join and prune apriori approach to generating candidate itemsets defined in Section 2.1.1 of the Agrawal and Srikant paper
        @params:
            :L_kminus1: Itemset
        @returns:
            :Itemset: Dictionary with itemsets as keys and support count as value
        """
        C_k = set()
        L_kminus1 = set(L_kminus1)
        # Step 1. Joining phase. SQL implementation is mirrored by extracting only sets with size K+1 when generating C_k
        # Source: https://stackoverflow.com/questions/464864/how-to-get-all-possible-combinations-of-a-list-s-elements, 
        #TODO: Confirm logic behind K+1 set size with Shantanu/Professor
        num_viable_set = 0
        for itemset1 in L_kminus1:
            for itemset2 in L_kminus1:
                C_t = itemset1.union(itemset2)
                # # print("Sorted C_t: ", )
                # present_in_C_k = False
                # for item in C_k:
                #     if sorted(C_t) == sorted(item):
                #         present_in_C_k = True
                if len(C_t) == len(itemset1)+1 and C_t not in C_k:
                    print("\nFound a viable candidate set C_t with len {}: {}".format(len(C_t),C_t))
                    print("From itemset1: {}".format(itemset1))
                    print("From itemset2: {}".format(itemset2))
                    if num_viable_set%10000 == 0:
                        print("Generating {} sets".format(num_viable_set))
                    C_k.add(C_t)
                    num_viable_set += 1
        print("Finished generating viable sets. Num of viable sets: {}".format(num_viable_set))
        # Step 2. Prune phase.
        # L_kminus1 = set(L_kminus1) # Convert to set for faster lookup
        pruned_C_k = list()
        for C_t in C_k:
            supported = True
            for item in C_t: 
                # print("Item: ", item)
                # Copy and create (K-1) subset
                subset = set(C_t.copy())
                subset.remove(item)
                subset = frozenset(subset)
                # print(subset)
                # print("C_t: {}, subset: {}".format(C_t, subset))
                # Check if subset support is below threshold
                if subset not in L_kminus1:
                    # print("\nFound unsupported itemset {}, removing {} from C_k".format(subset,C_t))
                    supported = False
                    break
            if supported:
                pruned_C_k.append(C_t)
        print("\nNum final candidate itemsets are: {}".format(len(pruned_C_k)))
        return pruned_C_k
    
    def generate_association_rules(self):
        """
        For each supported itemset that meets SUPP_THRES, generate powerset of LHS sets for each RHS item using python itertools package.
        Calculates confidence and compares against CONF_THRES
        Source: https://docs.python.org/3/library/itertools.html
        @params:
            :None:
        @returns:
            :Association_Rules: Dictionary with association rules (tuples of (LHS,RHS)) as keys and confidence
        """
        for itemset in self.SupportedItemsets:
            for RHS in itemset:
                # Generate LHS itemset:
                LHS = set(itemset.copy())
                LHS.remove(RHS)
                # Enumerate all 
                LHS_subsets = self.powerset(LHS)
                for subset in LHS_subsets:
                    # Calculate 
                    subset = frozenset(subset)
                    if subset != frozenset([]):
                        confidence = (self.Itemsets[itemset]/self.NumTransactions)/(self.Itemsets[subset]/self.NumTransactions)
                        # print("Confidence for association rule {}: {}".format(tuple((subset,RHS)), confidence))
                        if confidence >= self.CONF_THRES:
                            key = tuple((subset,RHS))
                            self.AssociationRules[key] = confidence
        return self.AssociationRules

    def powerset(self,iterable):
        """
        Generates all combination of subsets for a given iterable
        Source: https://docs.python.org/3/library/itertools.html
        @params:
            :Iterable: Iterable set/list/tuple
        @returns:
            :powerset: Iterable containing all generated subsets 
        """
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
    
    def print_to_txt(self,filename):
        with open(filename, "w+") as f:
            print("==Frequent itemsets (min_sup={}%)==\n".format(self.SUPP_THRES), file=f)
            for item in self.SupportedItemsets:
                print("{}, {}%".format(list(item), self.Itemsets[item]*100/self.NumTransactions),file=f)
            print("\n\n", file=f)
            print("==High-confidence association rules (min_conf={}%)==\n".format(self.CONF_THRES),file=f)
            for rule in self.AssociationRules.keys():
                basket = list(rule[0])
                basket.extend([rule[1]])
                # print("Basket is: {}".format(basket), file=f)
                print("{} => {} (Conf: {}%, Supp: {}%)".format(list(rule[0]), [rule[1]], self.AssociationRules[rule]*100, self.Itemsets[frozenset(basket)]*100/self.NumTransactions),file=f)

def main():
    FILE = sys.argv[1]
    SUPP_THRES = float(sys.argv[2])
    CONF_THRES = float(sys.argv[3])
    session = AssociationRuleGenerator(FILE, SUPP_THRES, CONF_THRES)
    return
    itemsets = session.generate_itemsets()
    # print("Final itemsets: {}".format(itemsets.keys()))
    association_rules = session.generate_association_rules()
    session.print_to_txt("output.txt")
    print("Done!\n")
    # print("Final Association Rules are: {}".format(association_rules))
    # result_set = session.extract_structured_tuples()
    # print("Final number of extracted tuples: {}".format(len(result_set.keys())))

if __name__ == "__main__":
    main()