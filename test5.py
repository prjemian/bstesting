#!/usr/bin/env python

"""
test for TimeoutError

see: https://github.com/bluesky/ophyd/issues/776
"""

import datetime
import epics
import logging
import os
import sys
import time

for _nm in "epics epics.ca epics.pv".split():
    logger = logging.getLogger(_nm)
    logger.setLevel("DEBUG")


if len(sys.argv) == 1:
    CYCLES = 10
elif len(sys.argv) == 2:
    CYCLES = int(sys.argv[1])
DELAY_S = 1e-6
TEST_PV = "8idi:Reg200"
TIMEOUT = 1.0


pv = epics.PV(TEST_PV)
pv.wait_for_connection()


def move(signal, label, dest, delay_s):
    signal.put(dest, timeout=TIMEOUT, use_complete=True)
    info = signal.get_with_metadata()
    if info is None:
        raise TimeoutError("timeout")
    print(f"{datetime.datetime.now()}: {label}:  {dest} {signal.value} {info['value']}")
    time.sleep(delay_s)

i = 0
def stepper(signal, delay_s=1e-2):
    global i
    for j in range(5):
        move(signal, f"#{i+1}", j, delay_s)
    i += 1


if __name__ == "__main__":
    print(epics.__name__, epics.__version__)

    for cycle in range(CYCLES):
        stepper(pv, delay_s=DELAY_S)

    print(epics.__name__, epics.__version__)
