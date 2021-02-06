import json
import argparse
import math
import time
import warnings
'''Copyright 2021 Ramón González Ruiz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'''

CRED = '\033[91m'
CEND = '\033[0m'
CGREEN  = '\33[32m'
# Instantiate the parser
parser = argparse.ArgumentParser(description='Portfolio Manager Application')
# Required positional argument

parser.add_argument('amount_introduced', type=int,
                    help='Amount of money to be introduced in the portfolio')
                    # Required positional argument
parser.add_argument('input_json', type=str,
                    help='json containing the data of the portfolio (i.e allocation, current amount allocated per asset, buy comissions...')
parser.add_argument('--rebalance', action='store_true',
                    help='Indicate wether rebalancing must be carried out')
args = parser.parse_args()
print("Amount of capital to be added: " + str(args.amount_introduced))
print("File with portfolio details: " + args.input_json)
print("Rebalancing: " + str(args.rebalance))
amount_introduced=args.amount_introduced
input_portfolio_json=args.input_json
rebalance=args.rebalance
#load input portfolio json
with open(input_portfolio_json) as f:
  portfolio = json.load(f)
  print(f.read())

#look for unallocated captital to add
for asset in portfolio:
    if asset.get("Is_Unallocated")=="1":
            amount_introduced+=float(asset["Allocated"])

#calculate total amount of allocated capital
total_allocated=0
for asset in portfolio:
    if asset.get("Is_Unallocated")!="1":
        total_allocated+=float(asset["Allocated"])
        total_allocated+=float(asset["Reserved"])

    #calculate current allocation per asset
    allocation_deviation_list=[]
    for asset in portfolio:
        if asset.get("Is_Unallocated")!="1":
            if total_allocated == 0:
                asset["Current_allocation"]=0
            else:    
                asset["Current_allocation"]=float(asset["Allocated"])/total_allocated
            asset["Allocation_Deviation"]=float(asset["Current_allocation"])-float(asset["Allocation"])
            allocation_deviation_list.append(asset["Allocation_Deviation"])
    allocation_deviation_list = sorted(allocation_deviation_list, key=float)
if rebalance == True:
    print(CRED +"Rebalancing not yet implemented: TODO"+CEND)

#calculate quantity of assets to be added and quantity to be reserved for future iterations
for i in allocation_deviation_list:
    for asset in portfolio:
        if float(asset.get("Allocation_Deviation"))==i:
            if asset["Minnimum_Movement_Size"]=="0": #free movement
                asset["ToBeAdded"], Reserved =  divmod((float(asset["Allocation"])*(amount_introduced)+float(asset["Reserved"])-float(asset["Movement_Comission"]))/float(asset["Price"]),1)   
                asset["Reserved"] = Reserved*float(asset["Price"])
            elif (float(asset["Allocation"])*(amount_introduced)+float(asset["Reserved"]))>=float(asset["Minnimum_Movement_Size"]): #if the amount is above the defined lower threshold
                asset["ToBeAdded"], Reserved =  divmod((float(asset["Allocation"])*(amount_introduced)+float(asset["Reserved"])-float(asset["Movement_Comission"]))/float(asset["Price"]),1)   
                asset["Reserved"] = Reserved*float(asset["Price"]) 
            else: #if it is below the threshold it is reserved 
                asset["Reserved"]=float(asset["Allocation"])*(amount_introduced)+float(asset["Reserved"])
    Allocated= float(asset.get("ToBeAdded") or 0)*float(asset["Price"])
    asset["Allocated"]=Allocated

#Stdout summary & json output 
total_added=0
total_reserved=0
for asset in portfolio:
    total_added+=float(asset.get("ToBeAdded") or 0)*float(asset["Price"])
    total_reserved+=float(asset.get("Reserved") or 0)
print(CGREEN +"-----")    
print("Added in this iteration: " + str(total_added))
print("Reserved in this iteration: " + str(total_reserved))
print("-----" + CEND)
for asset in portfolio:
    asset.pop('Allocation_Deviation', None)
    print("-----")
    print(asset["Asset"]+":")
    print("Price: " + asset["Price"])
    print("Quantity to be added: " + str(int(asset.get("ToBeAdded") or 0)))
    print("Reserved for future additions: " + str(asset.get("Reserved")))
    print("-----")
with open(input_portfolio_json.split(".")[0]+"_"+time.strftime("%d_%m_%Y")+".json", 'w') as f:
    json.dump(portfolio,f,sort_keys=True, indent=4)

