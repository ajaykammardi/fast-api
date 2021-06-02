import psycopg2 as pg
import pandas as pd
import numpy as np

from psycopg2 import extras


def data_reader():
    df = pd.read_parquet('/app/data/data.parquet.gzip')
    return df


def data_cleaner(df_to_clean):
    # Since country of interest is Peru, filtering only Peru assuming voucher amount differs on countries
    df_peru = df_to_clean.loc[df_to_clean['country_code'] == 'Peru']

    # Filter records for timestamp greater than or equal to last_order_ts
    df_peru = df_peru.loc[df_peru['timestamp'] >= df_peru['last_order_ts']]

    # Replacing missing voucher with 50% percentile
    # According to data 2640 is the common voucher_amount
    df_peru['voucher_amount'].fillna(value=2640, inplace=True)

    # Check total orders
    df_peru['total_orders'] = pd.to_numeric(df_peru['total_orders'], errors='coerce')
    df_peru['total_orders'].fillna(value=0, inplace=True)

    return df_peru


def data_tranformation(df_to_transform):
    # create a list of our conditions

    conditions_total_orders = [
        (df_to_transform['total_orders'] >= 0) & (df_to_transform['total_orders'] < 5),
        (df_to_transform['total_orders'] >= 5) & (df_to_transform['total_orders'] < 14),
        (df_to_transform['total_orders'] >= 14) & (df_to_transform['total_orders'] < 38),
        (df_to_transform['total_orders'] >= 38)
    ]

    # create a list of the values we want to assign for each condition
    values_total_orders = ['0-4', '5-13', '14-37', '38>']

    # create a new column and use np.select to assign values to it using our lists as arguments
    df_to_transform['frequent_segment'] = np.select(conditions_total_orders, values_total_orders)

    df_to_transform[['timestamp', 'last_order_ts']] = df_to_transform[['timestamp', 'last_order_ts']].apply(pd.to_datetime)
    df_to_transform['days'] = (df_to_transform['timestamp'] - df_to_transform['last_order_ts']).dt.days

    # create a list of our conditions
    conditions_days = [
        (df_to_transform['days'] >= 30) & (df_to_transform['days'] < 61),
        (df_to_transform['days'] >= 61) & (df_to_transform['days'] < 91),
        (df_to_transform['days'] >= 91) & (df_to_transform['days'] < 121),
        (df_to_transform['days'] >= 121) & (df_to_transform['days'] < 181),
        (df_to_transform['days'] >= 181),
        (df_to_transform['days'] < 30)
    ]

    # create a list of the values we want to assign for each condition
    values_total_days = ['30-60', '61-90', '91-120', '121-180', '180+', '<30']

    # create a new column and use np.select to assign values to it using our lists as arguments
    df_to_transform['recency_segment'] = np.select(conditions_days, values_total_days)

    df_peru_recency_segment = df_to_transform.groupby(['recency_segment', 'voucher_amount'])[
        'country_code'].count().sort_values().groupby(level=0).tail(1)

    df_peru_frequent_segment = df_to_transform.groupby(['frequent_segment', 'voucher_amount'])[
        'country_code'].count().sort_values().groupby(level=0).tail(1)

    df_peru_recency_segment = df_peru_recency_segment.reset_index()
    df_peru_frequent_segment = df_peru_frequent_segment.reset_index()

    df_peru_recency_segment['segment_name'] = 'recency_segment'
    df_peru_frequent_segment['segment_name'] = 'frequent_segment'

    df_peru_recency_segment.rename(columns={'recency_segment': 'segment_variants'}, inplace=True)
    df_peru_frequent_segment.rename(columns={'frequent_segment': 'segment_variants'}, inplace=True)

    df_row_merged = pd.concat([df_peru_recency_segment, df_peru_frequent_segment], ignore_index=True)
    df_row_merged['country_code'] = 'Peru'

    # No data found for days since the last order greater than 121+
    # Loading the value with 75% - 3520
    insert_loc = df_row_merged.index.max()
    df_row_merged.loc[insert_loc + 1] = ['121-180', 3520.0, 'Peru', 'recency_segment']
    df_row_merged.loc[insert_loc + 2] = ['180+', 3520.0, 'Peru', 'recency_segment']

    return df_row_merged


def data_loader(df_to_load):
    try:
        dbconnect = pg.connect(
            database='postgres_db',
            user='postgres_user',
            password='postgres',
            host='postgresdb',
            port=5432
        )
    except Exception as error:
        print(error)
    tuples = [tuple(x) for x in df_to_load.to_numpy()]

    cursor = dbconnect.cursor()

    cols = ','.join(list(df_to_load.columns))
    query = "INSERT INTO %s(%s) VALUES %%s" % ('customer_voucher_segments', cols)

    try:
        extras.execute_values(cursor, query, tuples)
        dbconnect.commit()
    except (Exception, pg.DatabaseError) as error:
        print(error)
        dbconnect.rollback()
    cursor.close()


if __name__ == '__main__':
    print('Etl Process starts')
    cleaned_data = data_cleaner(data_reader())
    transformed_data = data_tranformation(cleaned_data)
    data_loader(transformed_data)
    print('Etl Process completed...!!!')




