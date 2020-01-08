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

DEBUG_MODULES = [
    "ophyd.epics_motor",
    "ophyd.positioner",
    "ophyd.signal",
    "ophyd.status",
    "ophyd.ophydobj",
    # "ophyd.event_dispatcher",
    __name__        # always last
]
for _nm in DEBUG_MODULES:
    logger = logging.getLogger(_nm)
    logger.setLevel(logging.DEBUG)


ophyd.EpicsSignal.set_default_timeout(
    timeout=60, 
    read_retries=5, 
    floor=10,
    )


CYCLES = 10
DELAY_S = 0.002e-1
if len(sys.argv) > 1:
    CYCLES = int(sys.argv[1])
    if len(sys.argv) == 3:
        DELAY_S = float(sys.argv[2])
# MOTOR_PV = "sky:m1"
# MOTOR2_PV = "sky:m2"
# MOTOR_PV = "prj:m1"
MOTOR_PV = "8idi:m25"
# NOTE: do not move more than +/- 10 mm from current position (-46)
MOTOR_BASE_POSITION = -46
MOTOR_OFFSET = 0.1

bec = BestEffortCallback()
sd = bluesky.SupplementalData()
pbar_manager = ProgressBarManager()

RE = bluesky.RunEngine({})
RE.log.setLevel(logging.DEBUG)
RE.subscribe(bec)
RE.preprocessors.append(sd)
RE.waiting_hook = pbar_manager


m1 = ophyd.EpicsMotor(MOTOR_PV, name="m1")
# m2 = ophyd.EpicsMotor(MOTOR2_PV, name="m2")
m1.wait_for_connection()
# m2.wait_for_connection()


def when_move_ends(obj):
    print(datetime.datetime.now(), f"move ended: {obj.name}:{obj.position}")

def move(motor, label, dest, delay_s):
    yield from bps.checkpoint()
    t0 = time.time()
    yield from bps.mv(
        motor, dest, 
        # m2, -dest, 
        # moved_cb=when_move_ends
        )
    dt = time.time() - t0
    print(
        f"MOVE: {datetime.datetime.now()} "
        f"{label}:  {dest} {motor.position}  {dt:.6f}"
        "\n# ----------------------------------"
    )
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
            MOTOR_BASE_POSITION + MOTOR_OFFSET, 
            MOTOR_BASE_POSITION - MOTOR_OFFSET, 
            delay_s=DELAY_S,
            )
    )

    for item in (bluesky, ophyd, epics):
        print(item.__name__, item.__version__)
