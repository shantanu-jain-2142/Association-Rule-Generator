# Association Rule Mining
Implementation of Apriori Algorithm for mining association rules on the NYC dataset of City Government Campaign Expenditures.

# Team Members

Phan Anh Nguyen (pn2363)

Shantanu Lalitkumar Jain (slj2142)

# Project Structure
- /src
    - generateAssociationRules.py
    - Integrated_Dataset.csv
    - example-run.txt
    - output.txt
- requirements.txt
- README.md

# Environment
- Python Version: 3.6.9

# Instructions
Please follow the below mentioned instructions for running our program in the VM:
1. Go to the project folder
```
cd proj3/
```
2. Install the dependencies,
```
pip3 install -r requirements.txt
```
3. Run the driver program with the required arguments (mentioned below)
```
python3 src/generateAssociationRules.py src/Integrated_Dataset.csv <Min_Supp> <Min_Conf>
```

# Integrated Dataset Generation

+ We are looking at information regarding NY City Government Campaign Expenditures. For our Integrated Dataset, we have combined data from several years (2001 - 2017). 
+ We generated unique ids for each candidate (or "market basket") by appending "6111" and the campaign year to the id. + We used the "cross-tabs" function available in excel or tableau to visualize the attributes that are present for each campaign id and exported this data to obtain an NxM table (where N is the number of “baskets” M is the total number of possible “items”)
+ Lastly, we performed some final processing to map row attribuets to each of the 17 "items" of expenditure from the original datasets. 
+ Our final Integrated dataset size is 1347x17.

# Project design

Our product code contains a main driver called generateAssociationRules.py. The flow of our program works as follows: 

1. The user starts the program by passing in the Integrated Dataset, a min_supp threshold and min_cong threshold into the command line.
2. Our driver will then preprocess the integrated datasest to produce the initial support counts for one-item itemsets for each of the market baskets
3. The program then proceeds to generate k-item itemsets via the implemented apriori algorithm. For itemset generation, we used the basic generation and prune algorithm proposed by Agrawal and Srikant in section 2.1
4. We then generate association rules by implementing the naive rule-generation and threshold checking method described by Agrawal and Srikant in section 1.1
5. Lastly, we print the output to an "Output.txt" file that contains both supported itemsets as well as generated association rules.

# Analysis of Results

For testing, we found that min_support values betweenn 0.3 and 0.5 and min_conf values between 0.75 and 1.0 yielded the most interesting results. 

For example, running the program on min_supp 0.4 and min_conf 0.75 in the example-run.txt, we were able to extract some interesting association rules such as:
+ ['Campgn Consuls.', 'Campgn Mlngs', 'Prof. Srvcs.'] => ['Fundraising'] (Conf: 94.80069324090121%, Supp: 40.60876020786934%): We interpreted this as campaigns that spend a lot on consultations, mailings and professional services will most likely need to raise a lot of money from fundraising and as such, will also spend accordingly on fundraising efforts
+ ['Petition Expns.', 'Campgn Consuls.', 'Print Ads'] => ['Campgn Lit.'] (Conf: 94.78260869565217%, Supp: 40.46028210838901%): We interpreted this as campaings that spend on petition expansion, and ads then to also spend a lot on promoting campaign literacy. Which is something that we would expect.
['Print Ads', 'Campgn Lit.'] => ['Postage'] (Conf: 76.06727037516171%, Supp: 43.652561247216035%) (Conf: 75.0%, Supp: 43.652561247216035%): Another interesting association rule. Perhaps campaigns that spend on on ad prints and literacy are likely to deliver these ads/literacy materials via postage?

# Additional information

For our presentation, we noticed that program performance tended to deteriorate as we lowered the min_supp value. Our program took relatively long as we went below 0.05 for min_supp. This was most likely due to the dataset that was used. We noticed that there were a few items that had relatively high support. This resulted in market-basket sizes potentially reaching up to k=13 for the lowest support threshold min_sup = 0.01. The limiting step in our program is the generation of all subsets during the first step of the "Apriori Candidate Generation" where K=9 itemset generation could potentially generate up to 17C9 ~ 25,000 possible itemsets, if all K=1 items are supported.

We analyzed generated association rules and were able to identify some interesting trends

# Item mapping

Our dataset items contain abbreviated words. For ease of understanding we have attempted to map each term to their assumed meanings below:

- "Advance Repaymnnt": Advance Repayment fees
- "Campgn Consultations": Fees spent on external consultations for the campaign
- "Campgn Lit.:" Fees spent on promoting campaign literacy
- "Campgn Mlngs": Campaign Mailing expenditure
- "Campgn Wrkrs $$": Expenditure on hired campaign worker salary
- "Fundraising": Fees spent on supporting fundraising efforts
- "Interest Expns.": Fees spent on repaying interests as a result of loans given to campaign
- "Office Rent": Office Rent
- "Petition Expns.": Fees spent on petitioning efforts
- "Polit Contribs.": Fees spent on political contributions
- "Polling Costs": Costs associated with polling
- "Postage": Fees spent on postage
- "Print Ads": Fees spent on printed ads
- "Prof. Srvcs." Fees spent on hiring professional services (i.e: Lawyers, etc.)
- "Radio Ads": Fees spent on radio ads
- "Regis. Mtl/Srvcs": Fees spent on supporting and assisting voter registration/voting processes
- "Television Ads": Fees spent on televised ads

# Dataset Links:
2001 Campaign: https://data.cityofnewyork.us/City-Government/2001-Campaign-Expenditures/k3cd-yu9d

2005 Campaign: https://data.cityofnewyork.us/City-Government/2005-Campaign-Expenditures/easq-ubfe

2009 Campaign: https://data.cityofnewyork.us/City-Government/2009-Campaign-Expenditures/vg63-xw6u

2013 Campaign: https://data.cityofnewyork.us/City-Government/2013-Campaign-Expenditures/kwmq-dbub

2017 Campaign: https://data.cityofnewyork.us/City-Government/2017-Campaign-Expenditures/e9xc-u3ds