# building VM

1. download `linuxmint-19.2-mate-64bit.iso` from linuxmint.com
   1. visit https://linuxmint.com/release.php?id=35 for release 19.2
   2. choose *MATE (64-bit)*
   3. choose a download mirror
2. create VM in VirtualBox with these settings

    ```
    u: mintadmin
    p: mintadmin

    2 GB RAM
    40 GB storage (dynamic)
    2 CPU (core)
    32 MB video RAM
    NAT network adapter
    USB 2.0 enabled
    no shared folders
    autologin
    no file or disk encryption
    install VirtualBox Guest Additions
    enable bidirectional shared clipboard

    always run executable CD on insertion
    ```

3. install or ignore OS updates as you wish
4. `mkdir ~/bin` (`~.profile` should will add to `PATH` at **next Restart**)
5. `mkdir ~/Apps` for linux packages such as EPICS, VSCode, and miniconda
6. install Microsoft Visual Studio Code editor
   1. visit https://code.visualstudio.com/Download#
   2. download latest .tar.gz for linux 64-bit
   3. install locally
   
      ```
      cd ~/Apps`
      tar xzf ~/Downloads/code-stable-1576089840.tar.gz`
      mv VSCode-linux-x64{,-stable-1576089840}`
      ln -s VSCode-linux-x64-stable-1576089840 VSCode`
      cd ~/bin`
      ln -s ~/Apps/VSCode/bin/code ./`
      ```

7. install miniconda (64bit, Python 3.7) to `~/Apps/` and init to bash shell
   1. visit https://docs.conda.io/en/latest/miniconda.html
   2. `cd ~/Apps`
   3. `bash ~/Downloads/Miniconda3-latest-Linux-x86_64.sh`
   4. install to `/home/mintadmin/Apps/miniconda3`
   5. say *Yes* to add conda init to bash shell
   6. restart terminal session to see `(base) ` prefixed to command line
8. install and compile EPICS base (get command line tools)
   1. skip this step, we can use ophyd instead
9. install docker (via Software Manager: `docker.io` is the package)
   
   1. `sudo usermod -a -G docker $USER`
   2. Restart the VM to finish the docker install
   3. on restart, you should see any empty list from command `docker ps`

        ```
        (base) mintadmin@mint-19-2-vm:~$ docker ps
        CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
        ```

    4. instructions: https://github.com/prjemian/epics-docker/tree/master/n3_synApps#one-time-setup

        ```
        cd ~/bin`
        wget https://raw.githubusercontent.com/prjemian/epics-docker/master/n3_synApps/start_xxx.sh`
        wget https://raw.githubusercontent.com/prjemian/epics-docker/master/n3_synApps/remove_container.sh`
        chmod +x start_xxx.sh remove_container.sh`
        ```

10. start IOC sky (in docker)
    1. `start_xxx.sh sky`
    2. note: first time this is run, it downloads all container images from docker
    3. verify that IOC is running
       1. log into IOC's docker container and use caget from there

            ```
            (base) mintadmin@mint-19-2-vm:~/bin$ docker exec -it iocsky bash
            root@mint-19-2-vm:/opt/synApps/support# caget sky:UPTIME
            sky:UPTIME                     00:01:34
            root@mint-19-2-vm:/opt/synApps/support# exit
            exit
            ```

       2. verify docker container is running

            ```
            (base) mintadmin@mint-19-2-vm:~/Documents/bstesting$ docker ps
            CONTAINER ID        IMAGE                         COMMAND                  CREATED             STATUS              PORTS               NAMES
            258d818439cf        prjemian/synapps-6.1:latest   "bash -c 'while true…"   10 minutes ago      Up 10 minutes                           iocsky
            ```

11. git clone https://github.com/prjemian/bstesting

    ```
    cd ~/Documents
    git clone https://github.com/prjemian/bstesting
    ```
 
12. create bsmotor conda environment

    ```
    cd bstesting
    # show the command to use
    grep "conda create" README.md
    # copy from previous output and execute
    conda create -yn bsmotor bluesky ophyd databroker epics-base ipython -c nsls2forge
    conda activate bsmotor
    ```

13. run test3.py
    1.  `./test3.py`
    
        ```
        (bsmotor) mintadmin@mint-19-2-vm:~/Documents/bstesting$ ./test3.py 
        ping 1:  0.1 0.1                                                                                                                                                         
        pong 1:  -0.1 -0.1                                                                                                                                                       
        ping 2:  0.1 0.1                                                                                                                                                         
        pong 2:  -0.1 -0.1                                                                                                                                                       
        ping 3:  0.1 0.1                                                                                                                                                         
        m1: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 0.2/0.2 [00:00<00:00,  2.12s/degrees]
        ^C^C
        ```

        1. observe the motor stall during cycle 3 after the *ping* step
