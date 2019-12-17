#!/usr/bin/env python

import bluesky, bluesky.plan_stubs
import epics
import json
import numpy as np
import ophyd
import time

CYCLES = 10
PERIOD_S = 0.001

m1 = ophyd.EpicsMotor("sky:m1", name="m1")
em1 = epics.Motor("sky:m1")


def print_timings(timings):
    t = np.array(timings)
    rep = dict(
        length = len(t),
        average = np.average(t),
        st_dev = np.std(t),
        max = max(timings),
        min = min(timings),
        )
    print(f"timings: {json.dumps(rep, indent=4)}")


def pyepics_test(cycles=10):
    print("pyepics test")
    timings = []
    
    def move(motor, dest, i=None, period=PERIOD_S):
        motor.move(dest, wait=True)
        print(f"{i}  {dest} {motor.get_position()}")
        time.sleep(period)
    
    for i in range(cycles):
        t0 = time.time()
    
        move(em1, 1, i, PERIOD_S)
        move(em1, -1, i, PERIOD_S)
    
        t = time.time()-t0
        if i:
            timings.append(t)
    
    print_timings(timings)


def ophyd_test(cycles=10):
    print("ophyd test")
    timings = []
    
    def move(motor, dest, i=None, period=PERIOD_S):
        motor.move(dest)
        print(f"{i}  {dest} {motor.position}")
        time.sleep(period)
    
    for i in range(cycles):
        t0 = time.time()
    
        move(m1, 1, i, PERIOD_S)
        move(m1, -1, i, PERIOD_S)
    
        t = time.time()-t0
        if i:
            timings.append(t)
    
    print_timings(timings)


def bluesky_test(cycles=10):
    print("bluesky test")
    RE = bluesky.RunEngine({})

    def move(motor, dest, i=None, period=PERIOD_S):
        yield from bluesky.plan_stubs.sleep(period)
        yield from bluesky.plan_stubs.mv(motor, dest)
        print(f"{i} {dest} {motor.position}")
    
    def ping_pong(v1=1, v2=-1, delay_s=PERIOD_S):
        timings = []
        for i in range(cycles):
            t0 = time.time()
            
            yield from move(m1, 1, i, delay_s)
            yield from move(m1, -1, i, delay_s)

            t = time.time()-t0
            if i:
                timings.append(t)

        print_timings(timings)

    def this_that(fsig, v1, v2, delay_s=PERIOD_S):
        timings = []
        for i in range(cycles):
            t0 = time.time()
    
            yield from bluesky.plan_stubs.sleep(delay_s)
            yield from bluesky.plan_stubs.mv(fsig, v1)
            print(f"{i} {v1} {fsig.value}")
    
            yield from bluesky.plan_stubs.sleep(delay_s)
            yield from bluesky.plan_stubs.mv(fsig, v2)
            print(f"{i} {v2} {fsig.value}")
            t = time.time()-t0
            if i:
                timings.append(t)

        print_timings(timings)

    cycles = 10
    RE(ping_pong())
    cycles = 1000
    RE(this_that(m1.acceleration, 0.25, 0.2))


if __name__ == "__main__":
    pyepics_test()
    ophyd_test()
    bluesky_test()
    
    for pkg in (bluesky, epics, ophyd):
        print(f"{pkg.__name__} version: {pkg.__version__}")
