import pandas as pd
import numpy as np

df = pd.read_parquet('../../data/data.parquet.gzip')
print(len(df))  # 511427

# Unique countries present in data
print(df['country_code'].unique())  # ['China' 'Peru' 'Australia' 'Latvia']

# Since country of interest is Peru, filtering only Peru assuming voucher amount differs on countries
df_peru = df.loc[df['country_code'] == 'Peru']
print(len(df_peru))  # 106547

# Finding missing value
print(df_peru['voucher_amount'].isnull().sum())  # 13950

# Check how many records have timestamp is less than last_order_ts
df_peru_error = df_peru.loc[df_peru['timestamp'] < df_peru['last_order_ts']]
print(len(df_peru_error))  # 8624

# Filter records for timestamp greater than or equal to last_order_ts
df_peru = df_peru.loc[df_peru['timestamp'] >= df_peru['last_order_ts']]

# Finding Voucher amount distribution for replacing missing value
print(df_peru['voucher_amount'].describe())

'''
count    85048.000000
mean      3257.152667
std        721.686882
min       2640.000000
25%       2640.000000
50%       2640.000000
75%       3520.000000
max       4400.000000
'''

# Replacing missing voucher with 50% percentile
# According to data 2640 is the common voucher_amount
df_peru['voucher_amount'].fillna(value=2640, inplace=True)

# Check total orders
df_peru['total_orders'] = pd.to_numeric(df_peru['total_orders'], errors='coerce')
df_peru['total_orders'].fillna(value=0, inplace=True)

print(df_peru['total_orders'].describe())
'''
count    97923.000000
mean        44.891844
std         52.932883
min          0.000000
25%          2.000000
50%         27.000000
75%         52.000000
max        516.000000
'''

# create a list of our conditions
conditions_total_orders = [
    (df_peru['total_orders'] >= 0) & (df_peru['total_orders'] < 5),
    (df_peru['total_orders'] >= 5) & (df_peru['total_orders'] < 14),
    (df_peru['total_orders'] >= 14) & (df_peru['total_orders'] < 38),
    (df_peru['total_orders'] >= 38)
]

# create a list of the values we want to assign for each condition
values_total_orders = ['0-4', '5-13', '14-37', '38>']

# create a new column and use np.select to assign values to it using our lists as arguments
df_peru['frequent_segment'] = np.select(conditions_total_orders, values_total_orders)

print(df_peru)

df_peru[['timestamp', 'last_order_ts']] = df_peru[['timestamp', 'last_order_ts']].apply(pd.to_datetime)
df_peru['days'] = (df_peru['timestamp'] - df_peru['last_order_ts']).dt.days
print(df_peru)

# create a list of our conditions
conditions_days = [
    (df_peru['days'] >= 30) & (df_peru['days'] < 61),
    (df_peru['days'] >= 61) & (df_peru['days'] < 91),
    (df_peru['days'] >= 91) & (df_peru['days'] < 121),
    (df_peru['days'] >= 121) & (df_peru['days'] < 181),
    (df_peru['days'] >= 181),
    (df_peru['days'] < 30)
]

# create a list of the values we want to assign for each condition
values_total_days = ['30-60', '61-90', '91-120', '121-180', '180+', '<30']

# create a new column and use np.select to assign values to it using our lists as arguments
df_peru['recency_segment'] = np.select(conditions_days, values_total_days)

# No data found for days since the last order greater than 121+
print(df_peru['recency_segment'].unique())
print(df_peru['frequent_segment'].unique())

df_peru_recency_segment = df_peru.groupby(['recency_segment', 'voucher_amount'])[
    'country_code'].count().sort_values().groupby(level=0).tail(1)
df_peru_frequent_segment = df_peru.groupby(['frequent_segment', 'voucher_amount'])[
    'country_code'].count().sort_values().groupby(level=0).tail(1)

df_peru_recency_segment = df_peru_recency_segment.reset_index()
df_peru_frequent_segment = df_peru_frequent_segment.reset_index()

df_peru_recency_segment['segment_name'] = 'recency_segment'
df_peru_frequent_segment['segment_name'] = 'frequent_segment'

df_peru_recency_segment.rename(columns={'recency_segment': 'segment_variants'}, inplace=True)
df_peru_frequent_segment.rename(columns={'frequent_segment': 'segment_variants'}, inplace=True)

df_row_merged = pd.concat([df_peru_recency_segment, df_peru_frequent_segment], ignore_index=True)
df_row_merged.rename(columns={'country_code': 'max_count'}, inplace=True)
print(df_row_merged)
