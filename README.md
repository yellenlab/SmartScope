# Smart Scope

This repo contains code for tools for automated high throughput imaging using Ubuntu and Python 3. It was designed specifically for imaging with a PVCAM. 

This repo can be used through an included GUI or directly through python. 

## Getting Started

The installation process of this repo is very involved.

### Prerequisites

Make sure that the following programs are installed:
* PVCAM
* PVCAM-SDK
* [Miniconda3](https://conda.io/en/latest/miniconda.html)

The success of this install depends on the following projects:
* [Micro-Manager](https://github.com/micro-manager/micro-manager)
* [PyVCAM](https://github.com/Photometrics/PyVCAM#prerequisites)

## Installing
The followign process was used to set up the environment.

### PVCAM
Contact Qimaging and request downloads for pvcam and pvcam-sdk for linux. Once you have recieved these files, follow the included instructions to install both pvcam and pvcam-sdk.

Make sure that Anaconda or Miniconda is installed on system. Then create environment.yml (PyVCAM is already installed in this environment):
```
cd Smart_Scope
conda env create -f environment.yml
```

Verify that PyVCAM is working
 ```
 source activate Py36
 python
 
   >>> from pyvcam import pvc 
   >>> from pyvcam.camera import Camera   
   >>> 
   >>> pvc.init_pvcam()                   # Initialize PVCAM 
   >>> cam = next(Camera.detect_camera()) # Use generator to find first camera. 
   >>> cam.open()                         # Open the camera.
 ```

### Micro-Manager

Install build programs and libraries:

```
sudo apt-get install subversion build-essential autoconf automake libtool \
                     libboost-all-dev zlib1g-dev swig ant
```

Fetch Source Repositories
```
mkdir ~/mm
cd ~/mm
git clone https://github.com/micro-manager/micro-manager.git
svn co https://valelab4.ucsf.edu/svn/3rdpartypublic/
```

Since the 3rdpartypublic repository is so large, svn may return the following error: 

svn: REPORT de '/svn/3rdpartypublic/!svn/vcc/default': 
Could not read chunk delimiter: Secure connection truncated (https://valelab4.ucsf.edu)

This can be solved with:
```
svn cleanup 3rdpartypublic/
svn update 3rdpartypublic/ # This command might be executed several times
```

Genrate the configure script
```
cd ~/mm/micro-manager
./autogen.sh
```

Run the configure script, the PYTHON variable will have to change depending on the install location of miniconda or anaconda on specific machine. If you have miniconda3 installed in the home directory then the python paths should look like this. Replace \<USER\> with your username. 
```
PYTHON="/home/<USER>/miniconda3/envs/Py36/bin/python3" ./configure --prefix="/micro-manager/src/build" --with-python="/home/<USER>/miniconda3/envs/Py36/include/python3.6m"

```
Look at the output of the previous command and make sure that configure found our version of python and numpy without any problems. 

Install Mirco-Manger. The make process resulted in many errors the first few times that I ran it. I fixed these errors by searching shwat caused them and including more packages in the underlying c files that the errors refer to. These errors will hopefully be eliminated as new versions of Mirco-Manger are released. 
```
make
sudo make install
```

Add MMCorePy to the PYTHONPATH.
```
export PYTHONPATH="${PYTHONPATH}:/micro-manager/src/build/lib/micro-manager"
```

Once micro-manager is installed, you must allow it access to the usb ports.
```
sudo vi /etc/udev/rules.d/01-ttyusb.rules
```

Press 'i' to enter insert mode and then place  the following line in the file.
```
SUBSYSTEMS=="usb-serial", TAG+="uaccess"
```

Enter ':wq' then press ENTER to exit.  

Micro-Manager for Python 3 should be installed! verify that it is working.
```
python
   >>> import MMCorePy
   >>> mmc = MMCorePy.CMMCore()  # Instance micromanager core
   >>> mmc.getVersionInfo()

```
Additional instructions can be found [on micro-manager's website.](https://micro-manager.org/wiki/Linux_installation_from_source_(Ubuntu))

## Notes
Please remember that we have installed these resources onto Pyhton within a conda environment. Every time that you want to use this package, you must first run:
```
source activate Py36
```

## Useful Resources

The micro-manager API can be found [here](https://valelab4.ucsf.edu/~MM/doc/MMCore/html/class_c_m_m_core.html)

The PyVCAM API can be found [here](https://github.com/Photometrics/PyVCAM/blob/master/Documents/PyVCAM%20Wrapper.md)


