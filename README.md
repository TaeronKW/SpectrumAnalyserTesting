# SpectrumAnalyserTesting
Python code for testing the RFExplorer IoT module WSUB3G

This code uses the [RFExplorer Python Library.](https://github.com/RFExplorer/RFExplorer-for-Python) Version 1.33.2106.3 contains some errors that are corrected in my fork which is [here.](https://github.com/TaeronKW/RFExplorer-for-Python) If the errors get corrected in the original repo my fork becomes redundant and the original repo can be installed using the pip3 installer rather than the instructions below.

- Uninstall the existing pip3 library if necessary
  - `sudo pip3 uninstall RFExplorer`
- Clone the forked RFExplorer library into this project folder
  - `git clone https://github.com/TaeronKW/RFExplorer-for-Python.git`
- Create a link to the library
  - `ln -s RFExplorer-for-Python/RFExplorer/ RFExplorer`
- when running the python code, you must be super user for the raspberry pi to properly access IO. Use the -E switch to copy in environment variables if you want to use and plotting functions over ssh/X-term. For example:
  - `sudo -E python3 fullscan.py`

