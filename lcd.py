#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# HD44780 LCD Test Script for
# Raspberry Pi
#
# Author : Matt Hawkins
# Site   : http://www.raspberrypi-spy.co.uk
#
# Date   : 26/07/2012
#

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

#import
import socket
import fcntl
import struct
import RPi.GPIO as GPIO
import time

from time import gmtime, strftime
from datetime import datetime

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.00005
E_DELAY = 0.00005


def main():
    ''''''
  # Main program block
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)             # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT)    # E
    GPIO.setup(LCD_RS, GPIO.OUT)  # RS
    GPIO.setup(LCD_D4, GPIO.OUT)  # DB4
    GPIO.setup(LCD_D5, GPIO.OUT)  # DB5
    GPIO.setup(LCD_D6, GPIO.OUT)  # DB6
    GPIO.setup(LCD_D7, GPIO.OUT)  # DB7

    # Initialise display
    lcd_init()

    # Send some test
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("Rasbperry Pi")
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("Model B")

    time.sleep(3)  # 3 second delay
    # Send some text
    while True:
        for t in range(0, 5):
            lcd_byte(LCD_LINE_1, LCD_CMD)
            lcd_string(datetime.now().strftime("%Y-%m-%d"))
            lcd_byte(LCD_LINE_2, LCD_CMD)
            lcd_string(datetime.now().strftime("%H:%M:%S"))
            time.sleep(1)
        # TEMP
        tempC = int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3
        lcd_byte(LCD_LINE_1, LCD_CMD)
        lcd_string("Temperatura")
        lcd_byte(LCD_LINE_2, LCD_CMD)
        lcd_string(u'%.2f °C' % float(tempC))
        time.sleep(5)
        # IP
        lcd_byte(LCD_LINE_1, LCD_CMD)
        lcd_string("IP")
        lcd_byte(LCD_LINE_2, LCD_CMD)
        lcd_string(get_ip_address('eth0'))
        time.sleep(5)
        # MAC
        mac = getHwAddr('eth0')
        lcd_byte(LCD_LINE_1, LCD_CMD)
        lcd_string(mac[:8])
        lcd_byte(LCD_LINE_2, LCD_CMD)
        lcd_string(mac[9:])
        time.sleep(5)
        # DNS
        dns = getDNS()
        lcd_byte(LCD_LINE_1, LCD_CMD)
        lcd_string(dns[0])
        lcd_byte(LCD_LINE_2, LCD_CMD)
        lcd_string(dns[1])
        time.sleep(5)

    time.sleep(20)


def lcd_init():
    ''''''
    # Initialise display
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)


def lcd_string(message):
    ''''''
    # Send string to display

    message = message.ljust(LCD_WIDTH, " ")

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)


def lcd_byte(bits, mode):
    ''''''
    # Send byte to data pins
    # bits = data
    # mode = True    for character
    #                False for command

    GPIO.output(LCD_RS, mode)  # RS

    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)

    if bits&0x10 == 0x10:
        GPIO.output(LCD_D4, True)

    if bits&0x20 == 0x20:
        GPIO.output(LCD_D5, True)

    if bits&0x40 == 0x40:
        GPIO.output(LCD_D6, True)

    if bits&0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)

    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)

    if bits&0x01 == 0x01:
        GPIO.output(LCD_D4, True)

    if bits&0x02 == 0x02:
        GPIO.output(LCD_D5, True)

    if bits&0x04 == 0x04:
        GPIO.output(LCD_D6, True)

    if bits&0x08 == 0x08:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)


def get_ip_address(ifname):
    '''Recupera la direccion ip de la placa dada'''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,    # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
        )[20:24])


def getHwAddr(ifname):
    '''Recupera la macaddress de la placa dada'''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,
        struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]


def getDNS():
    '''recupera los dns del resolv.conf'''
    f = open('/etc/resolv.conf').readlines()

    for x in range(0, len(f)):
        f[x] = f[x].replace('nameserver ', '').replace('\n', '')

    return f


if __name__ == '__main__':
    main()
