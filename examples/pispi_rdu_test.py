#!/usr/bin/python

import time
import sys
import pispi_rdu_lib as RDU

print ("Start Pi-SPI-RDU Test program")
print ("Press CTRL C to exit")

# RDU Status LED Options 

# OFF 
# GREEN 
# AMBER
# RED

# LED SLOW FLASH

# GREEN_SLOW 
# AMBER_SLOW 
# RED_SLOW 

# LED FAST FLASH

# GREEN_FAST
# AMBER_FAST
# RED_FAST

# Audible Options

# AUDIBLE_ON
# AUDIBLE_OFF

# RDU Commad Structure
# RDU.write_rdu(Modbus ID, LCD Line 1, LCD Line 2, LCD Line 3, LCD Line 4, Status LED 1 , Status LED 2, Audible )

# RDU Read Pushbuttons Values = 0 No Buttons Pressed
# ENTER = 1
# DOWN = 1
# UP = 4
# MENU = 8
# Combinations: UP + DOWN + ENTER = 7, Enter Program Mode, COM is stopped, will produce Com Errors
# ENTER + UP = 5
# ENTER + DOWN = 3
# UP + DOWN = 6

# COM Status
# -1 = COM Read Error
# -2 = Checksum Error
# 0 = OK, Valid Read or Write
# 1,2 or 3 = Exceptions where 1 = Invalid Function call, 2 = Invalid Address Range, 3 = Invalid Data Range

if __name__ == '__main__':
    try:

        Loop_Counter = 0        
        RDU_ID = 100       # Modbus ID
        
        while True:

            print( " ")

            # read_temperature returns value[0] = com status. value[1] = temperature * 100 in Deg C   
            temperature = RDU.read_temperature(RDU_ID)

            if temperature[0] == 0:     # verify temperature read is valid
                print("Temperature = %5.1f Deg C" % ((float)(temperature[1])/100)) # Temperature is scaled by 100
            else:
                print("Temp Read Error")
                
            # read_pushbuttons returns value[0] = com status. value[1] = pushbuttons pressed, no buttons = 0 (see above)    
            pushbuttons = RDU.read_pushbuttons(RDU_ID)

            if pushbuttons[0] == 0:     # verify pushbutton read is valid
                print("Pushbuttons = " , pushbuttons[1]) # Combined pushbuttons values
            else:
                print("Pushbutton Read Error")
                
            LCD_1 = ("PI-SPI RDU Test")
            LCD_2 = ("Temp = %5.1f Deg C" % ((float)(temperature[1])/100)) # Temperature is scaled by 100)
            LCD_3 = ("Buttons = %d" % pushbuttons[1])
            LCD_4 = ("Loop Counter = %d" % Loop_Counter  )

            status = RDU.write_rdu(RDU_ID, LCD_1, LCD_2, LCD_3, LCD_4, RDU.GREEN, RDU.GREEN, RDU.AUDIBLE_OFF)

            if status != 0:
                print("Error = " , RDU.check_rs485_error(status))

            # Program Loop Activity                    
            Loop_Counter += 1
            print( "Loop Counter = %d " % Loop_Counter)
            
            time.sleep(0.25)                  # Sleepy time   

            if(Loop_Counter > 100):
                Loop_Counter = 0
			
             
    except KeyboardInterrupt:   # Press CTRL C to exit Program
        sys.exit(0)
            
