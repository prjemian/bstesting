#!/usr/bin/env python

"""
test for TimeoutError

see: https://github.com/bluesky/ophyd/issues/776
"""

import bluesky
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.utils import ProgressBarManager
import bluesky.plan_stubs as bps
import datetime
import epics
import logging
import ophyd
import os
import sys
import time

# ophyd.event_dispatcher
for _nm in "ophyd.signal ophyd.status ophyd.epics_motor ophyd.positioner ophyd.ophydobj".split():
    logger = logging.getLogger(_nm)
    logger.setLevel("DEBUG")

ophyd.EpicsSignal.set_default_timeout(
    timeout=60, 
    read_retries=5, 
    floor=10,
    )


if len(sys.argv) == 1:
    CYCLES = 10
elif len(sys.argv) == 2:
    CYCLES = int(sys.argv[1])
DELAY_S = 1e-6
TEST_PV = "8idi:Reg200"

bec = BestEffortCallback()
sd = bluesky.SupplementalData()
pbar_manager = ProgressBarManager()

RE = bluesky.RunEngine({})
RE.subscribe(bec)
RE.preprocessors.append(sd)
RE.waiting_hook = pbar_manager


pv = ophyd.EpicsSignal(TEST_PV, name="pv")
pv.wait_for_connection()


def move(signal, label, dest, delay_s):
    yield from bps.checkpoint()
    yield from bps.mv(signal, dest)
    msg = f"{label}:  {dest} {signal.value}"
    print(datetime.datetime.now(), msg)
    yield from bps.sleep(delay_s)

i = 0
def ping_pong(signal, v1, v2, delay_s=1e-2):
    global i
    yield from move(signal, f"ping {i+1}", v1, delay_s)
    yield from move(signal, f"pong {i+1}", v2, delay_s)
    i += 1


if __name__ == "__main__":
    for item in (bluesky, ophyd, epics):
        print(item.__name__, item.__version__)

    RE(
        bps.repeater(
            CYCLES,
            ping_pong,
            pv, 
            .1, 
            -.1, 
            delay_s=DELAY_S,
            )
    )

    for item in (bluesky, ophyd, epics):
        print(item.__name__, item.__version__)
