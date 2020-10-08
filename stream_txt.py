#!/home/aldous.elpizochari/miniconda3/bin/python

import json
import os
import sys


def parse_create(payload_after, op_type, ts_dbz, ts_db, lsn):
    out_tuples = [(
        payload_after.get('order_id'),
        payload_after.get('item_name'),
        payload_after.get('created_at'),
        op_type,
        ts_dbz,
        ts_db,
        lsn
    )]
    return out_tuples


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

    return []


for line in sys.stdin:

    data = parse_payload(line)
    for log in data:
        log_str = ','.join([str(elt) for elt in log])
        print(log_str, flush=True)
