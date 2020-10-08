#!/home/aldous.elpizochari/miniconda3/bin/python

import json
import os
import sys
import datetime
from google.cloud import bigquery


def stream_bq(row_dict):
    table_id = "tokopedia-staging-198806.aldous_test.ws_order_debezium"
    rows_to_insert = [row_dict]

    errors = client.insert_rows_json(table_id, rows_to_insert) 
    if errors == []:
        print("New rows have been added.")
        print(json.dumps(row_dict))
    else:
        print("Encountered errors while inserting rows: {}".format(errors))


def convert_epoch(epoch, epoch_range='micro'):
    erange = 1000.
    if epoch_range == 'nano':
        erange = 1000000.
    fmt = "%Y-%m-%d %H:%M:%S"
    t = datetime.datetime.fromtimestamp(float(epoch)/erange)
    return t.strftime(fmt) # 2012-08-28 02:45:17


def parse_create(payload_after, op_type, ts_dbz, ts_db, lsn):
    return {
        "order_id": payload_after.get('order_id'),
        "item_name": payload_after.get('item_name'),
        "created_at": convert_epoch(payload_after.get('created_at'), epoch_range='nano'),
        "OPTYPE": op_type,
        "timestamp_db": convert_epoch(ts_dbz),
        "timestamp_debezium": convert_epoch(ts_db),
        "lsn": lsn
    }


def parse_payload(input_raw_json):
    input_json = json.loads(input_raw_json)
    op_type = input_json.get('payload', {}).get('op')

    if op_type == 'c':
        return parse_create(
            input_json.get('payload', {}).get('after', {}),
            'INSERT',
            input_json.get('payload', {}).get('ts_ms'),
            input_json.get('payload', {}).get('source', {}).get('ts_ms'),
            input_json.get('payload', {}).get('source', {}).get('lsn')
        )
    # elif optype == 'u':
    # elif optype == 'd':

    return {}


client = bigquery.Client()

for line in sys.stdin:
    stream_bq(parse_payload(line))
    
