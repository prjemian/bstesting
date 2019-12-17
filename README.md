# bstesting
examine and test internal aspects of ophyd.EpicsMotor support

See:

* https://github.com/bluesky/ophyd/pull/783
* https://github.com/bluesky/ophyd/issue/782

## conda environment

    conda create -yn bsmotor bluesky ophyd databroker epics-base ipython -c nsls2forge

This results in these installed packages from `nsls2forge` channel:

    (bsmotor) mintadmin@mint-vm:~/.../eclipse/bstesting$ conda list | grep nsls
    asteval                   0.9.14             pyh5ca1d4c_0    nsls2forge
    attrs                     19.1.0                     py_0    nsls2forge
    bluesky                   1.6.0rc3                   py_0    nsls2forge
    boltons                   19.1.0                     py_0    nsls2forge
    databroker                1.0.0b4                    py_0    nsls2forge
    doct                      1.0.5                      py_0    nsls2forge
    epics-base                3.15.6               he1b5a44_0    nsls2forge
    event-model               1.13.0b4                   py_0    nsls2forge
    historydict               1.2.3                      py_0    nsls2forge
    lmfit                     0.9.13                     py_1    nsls2forge
    mongoquery                1.1.0                      py_0    nsls2forge
    ophyd                     1.4.0rc3                   py_0    nsls2forge
    pims                      0.4.1                      py_0    nsls2forge
    prettytable               0.7.2                      py_0    nsls2forge
    pyepics                   3.4.0                    py37_0    nsls2forge
    slicerator                1.0.0                      py_0    nsls2forge
    suitcase-mongo            0.1.1                      py_0    nsls2forge
    suitcase-msgpack          0.2.4                      py_0    nsls2forge
    suitcase-utils            0.5.0                      py_2    nsls2forge
    super_state_machine       2.0.2                      py_0    nsls2forge
    tifffile                  0.15.1           py37hc1659b7_1    nsls2forge
    uncertainties             3.1.2                      py_0    nsls2forge
