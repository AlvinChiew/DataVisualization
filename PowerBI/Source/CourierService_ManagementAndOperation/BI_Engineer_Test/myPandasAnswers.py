#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import pandas as pd

# Edit the two paths to vanorder and vaninterest csv files
vanorder_path = './vanorder.csv'
vaninterest_path = './vaninterest.csv'

# Read the two csv into pandas DataFrame, parsing the datetime columns
vanorder = pd.read_csv(vanorder_path, parse_dates=['order_datetime', 'txCreate'])
vaninterest = pd.read_csv(vaninterest_path, parse_dates=['txCreate'])

# print(vaninterest.tail(3))
# print(vanorder.tail(3))
# print(vanorder.iloc[3])

print(vaninterest.columns)
# print(vaninterest.dtypes)
print(vanorder.columns)
# print(vanorder.dtypes)


# Q1 What is the order fulfillment rate, i.e. percentage of orders that was completed, based on order time?
vanorder['hour'] = vanorder['order_datetime'].dt.hour
vanorder_byHour = vanorder.groupby(['hour']).count()['idvanOrder'].reset_index(name="#_all_order")
vanorder_byHour_completedOrder = vanorder[vanorder['order_status'] == 2 ].groupby(['hour']).count()['idvanOrder'].reset_index(name="#_completed_order")

vanorder_byHour = pd.concat([vanorder_byHour,vanorder_byHour_completedOrder['#_completed_order']], axis = 1, sort=False)
vanorder_byHour['%_order_fulfillment_rate'] = vanorder_byHour['#_completed_order'] / vanorder_byHour['#_all_order'] * 100
vanorder_byHour['%_order_fulfillment_rate']  = round(vanorder_byHour['%_order_fulfillment_rate'] ,2)
print(vanorder_byHour)

# Q2 We will now look at the match time. Match time is the time it takes from user placing the order, to the driver accepting the order. For this part, consider only orders with a driver at subset A, i.e. all records with a driver at subset A in vaninterest table.
vaninterest.rename(columns = {"txCreate" : "txCreate_driver"}, inplace = True)
vanorder.rename(columns = {"txCreate" : "txCreate_user"}, inplace = True)

vaninterest_A = vaninterest[vaninterest['order_subset_assigned'].str.match("A")]
vanorder_A = vanorder[vanorder['order_subset'].str.match("A")]

vaninterest_A.describe().loc[['count']]
vanorder_A.describe().loc[['count']]


vanMasterTable_A = vaninterest_A.merge(vanorder_A[['idvanOrder','txCreate_user', 'order_datetime']], on='idvanOrder', how='left')
vanMasterTable_A['matchTime'] = (vanMasterTable_A['txCreate_driver'] - vanMasterTable_A['txCreate_user']).astype('timedelta64[m]')
vanMasterTable_A['order_place_time'] = (vanMasterTable_A['order_datetime'] - vanMasterTable_A['txCreate_user']).astype('timedelta64[m]')

vanMasterTable_A['orderPeriod'] = "advanced"
vanMasterTable_A.loc[vanMasterTable_A['order_place_time'] <= 60, 'orderPeriod'] = "immediate"

print(vanMasterTable_A.iloc[0])

#  (a) What is the average match time, by immediate/advanced orders? Immediate orders are defined as orders with order time within 60 minutes(inclusive) of placed time
print(vanMasterTable_A.groupby(['orderPeriod']).mean()['matchTime'].reset_index(name="mean_matchTime"))

#  (b) What is the median match time, again by immediate/advanced?
print(vanMasterTable_A.groupby(['orderPeriod']).median()['matchTime'].reset_index(name="median_matchTime"))

#  (c) Which of the above one do you think provides a better representation the data, i.e. a better metric for tracking our performance in matching?
# vanMasterTable_A.to_csv('masterTable.csv', sep=',')

# Ans : in the context of statistics, there is no better or worse. Both give important information,i.e.
#           Mean/Average tells you the average performance; Median tells you how much the data is skewed towards one extreme.
#           From the graph plot below, we know that the majority of the match time is 0 to 1 minute regardless of the order period (immediate/advanced)
#           The reason that the average match time for advanced order = 12.2minute is because of the outliers (match time = 260 minutes). And this can be explained because the customer made order during midnight ('4/18/2017 0:46'). There might be less driver.
#           I will suggest to use both. In this case we see that the majority of the match time is good (median), and we know that there is significant outlier we have to take care (average and the graph) in order to further boosting the overall performance.

import matplotlib.pyplot as plt

vanMasterTable_A_groupedImmediate = vanMasterTable_A[vanMasterTable_A['orderPeriod'].str.match("immediate")].groupby(['matchTime']).count()['idvanInterest'].reset_index(name="#_order")
print(vanMasterTable_A_groupedImmediate.tail())
plt.bar(vanMasterTable_A_groupedImmediate['matchTime'], vanMasterTable_A_groupedImmediate['#_order'])
plt.xticks(vanMasterTable_A_groupedImmediate['matchTime'])
plt.show()

vanMasterTable_A_groupedAdvanced = vanMasterTable_A[vanMasterTable_A['orderPeriod'].str.match("advanced")].groupby(['matchTime']).count()['idvanInterest'].reset_index(name="#_order")
print(vanMasterTable_A_groupedAdvanced.tail())
plt.bar(vanMasterTable_A_groupedAdvanced['matchTime'], vanMasterTable_A_groupedAdvanced['#_order'])
#plt.xticks(vanMasterTable_A_groupedAdvanced['matchTime'], rotation='vertical')
plt.show()