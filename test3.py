#!/usr/bin/env python

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
# ophyd.signal 
for _nm in "ophyd.epics_motor ophyd.positioner ophyd.ophydobj ophyd.status".split():
    logger = logging.getLogger(_nm)
    logger.setLevel("DEBUG")


if len(sys.argv) == 1:
    CYCLES = 10
elif len(sys.argv) == 2:
    CYCLES = int(sys.argv[1])
DELAY_S = 1e-6
MOTOR_PV = "sky:m1"
# MOTOR_PV = "prj:m1"

bec = BestEffortCallback()
sd = bluesky.SupplementalData()
pbar_manager = ProgressBarManager()

RE = bluesky.RunEngine({})
RE.subscribe(bec)
RE.preprocessors.append(sd)
RE.waiting_hook = pbar_manager


m1 = ophyd.EpicsMotor(MOTOR_PV, name="m1")
m1.wait_for_connection()


def move(motor, label, dest, delay_s):
    yield from bps.checkpoint()
    yield from bps.mv(m1, dest)
    msg = f"{label}:  {dest} {motor.position}"
    print(datetime.datetime.now(), msg)
    yield from bps.sleep(delay_s)

i = 0
def ping_pong(motor, v1, v2, delay_s=1e-2):
    global i
    yield from move(motor, f"ping {i+1}", v1, delay_s)
    yield from move(motor, f"pong {i+1}", v2, delay_s)
    i += 1


if __name__ == "__main__":
    RE(
        bps.repeater(
            CYCLES,
            ping_pong,
            m1, 
            .1, 
            -.1, 
            delay_s=DELAY_S,
            )
    )

    for item in (bluesky, ophyd, epics):
        print(item.__name__, item.__version__)
