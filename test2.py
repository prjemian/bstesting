#!/usr/bin/env python

import bluesky, bluesky.plan_stubs
import epics
import numpy as np
import ophyd
import pyRestTable
import time

REPETITIONS = 10
CYCLES = 1000
PERIOD_S = 0.001

f1 = ophyd.EpicsSignal("IOC:float1", name="f1")
ef1 = epics.PV("IOC:float1")
time.sleep(1)
f1.read()
ef1.get()
results = None


def d2t(d):
    table = pyRestTable.Table()
    table.labels = "key value".split()
    for k, v in d.items():
        table.addRow((k, v))
    return table


def print_timings(timings):
    t = np.array(timings)
    rep = dict(
        length = len(t),
        average = np.average(t),
        st_dev = np.std(t),
        max = max(timings),
        min = min(timings),
        )
    print(d2t(rep))
    return rep


def pyepics_test(cycles=10):
    print("pyepics test")
    timings = []
    
    def move(signal, dest, i=None, period=PERIOD_S):
        t0 = time.time()
        signal.put(dest, wait=True)
        t = time.time()-t0
        print(f"{i}  {dest} {signal.value}   {t:.5f}s")
        time.sleep(period)
        return t
    
    for i in range(cycles):
        timings.append(move(ef1, 1, i, PERIOD_S))
        timings.append(move(ef1, 0, i, PERIOD_S))

    return print_timings(timings)


def ophyd_test(cycles=10):
    print("ophyd test")
    timings = []
    
    def move(signal, dest, i=None, period=PERIOD_S):
        t0 = time.time()
        signal.put(dest, use_complete=True)
        t = time.time()-t0
        print(f"{i}  {dest} {signal.value}   {t:.5f}s")
        time.sleep(period)
        return t
    
    for i in range(cycles):
        timings.append(move(f1, 1, i, PERIOD_S))
        timings.append(move(f1, 0, i, PERIOD_S))
    
    return print_timings(timings)


def bluesky_test(cycles=10):
    global results
    print("bluesky test")
    RE = bluesky.RunEngine({})
    t = 0

    def move(signal, dest, i=None, period=PERIOD_S):
        global t
        global results
        t0 = time.time()
        yield from bluesky.plan_stubs.mv(signal, dest)
        t = time.time()-t0
        print(f"{i}  {dest} {signal.value}   {t:.5f}s")
        yield from bluesky.plan_stubs.sleep(period)
    
    def ping_pong(signal, v1=1, v2=-1, delay_s=PERIOD_S):
        global t
        global results
        timings = []
        for i in range(cycles):
            yield from move(signal, v1, i, delay_s)
            timings.append(t)
            yield from move(signal, v2, i, delay_s)
            timings.append(t)

        results = print_timings(timings)

    RE(ping_pong(f1, 1, 0))
    return results


def suite():
    results = dict(
        pyepics = pyepics_test(CYCLES),
        ophyd = ophyd_test(CYCLES),
        bluesky = bluesky_test(CYCLES),
    )

    table = pyRestTable.Table()
    table.labels = ["time to put(value)",]
    table.labels += "PyEpics ophyd bluesky/RunEngine".split()
    table.addRow((
        "version",
        epics.__version__,
        ophyd.__version__,
        bluesky.__version__,
        ))
    table.addRow((
        "# samples: put()",
        results["pyepics"]["length"],
        results["ophyd"]["length"],
        results["bluesky"]["length"],
        ))
    table.addRow((
        "longest, s",
        f'{results["pyepics"]["max"]*1000:.2f} ms',
        f'{results["ophyd"]["max"]*1000:.2f} ms',
        f'{results["bluesky"]["max"]*1000:.2f} ms',
        ))
    table.addRow((
        "average time, s",
        f'{results["pyepics"]["average"]*1000:.2f} ms',
        f'{results["ophyd"]["average"]*1000:.2f} ms',
        f'{results["bluesky"]["average"]*1000:.2f} ms',
        ))
    table.addRow((
        "standard deviation, s",
        f'{results["pyepics"]["st_dev"]*1000:.2f} ms',
        f'{results["ophyd"]["st_dev"]*1000:.2f} ms',
        f'{results["bluesky"]["st_dev"]*1000:.2f} ms',
        ))
    table.addRow((
        "shortest, s",
        f'{results["pyepics"]["min"]*1000:.2f} ms',
        f'{results["ophyd"]["min"]*1000:.2f} ms',
        f'{results["bluesky"]["min"]*1000:.2f} ms',
        ))
    print(table)
    return table


if __name__ == "__main__":
    memory = []
    for i in range(REPETITIONS):
        memory.append(suite())
    
    print("#"*80)
    print("\n".join(map(str, memory)))
