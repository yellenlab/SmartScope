# Smart Scope

This repo contains code for tools for automated high throughput imaging using Windows or Ubuntu and Python 3. It was designed specifically for imaging with PVCAM.

# Windows 10 Install

## Prerequisites

Make sure that the following programs are installed:
* [PVCAM](https://www.photometrics.com/support/software/#software)
* [PVCAM-SDK](https://www.photometrics.com/support/software/#software)
* [Miniconda3](https://conda.io/en/latest/miniconda.html)
* [Nvidia Driver >= 410.48](https://www.nvidia.com/Download/index.aspx?lang=en-us)
* [Visual Studio 2017 Community Edition](https://www.techspot.com/downloads/6278-visual-studio.html)

NOTE: Visual Studio 2017 is required for a successful tensorflow-gpu 1.13 installation and building PyVCAM. In the VS installer, select all of the Windows packages when installing.

## Installing
Make a folder to store everything in, then using the Anaconda Prompt, change directories into that folder.

Clone the following repositiories
```
git clone https://github.com/yellenlab/SmartScope.git
git clone https://github.com/zfphil/micro-manager-python3.git
git clone https://github.com/Photometrics/PyVCAM.git
```

Create and activate the conda environment
```
conda env create -f SmartScope\environment.yml
conda activate smartscope
```

Install PyVCAM
```
setx PVCAM_SDK_PATH "C:\Program Files\Photometrics\PVCamSDK"
python PyVCAM\pyvcam_wrapper\setup.py install
```

Install Mirco-Manager 2.0

For now, this install only works with [this](https://valelab4.ucsf.edu/~MM/nightlyBuilds/2.0.0-beta/Windows/MMSetup_64bit_2.0.0-beta3_20171106.exe) exact build of Mirco-Manger. Install it normally, then copy the files from "micro-manager-python3\MMCorePy" into the "C:\Program Files\Micro-Manager-2.0beta" directory.

Download Machine Learing Models from [here](https://www.dropbox.com/sh/jipfb9xnwcw1ssc/AACJAwnoaR7FSGBTrAv3fdhba?dl=0), unzip and place all 4 files in "SmartScope\python\notebook" directory


## Connecting to Scope and Stage
* Open Mirco-Manger application
* Click Devices/Hardware Configuration Wizard...
* Create a new cfg file with hardware plugged in
* Name that file scope_stage.cfg and place it in SmartScope\config

## Image Chip
Run jupyter lab 
```
cd Smartscope\python\notebook
jupyter lab
```

Open run.ipynb and run the cells


*This open source software was developed with the generous support of a grant from the National Institutes of Health (1R21GM131279)*
