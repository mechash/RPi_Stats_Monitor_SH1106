# -------------------------------------------------------------------------------
# Python script to Monitor UP Time, IP Address, CPU Load, 
# Temperature, RAM Usage and Dist Utilization
#
# Copyright (C) 2021 Ashish Jaiswal, https://mechash.com.
# All rights reserved.
#
# This file is part of https://github.com/mechash/RPi_Stats_Monitor_SH1106.git,
# and is released under the "MIT License Agreement". Please see the LICENSE file
# that should have been included as part of this package.
# -------------------------------------------------------------------------------

#!/bin/bash
clear
cd ~/RPi_Stats_Monitor_SH1106
sleep 5
python3 stats.py 
