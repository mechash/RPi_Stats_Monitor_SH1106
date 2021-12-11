import os
import multiprocessing
import time
import psutil
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from demo_opts import get_device
from luma.core.render import canvas
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106

serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

REFRESH_INTERVAL = 0.1

blnk = 1
font = ImageFont.truetype('pixelmix.ttf', 8)

 

def main():
    # Importing some global vars
    global blnk
    
    cmd = "hostname -I | cut -d\  -f1"
    IP = subprocess.check_output(cmd, shell = True )
    cmd = "top -bn1 | grep load | awk '{printf \"CPU: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell = True )
    cmd = "free -m | awk 'NR==2{printf \"RAM: %s/\", $3 }'"
    MemUsage = subprocess.check_output(cmd, shell = True )
    cmd = "df -h | awk '$NF==\"/\"{printf \"%d / %dGB \", $3,$2}'"
    Disk = subprocess.check_output(cmd, shell = True )
    cmd = "vcgencmd measure_temp |cut -f 2 -d '='"
    temp = subprocess.check_output(cmd, shell = True )
    

    # Vars:
    # Getting system uptime
    sysUptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())

    # RAM bar
    minRamBarH = 30
    maxRamBarH = 34
    minRamBarW = 128
    maxRamBarW = 100
    ramStat = psutil.virtual_memory()
    ramTot = ramStat.total >> 20
    ramUsd = ramStat.used >> 20
    ramPerc = (ramUsd / ramTot) * 100
    ramBarWidth = (((100 - ramPerc) * (minRamBarW - maxRamBarW)) / 100) + maxRamBarW
    
    

    # Temp bar
    maxBarWidth = 128
    minBarWidth = 24
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp:
            tmpCel = float(temp.read()[:2])
            tmpPercent = (tmpCel / 60) * 100

            width = (((30 - tmpPercent) * ( minBarWidth - maxBarWidth)) / 100) + minBarWidth
    except:
        tmpCel = 0
        height = 0

    # CPU Parameters and data fetch
    cputhresh = 3.5
    minCpuBarH = 31
    maxCpuBarH = 25
    minCpuBarW = 24
    maxCpuBarW = 123
    cpuLoad = os.getloadavg()
    cpuPercent = cpuLoad[0] / multiprocessing.cpu_count() * 100
    

    # Starting the canvas for the screen
    with canvas(device, dither=True) as draw:
 

        # Main Outline
        draw.rectangle(device.bounding_box, outline="white")

       
        # System Uptime
        draw.rectangle((1, 0, 127, 10), fill="White")
        draw.text((2, 1), "Up Time- " + str(sysUptime)[:7], font=font, fill="black")
        
        #IP
        draw.text((3,12), "IP  " + str(IP,'utf-8'), font=font, fill="white")
        draw.rectangle((0, 10, 128, 22), outline="white")
        
        #CPU usage Bar
        if cpuLoad[0] > cputhresh:
            cpuBarWidth = (((190 - cpuPercent) * (minCpuBarW - maxCpuBarW)) / 100) + maxCpuBarW
            draw.rectangle((minCpuBarW, minCpuBarH, cpuBarWidth, maxCpuBarH), fill="white")
            draw.text((3,24),"CPU" , font=font, fill="white")
        #draw.rectangle((cpuBarWidth, 32, cpuBarWidth+100, 42 ), fill="white")cpuBarWidth
            draw.text((cpuBarWidth+4,24),"{0:.2f}".format(cpuLoad[0]) + "%", font=font, fill="white")
        else:
            cpuBarWidth = (((110 - cpuPercent) * (minCpuBarW - maxCpuBarW)) / 100) + maxCpuBarW
            draw.rectangle((minCpuBarW, minCpuBarH, cpuBarWidth, maxCpuBarH), fill="white")
            draw.text((3,24),"CPU" , font=font, fill="white")
        #draw.rectangle((cpuBarWidth, 32, cpuBarWidth+100, 42 ), fill="white")cpuBarWidth
            draw.text((cpuBarWidth+4,24),"{0:.2f}".format(cpuLoad[0]) + "%", font=font, fill="white")
             
        #Temp
        draw.rectangle((0, 22, 128, 43), outline="white")
        if width > minBarWidth:
            draw.text((3, 33 ), "TMP",font=font, fill="White")
            draw.rectangle((24, 34, width, 40) ,fill="White")
            draw.text((width+4, 33 ), str(tmpCel)+" C",font=font, fill="White")
       
        #RAM usage Bar
        draw.rectangle((0,43 , 64, 64), outline="white")
        draw.text((3,44 ),"RAM "+str(ramUsd),font=font, fill="White")
        draw.text((4,54 ),"/ " + str(ramTot)+" MB",font=font, fill="White")
        
        #Disk Utilization
        draw.text((68,44 ),"SD CARD ",font=font, fill="White")
        draw.rectangle((64,43 , 128, 64), outline="white")
        draw.text((68, 54), str(Disk,'utf-8'), font=font, fill="white")

        



while True:
    main()
    time.sleep(REFRESH_INTERVAL)
