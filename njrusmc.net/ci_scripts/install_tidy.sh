#!/bin/bash
# File:    install_tidy.sh
# Version: Bash 3.2.57(1)
# Author:  Nicholas Russo (http://njrusmc.net)
# Purpose: Pre-build CI stage check to install the 'tidy' HTML linting
#          utility on the Ubuntu CI runner.
#
# Tidy is not available through apt, so download the binary manually
curl -OL https://github.com/htacg/tidy-html5/releases/download/5.4.0/tidy-5.4.0-64bit.deb
#
# Perform SHA256 integrity check before installing
sum=b6b971534ee6bacc68a7c5f9878b0a146fbd7f50c580db76a19823e8541f92f8
echo $sum tidy-5.4.0-64bit.deb | sha256sum -c
#
# Install the package (apt is slow and requires updates, so avoid it)
#sudo dpkg -i tidy-5.4.0-64bit.deb
dpkg -i tidy-5.4.0-64bit.deb
#
# Test to ensure which was properly installed then delete the package
which tidy
tidy --version
rm -f tidy-5.4.0-64bit.deb
