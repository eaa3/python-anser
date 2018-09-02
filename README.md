# Anser Startup Guide

## Inventory

The following *components* are required for using the Anser EMT system.

Hardware:
- 1 x Anser EMT field generator
- 1 x Anser EMT base station
- 1 x Sensor calibration probe (Probably needed for every system)
- 1 x Barrel jack power supply 15V
- 1 x 3M centronics cable
- 2 x USB A-B cable

Software:
- 1 x Windows 7/8/10 PC
- 1 x National Instruments DAQmx driver

## Hardware Setup

- On your Windows PC install the *National Instruments DAQmx driver*. This can be found at [https://www.ni.com/](https://www.ni.com/).
- Place the Anser EMT field generator on a *metal-free surface.*
- Connect the base station to the field generator using the supplied *centronics cable*.
- Connect the *barrel jack power adapter* to the base station via the DC-IN port. The red standby LED located on the front panel of the unit should light up.
- Connect the Windows PC to the NI-DAQ port of the base station using the supplied *USB A-B cable*. Using a second *USB A-B cable* connect the Windows PC to the MCU port.
- Wait 10 seconds to let the driver install. The *NI Measurement and Automation explorer* provided with the driver should launch automatically, take note of the National Instruments device enumeration e.g. **DevX**. If this is the first time an National Instruments device has been connected to the PC then its enumerated name is Dev1.
- Power on the base station by pressing the *PWR button* at the rear of the unit. The green LED located on the front panel of the unit should light up.
- Connect a *sensor probe* to the first port on the front of the unit.

## Installation

### Windows
- Install the latest version of NI DAQmx for Windows (available [here](http://www.ni.com/download/ni-daqmx-17.6/7169/en/))
- Install the 64-bit edition of the Anaconda 3 Python distribution
- Once Anaconda is installed, install PyIGTLink, PySerial, PyDAQmx, rx, numpy, scipy, ruamel.yaml using the pip package manager
- The scripts should now run

### OS 10.X / Mac OS
- Install the latest version of NI DAQmx Base for Mac OS X (available [here](http://www.ni.com/download/ni-daqmx-base-15.0/5648/en/))
- Follow instructions as for Windows
### Linux (CentOS/Redhat)
- Install the latest version of NI DAQmx Base for Linux (available [here](http://www.ni.com/download/ni-daqmx-base-15.0/5644/en/))
- The installer may throw errors during installation due to a kernel compilation issue, follow the fix below
- Once the NI DAQmx Base installed, navigate to `/var/lib/nikal/<kernel_version>/nikal/nikal.c`
- Find the line containing the function definition `do_munmap(mm,addr,len);`
- Add 'NULL' as a 4th parameter to the function. It should now read `do_munmap(mm,addr,len,NULL);`
- Save the file (You will need to have root privilages to do this i.e. use `su ` or `sudo`).
- Run `UpdateNIDrivers` program in the `/bin` folder. The kernel drivers should compile successfully.
- If using a 64-bit OS you must install the following 32-bit dependencies:

`compat-libstdc++.i686
expat.i686
glibc.i686
glibc-devel.i686
libdrm.i686
libgcc.i686
libselinux.i686
libstdc++.i686
libX11.i686
libXau.i686
libxcb.i686
libXdamage.i686
libXext.i686
libXinerama.i686
libXfixes.i686
libXxf86vm.i686
mesa-dri-drivers.i686
mesa-libGL.i686
nss-softokn-freebl.i686
zlib.i686`
- More information about this issue can be found [here](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PASQSA4)
- *NOTE* You must rerun `UpdateNIDrivers` located in `/bin` whenever the OS kernel is updated, otherwise the DAQ driver will not initialise
- Reboot the OS and run `lsdaq` with the DAQ plugged into the computer. The device should be recognised as `DevX` where X is the index of the device.

## Setup

### Commands

Run `command.py -h` to see the list of available commands

|    Command                                        |                       Description                        |
|---------------------------------------------------|----------------------------------------------------------|
|  add *mysensor* [ --description, --dof]           | Creates a new sensor called 'mysensor'                   |
| remove *mysensor*                                 |Removes sensor 'mysensor'                                 |
| list [ --calibration]                             |Lists all available sensors                               |
| calibrate *mysensor* *1*                          |Performs calibration with 'mysensor' on port '1'.         |
|track *mysensor*, *mysensor2  1,2* [ --speed 1-4]  |   Track 'mysensor' on port '1', 'mysensor2' on port '2'  |

### Steps
#### 1. Configuration
Edit the configuration file **config_1.yaml**. Under ‘system’ change the ‘device_name’ to your **DevX** identifier [see Hardware Setup](##hardware-setup). Alternatively, you can add the [-d DevX] option when executing the following commands.
#### 2. Add Sensor
Create a 5-Dof sensor called 'mysensor'.
> `command.py add mysensor --description UCC --dof 5`

#### 3. Calibrate EMT System
Connect the sensor probe lead to the *Port 1*.
Fully insert the sensor probe into the field generator at *Point 1*.
Execute the following command, press enter follow and the on-screen instructions.
> `command.py calibrate mysensor 1`

#### 4. Tracking
To track and visualise the positions of *mysensor* in MITK/CustusX/3DSlicer, create an OpenIGTLink **client connection** in the software package.
Finally, execute the following command.
- *--igt* : creates a server and transfers positions via OpenIGTLInk
- *--speed*: there are four possible speeds (1 = most accurate, 4 = fastest).
- *--p*: prints sensor positions to the terminal in real-time.
> `command.py track mysensor 1 --speed 4 --igt -p`

## Cite this project
https://doi.org/10.1007/s11548-017-1568-7
## References
This software project uses the following open-source packages
SciPy: https://www.scipy.org
NumPy: https://www.numpy.org
PyDAQmx: https://pythonhosted.org/PyDAQmx/

[0]: http://www.ni.com/download/ni-daqmx-17.6/7169/en/
[1]: http://www.ni.com/download/ni-daqmx-base-15.0/5648/en/
[3]: http://www.ni.com/download/ni-daqmx-base-15.0/5644/en/