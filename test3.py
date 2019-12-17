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
import sys
import time

# logging.basicConfig(level=logging.DEBUG)
REPETITIONS = 10
if len(sys.argv) == 1:
    CYCLES = 25
elif len(sys.argv) == 2:
    CYCLES = int(sys.argv[1])
DELAY_S = 1e-6

bec = BestEffortCallback()
db = Broker.named("mongodb_config")
sd = SupplementalData()
pbar_manager = ProgressBarManager()

RE = RunEngine(get_history())
RE.subscribe(db.insert)
RE.subscribe(bec)
RE.preprocessors.append(sd)
RE.waiting_hook = pbar_manager


m1 = EpicsMotor("sky:m1", name="m1")
while not m1.connected:
    time.sleep(.05)


def move(motor, label, dest, delay_s):
    yield from bps.checkpoint()
    yield from bps.mv(
        #m1.description, f"{label}",
        m1,             dest
        )
    msg = (
        f"{label}:"
        # f" ({motor.travel_direction.get()})"
        # f" ({motor.motor_done_move.get()})"
        f"  {dest}"
        f" {motor.position}"
        )
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

