#!/usr/bin/env python

#from apstools.devices import DeviceMixinBase
from bluesky import RunEngine
from bluesky import SupplementalData
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.utils import get_history
from bluesky.utils import ProgressBarManager
import bluesky.plan_stubs as bps
from databroker import Broker
import epics
import logging
from ophyd import Component, EpicsMotor, EpicsSignal, EpicsSignalRO
import os
# import stdlogpj
import sys
import time

# import ophyd
# logger = logging.getLogger('ophyd.event_dispatcher')
# logger.setLevel("DEBUG")


# logging.basicConfig(level=logging.DEBUG)
# logger = stdlogpj.standard_logging_setup("test3", level=logging.DEBUG)
if len(sys.argv) == 1:
    CYCLES = 10
elif len(sys.argv) == 2:
    CYCLES = int(sys.argv[1])
DELAY_S = 1e-6
MOTOR_PV = "sky:m1"
# MOTOR_PV = "prj:m1"

bec = BestEffortCallback()
# db = Broker.named("mongodb_config")
sd = SupplementalData()
pbar_manager = ProgressBarManager()

RE = RunEngine({})
# RE = RunEngine(get_history())
# RE.subscribe(db.insert)
RE.subscribe(bec)
RE.preprocessors.append(sd)
RE.waiting_hook = pbar_manager


m1 = EpicsMotor(MOTOR_PV, name="m1")
m1.wait_for_connection()


def move(motor, label, dest, delay_s):
    yield from bps.checkpoint()
    yield from bps.mv(
        #m1.description, f"{label}",
        m1,             dest
        )
    msg = f"{label}:  {dest} {motor.position}"
    # print(msg, os.system("uptime"))
    print(msg)
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

