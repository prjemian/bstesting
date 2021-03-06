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
import math
import ophyd
import os
import sys
import time

# ophyd.event_dispatcher
for _nm in "ophyd.signal ophyd.status ophyd.epics_motor ophyd.positioner ophyd.ophydobj".split():
    logger = logging.getLogger(_nm)
    logger.setLevel("DEBUG")

# ophyd.set_cl('caproto') # use caproto instead of PyEpics
ophyd.EpicsSignal.set_default_timeout(timeout=60)


if len(sys.argv) == 1:
    CYCLES = 10
elif len(sys.argv) == 2:
    CYCLES = int(sys.argv[1])
DELAY_S = 1e-6
if len(sys.argv) > 1:
    CYCLES = int(sys.argv[1])
    if len(sys.argv) == 3:
        DELAY_S = float(sys.argv[2])
TEST_PV = "8idi:Reg200"

bec = BestEffortCallback()
sd = bluesky.SupplementalData()
pbar_manager = ProgressBarManager()

RE = bluesky.RunEngine({})
RE.log.setLevel(logging.DEBUG)
RE.subscribe(bec)
RE.preprocessors.append(sd)
RE.waiting_hook = pbar_manager

pv = ophyd.EpicsSignal(TEST_PV, name="pv")
pv.wait_for_connection()


def move(signal, label, dest, delay_s):
    yield from bps.checkpoint()
    t0 = time.time()
    ret = yield from bps.mv(signal, dest)
    dt = time.time() - t0
    scale = "@"*max(1,int(math.log10(dt)+4))
    print(
        f"{datetime.datetime.now()} "
        f"MOVE: {scale} {label}:  {dest} {signal.value}  {dt:.6f}"
        # f"MOVE: {label}:  {dest} {ret['data'][signal.name]}  {dt:.6f}"
        # f"MOVE: {label}:  {dest} {ret}  {dt:.6f}"
        "\n# ----------------------------------"
    )
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
