#!/usr/bin/env python
"""
Author: Petr Stehlik <xstehl14@stud.fit.vutbr.cz>
"""

import sqlite3
import json
import sys

conn = sqlite3.connect('../db.sq3', check_same_thread=False)
conn.row_factory = sqlite3.Row

records_count = 200

args = sys.argv
if len(args) > 1:
    records_count = int(args[1])

c = conn.cursor()
c.execute("SELECT * FROM weather_data ORDER BY time DESC LIMIT {}".format(records_count))

rows = c.fetchall()

with open('data.json', 'w') as outfile:
    for row in rows:
        record = dict()
        for key in row.keys():
            record[key] = round(row[key], 1)
        outfile.write(json.dumps(record) + "\n")
