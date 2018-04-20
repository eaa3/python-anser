# Run the Anser EMT system on Windows & Linux

## Installation and Setup

### Windows
- Install the latest version of NI DAQmx for Windows (available [here](http://www.ni.com/download/ni-daqmx-17.6/7169/en/))
- Install the 64-bit edition of the Anaconda 3 Python distribution
- Once Anaconda is installed, install PyIGTLink, PySerial and PyDAQmx using the pip package manager
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
- *NOTE* You must rerun `UpdateNIDrivers` whenever the OS kernel is updated, otherwise the DAQ driver will not initialise
- Reboot the OS and run `lsdaq` with the DAQ plugged into the computer. The device should be recognised as `DevX` where X is the index of the device.

## Calibration for Anser EMT 7x7
- Run `python launcher.py --calibrate -d DevX` where `python` corresponds to the Anaconda3 environment and X is the DAQ identifier.
- Enter the identifier of the sensor you wish to calibrate i.e. 1, 2 etc.
- Connect the calibration probe lead to the corresponding port and place the probe on Point 1
- Press enter and follow the on-screen instructions
- After calibration you have the option to save the resulting calibration to file.

## Tracking for Anser EMT 7x7 (Sensor 1)
- Run `python launcher.py -d DevX -u 50 -l 2000 -s 1 -p` where `python` corresponds to the Anaconda3 environment and X is the DAQ identifier.
- The position of the sensor should be print on the commandline in real-time at ~50Hz
- Creating an OpenIGTLink client connection in  MITK/CustusX/3DSlicer will allow you to visualise the positions being resolved.
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