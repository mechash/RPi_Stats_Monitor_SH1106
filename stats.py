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

import os
import multiprocessing
import time
import psutil
import subprocess

from datetime import datetime
from PIL import ImageFont
from demo_opts import get_device
from luma.core.render import canvas
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106

# Setting up OLED Display 
serial = i2c( port = 1 , address = 0x3C )                              # Refer documentation to find the port and address for the connected OLED Display
device = sh1106( serial )                                              # Selecting the Display for our use case it is SH1106 based OLED Display 

REFRESH_INTERVAL = 0.1                                                 # Refresh or loop delay after the whole code is been executed is done 

Font_Pixelmix = ImageFont.truetype( 'pixelmix.ttf' , 8)                # Import the Font from the same directory if you need to change the font please copy 
                                                                       # new font to the same directory as the stats.py script is located and change the location 
                                                                       # including the extention of the font in the code [ImageFont.truetype('font_path_or_name', font_size)] 


def main():
    
    # Setting up the Drawing Parameters 

    # System Uptime
    min_Sys_H = 0
    max_Sys_H = 10
    min_Sys_W = 1
    max_Sys_W = 127

    # System IP Address
    min_IP_H = 10
    max_IP_H = 22
    min_IP_W = 0
    max_IP_W = 128

    # CPU and RAM Outline 
    min_CPU_RAM_H = 22
    max_CPU_RAM_H = 43
    min_CPU_RAM_W = 0
    max_CPU_RAM_W = 128

    # CPU Load
    min_CPU_Bar_H = 31
    max_CPU_Bar_H = 25
    min_CPU_Bar_W = 24
    max_CPU_Bar_W = 123

    CPU_Threshold = 3.5

    # CPU Temp
    max_Bar_Width = 128
    min_Bar_Width = 24

    # RAM
    min_Ram_H = 43
    max_Ram_H = 64
    min_Ram_W = 0
    max_Ram_W = 64

    # Disk Utilization
    min_Disk_H = 43 
    max_Disk_H = 64
    min_Disk_W = 64
    max_Disk_W = 128


    # Calculations and Feteching Data we need for Displaying on the OLED Display 
    # Such as System Up Time, Current IP Address, CPU Load, CPU Temperature
    # RAM Utilization and Disk Utilization

    # Getting system uptime
    sysUptime = datetime.now() - datetime.fromtimestamp( psutil.boot_time() )

    # Getting System IP Address
    cmd = "hostname -I | cut -d\  -f1"
    IP = subprocess.check_output( cmd , shell = True )

    # Getting CPU Load data 
    CPU_Load = os.getloadavg()
    CPU_Percent = CPU_Load[0] / multiprocessing.cpu_count() * 100
    CPU_Bar_Width_1 = ( ( ( 190 - CPU_Percent ) * ( min_CPU_Bar_W - max_CPU_Bar_W ) ) / 100 ) + max_CPU_Bar_W
    CPU_Bar_Width_2 = ( ( ( 110 - CPU_Percent ) * ( min_CPU_Bar_W - max_CPU_Bar_W ) ) / 100 ) + max_CPU_Bar_W
    # Getting CPU Temperature Data
    try:
        with open( "/sys/class/thermal/thermal_zone0/temp" , "r" ) as temp:
            Temp_Cel = float( temp.read()[:2] )
            Temp_Percent = ( Temp_Cel / 60 ) * 100
            Bar_Width = ( ( ( 30 - Temp_Percent ) * ( min_Bar_Width - max_Bar_Width ) ) / 100) + min_Bar_Width
            
    except:
        Temp_Cel = 0
        
    # Getting RAM Utilization Data
    RAM_Stat = psutil.virtual_memory()
    RAM_Tot = RAM_Stat.total >> 20
    RAM_Usd = RAM_Stat.used >> 20
    
    # Getting Disk Utilization Data
    cmd = "df -h | awk '$NF==\"/\"{printf \"%d / %dGB \", $3,$2}'"
    Disk = subprocess.check_output( cmd , shell = True )
    

    # Starting the canvas for the screen
    with canvas( device , dither = True ) as draw:
 
        # Drawing OLED Dislay (Outline)
        draw.rectangle( device.bounding_box , outline = "white" )

        # Drawing System Uptime (Outline and Text)
        draw.rectangle( ( min_Sys_W , min_Sys_H , max_Sys_W , max_Sys_H ) , fill = "White" )
        draw.text( ( min_Sys_W + 1 , min_Sys_H + 1 ) , "Up Time- " + str(sysUptime)[:7] , font = Font_Pixelmix , fill="Black")
        
        # Drawing IP Address (Outline and Text)
        draw.rectangle( ( min_IP_W , min_IP_H , max_IP_W , max_IP_H ) , outline = "White" )
        draw.text( ( min_IP_W + 3 , min_IP_H + 2) , "IP  " + str( IP,'utf-8' ) , font = Font_Pixelmix, fill = "White" ) 
        
        # Drawing CPU and RAM (Outline)
        draw.rectangle( ( min_CPU_RAM_W , min_CPU_RAM_H , max_CPU_RAM_W , max_CPU_RAM_H ) , outline = "White")
        
        # Drawing CPU usage (Bar and Text)
        if CPU_Load[0] > CPU_Threshold :
            draw.rectangle ( ( min_CPU_Bar_W , min_CPU_Bar_H , CPU_Bar_Width_1 , max_CPU_Bar_H ) , fill = "white" )
            draw.text( ( 3 , 24 ) , "CPU" , font = Font_Pixelmix , fill = "white" )
            draw.text( ( CPU_Bar_Width_1 + 4 , 24 ) , "{0:.2f}".format( CPU_Load[0] ) + "%" , font = Font_Pixelmix , fill = "White")
        else :
            draw.rectangle( ( min_CPU_Bar_W , min_CPU_Bar_H , CPU_Bar_Width_2 , max_CPU_Bar_H ) , fill = "white" )
            draw.text( ( 3 , 24 ) , "CPU" , font = Font_Pixelmix , fill = "white" )
            draw.text( ( CPU_Bar_Width_2 + 4 , 24 ) , "{0:.2f}".format( CPU_Load[0] ) + "%" , font = Font_Pixelmix, fill = "white" )
            
        # Drawing CPU Temperature (Bar and Text)   
        if Bar_Width > min_Bar_Width:
            draw.text( ( 3 , 33 ) , "TMP" , font = Font_Pixelmix , fill = "White" )
            draw.rectangle( ( 24 , 34 , Bar_Width , 40 ) , fill = "White" )
            draw.text( ( Bar_Width + 4 , 33 ) , str( Temp_Cel ) + " C" , font = Font_Pixelmix, fill = "White" )
       
        # Drawing RAM Utilization (Outline and Text)
        draw.rectangle( ( min_Ram_W , min_Ram_H , max_Ram_W , max_Ram_H ), outline = "white" )
        draw.text( ( 3 , 44 ) , "RAM " + str( RAM_Usd ) , font = Font_Pixelmix , fill = "White" )
        draw.text( ( 4 , 54 ) , "/ " + str( RAM_Tot ) + " MB" , font = Font_Pixelmix , fill = "White" )
        
        # Drawing Disk Utilization (Outline and Text)
        draw.rectangle( ( min_Disk_W , min_Disk_H , max_Disk_W , max_Disk_H ) , outline = "white" )
        draw.text( ( 68 , 44 ) , "SD CARD " , font = Font_Pixelmix , fill = "White" )
        draw.text( ( 68 , 54) , str( Disk , 'utf-8' ) , font = Font_Pixelmix , fill = "white" )


while True:
    main()
    time.sleep( REFRESH_INTERVAL )
