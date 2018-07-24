#!/usr/bin/python

'''
PI-SPI-RDU Library
Modules Supported
VP_EC_RDU
VP-EC-RDU-MINI
'''

import RPi.GPIO as GPIO
import time
import sys
import serial

BAUD_RATE = 19200       # Default Baud Rate for RDU Displays            
TIME_OUT = 0.5            # Default Time Out for RDu Display to respond

DIR_RS485 = 25          # GPIO Pin used for RS485 Driver IC Direction Control (0=Rx, 1=Tx)
DIR_DELAY = 0.005       # Seconds Delay After Setting and Re-setting the Direction GPIO Pin

GPIO.setmode(GPIO.BCM)  # Use RPi GPIO numbers
GPIO.setwarnings(False) # disable warnings

GPIO.setup(DIR_RS485,GPIO.OUT)     # RS485 DIR bit
GPIO.output(DIR_RS485,0)           # Set RS485 to Read

# Status LED Definitions
OFF =   0x00
GREEN = 0x01
AMBER = 0x02
RED =   0x04

GREEN_SLOW = 0x11
AMBER_SLOW = 0x12
RED_SLOW =   0x14

GREEN_FAST = 0x21
AMBER_FAST = 0x22
RED_FAST =   0x24

# Audible 
AUDIBLE_ON = 1
AUDIBLE_OFF = 0

def write_rdu(modbus_id, line1, line2, line3, line4, led1, led2, audible):     # Send Display data to RDU via RS485
        tx_buf = [0] * 95
        if len(line1) > 20:                      # LCD line 1 has to be exaclty 20 characters
            line1 = line1[:20]
        if len(line1) < 20:
            for i in range(len(line1),20):
                line1 += " "

        if len(line2) > 20:                      # LCD line 2 has to be exaclty 20 characters
            line2 = line2[:20]
        if len(line2) < 20:
            for i in range(len(line2),20):
                line2 += " "

        if len(line3) > 20:                      # LCD line 3 has to be exaclty 20 characters
            line3 = line3[:20]
        if len(line3) < 20:
            for i in range(len(line3),20):
                line3 += " "

        if len(line4) > 20:                      # LCD line 4 has to be exaclty 20 characters
            line4 = line4[:20]
        if len(line4) < 20:
            for i in range(len(line4),20):
                line4 += " "
                         
        tx_buf[0] = modbus_id	        # Modbus ID
        tx_buf[1] = 16		        # Modbus Function 16 Write Multiple Holding Registers
        tx_buf[2] = 0
        tx_buf[3] = 0
        tx_buf[4] = 0
        tx_buf[5] = 43
        tx_buf[6] = 86

        for i in range(0, 20):
            tx_buf[7+i] = ord(line1[i])
            tx_buf[27+i] = ord(line2[i])
            tx_buf[47+i] = ord(line3[i])
            tx_buf[67+i] = ord(line4[i])
        
        tx_buf[87] = 0
        tx_buf[88] = led2
        tx_buf[89] = 0
        tx_buf[90] = led1
        tx_buf[91] = 0
        tx_buf[92] = audible

        checksum = _crc16(bytearray(tx_buf), 93)
        tx_buf[93] = (checksum & 0x00ff)
        tx_buf[94] = ((checksum >> 8) & 0xff)

        # Open Serial Port (ttyS0 used for RPI 3)
        rs485 = serial.Serial("/dev/ttyS0", baudrate=BAUD_RATE, timeout=TIME_OUT)

        GPIO.output(DIR_RS485,1)                # Set Direction Control to Tx
        time.sleep(DIR_DELAY)                   # 10 mSec delay to settle TX Line
        rs485.write(bytearray(tx_buf))
        time.sleep(DIR_DELAY*10)                 # 50 mSec Delay to allow last byte of Checksum and character delay
        GPIO.output(DIR_RS485,0)                # Set Direction Control to Rx

        read_bytes = 8                          # Expected return bytes
        rx_buf = rs485.read(read_bytes)         # read the bytes
        rs485.flushInput()                      # Flush the seriel Input buffer          
        rs485.close()                           # Close the port

        status = _check_receive_buffer(rx_buf, read_bytes)
        return status
        


def write_rdu_mini(modbus_id, line1, line2, line3, line4):     # Send Display data to RDU via RS485
        tx_buf = [0] * 95
        if len(line1) > 20:                      # LCD line 1 has to be exaclty 20 characters
            line1 = line1[:20]
        if len(line1) < 20:
            for i in range(len(line1),20):
                line1 += " "

        if len(line2) > 20:                      # LCD line 2 has to be exaclty 20 characters
            line2 = line2[:20]
        if len(line2) < 20:
            for i in range(len(line2),20):
                line2 += " "

        if len(line3) > 20:                      # LCD line 3 has to be exaclty 20 characters
            line3 = line3[:20]
        if len(line3) < 20:
            for i in range(len(line3),20):
                line3 += " "

        if len(line4) > 20:                      # LCD line 4 has to be exaclty 20 characters
            line4 = line4[:20]
        if len(line4) < 20:
            for i in range(len(line4),20):
                line4 += " "
                         
        tx_buf[0] = modbus_id	                # Modbus ID
        tx_buf[1] = 16		                # Modbus Function 16 Write Multiple Holding Registers
        tx_buf[2] = 0
        tx_buf[3] = 0
        tx_buf[4] = 0
        tx_buf[5] = 43
        tx_buf[6] = 86

        for i in range(0, 20):
            tx_buf[7+i] = ord(line1[i])
            tx_buf[27+i] = ord(line2[i])
            tx_buf[47+i] = ord(line3[i])
            tx_buf[67+i] = ord(line4[i])
        
        tx_buf[87] = 0
        tx_buf[88] = 0
        tx_buf[89] = 0
        tx_buf[90] = 0
        tx_buf[91] = 0
        tx_buf[92] = 0

        checksum = _crc16(bytearray(tx_buf), 93)
        tx_buf[93] = (checksum & 0x00ff)
        tx_buf[94] = ((checksum >> 8) & 0xff)
	
        # Open Serial Port (ttyS0 used for RPI 3)
        rs485 = serial.Serial("/dev/ttyS0", baudrate=BAUD_RATE, timeout=TIME_OUT)

        GPIO.output(DIR_RS485,1)                # Set Direction Control to Tx
        time.sleep(DIR_DELAY)                        # 10 mSec delay to settle TX Line
        rs485.write(bytearray(tx_buf))
        time.sleep(DIR_DELAY*10)                        # 50 mSec Delay to allow last byte of Checksum and character delay
        GPIO.output(DIR_RS485,0)                # Set Direction Control to Rx

        read_bytes = 8                          # Expected return bytes
        rx_buf = rs485.read(read_bytes)         # read the bytes
        rs485.flushInput()                      # Flush the seriel Input buffer          
        rs485.close()                           # Close the port

        status = _check_receive_buffer(rx_buf, read_bytes)

        return status

def read_temperature(modbus_id):
        status = [0] * 2
        tx_buf = [0] * 8
        
        tx_buf[0] = modbus_id	                # Modbus ID
        tx_buf[1] = 3		                # Modbus Function 3 Read Holding Registers
        tx_buf[2] = 0
        tx_buf[3] = 50                          # Address for Temperature
        tx_buf[4] = 0
        tx_buf[5] = 1                           # number of Registers to Read

        checksum = _crc16(bytearray(tx_buf), 6)
        tx_buf[6] = (checksum & 0x00ff)
        tx_buf[7] = ((checksum >> 8) & 0xff)
        
        # Open Serial Port (ttyS0 used for RPI 3)
        rs485 = serial.Serial("/dev/ttyS0", baudrate=BAUD_RATE, timeout=TIME_OUT)

        GPIO.output(DIR_RS485,1)                # Set Direction Control to Tx
        time.sleep(DIR_DELAY)                   # 10 mSec delay to settle TX Line
        rs485.write(bytearray(tx_buf))
        time.sleep(DIR_DELAY)                   # 50 mSec Delay to allow last byte of Checksum and character delay
        GPIO.output(DIR_RS485,0)                # Set Direction Control to Rx

        read_bytes = 7                          # Expected return bytes
        rx_buf = rs485.read(read_bytes)         # read the bytes
        rs485.flushInput()                      # Flush the seriel Input buffer          
        rs485.close()                           # Close the port

        status[0] = _check_receive_buffer(rx_buf, read_bytes)

        if status[0] == 0:                      # Temperature values in Deg C
                status[1] = (rx_buf[3] << 8) + rx_buf[4]
                
        return status

def read_pushbuttons(modbus_id):
        status = [0] * 2
        tx_buf = [0] * 8
        
        tx_buf[0] = modbus_id	                # Modbus ID
        tx_buf[1] = 3		                # Modbus Function 3 Read Holding Register
        tx_buf[2] = 0
        tx_buf[3] = 58                          # Address for Pushbutton Values
        tx_buf[4] = 0
        tx_buf[5] = 1                           # number of Registers to Read

        checksum = _crc16(bytearray(tx_buf), 6)
        tx_buf[6] = (checksum & 0x00ff)
        tx_buf[7] = ((checksum >> 8) & 0xff)
        
        # Open Serial Port (ttyS0 used for RPI 3)
        rs485 = serial.Serial("/dev/ttyS0", baudrate=BAUD_RATE, timeout=TIME_OUT)

        GPIO.output(DIR_RS485,1)                # Set Direction Control to Tx
        time.sleep(DIR_DELAY)                   # 10 mSec delay to settle TX Line
        rs485.write(bytearray(tx_buf))
        time.sleep(DIR_DELAY)                   # mSec Delay to allow last byte of Checksum and character delay
        GPIO.output(DIR_RS485,0)                # Set Direction Control to Rx

        read_bytes = 7                          # Expected return bytes
        rx_buf = rs485.read(read_bytes)         # read the bytes
        rs485.flushInput()                      # Flush the seriel Input buffer          
        rs485.close()                           # Close the port

        status[0] = _check_receive_buffer(rx_buf, read_bytes)

        if status[0] == 0:                      # Pushbutton Values 
                status[1] = (rx_buf[3] << 8) + rx_buf[4]
        
        return status


# Calculate CRC16 Checksum
def _crc16(data, no):
    crc = 0xffff
    poly = 0xa001               # Polynomial used for Modbus RS485 applications
    temp = no
    
    while True:
        crc ^= data[temp - no]        

        for i in range(0, 8):
            if crc & 0x0001:
                crc = (crc>>1) ^ poly
            else:
                crc >>= 1
                    
        no -= 1;

        if no == 0:
            break

    return crc & 0xffff                       


def _check_receive_buffer(rx_buf, read_bytes):        

        if len(rx_buf) == 5:                    # Check for "Exception" return from the Display
                return rx_buf[2]                # Returnt he exception value

        if len(rx_buf) != read_bytes:
                return -1                       # Return -1 as a Com Error
        
        if len(rx_buf) == read_bytes:
                # Verify Checksums
                checksum_calc = _crc16(bytearray(rx_buf), (read_bytes - 2))
                checksum_read = (rx_buf[read_bytes-1] << 8) + rx_buf[read_bytes-2]

                if checksum_calc != checksum_read:
                        return -2               # Checksum Error                

        return 0


def check_rs485_error(status):

        if status == -1:
            return "Com Error"

        if status == -2:
            return "Checksum Error"

        if status > 0:
            return "Modbus Exception Error "

        return
    

