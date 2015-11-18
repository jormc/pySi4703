import cmd
class si4703(object):
    
    import smbus
    i2c = smbus.SMBus(1)
    
    def __init__(self):
        print " "
        print "[init] Initializing si4703 class"
        
    def init(self):
        from time import sleep
        import RPi.GPIO as GPIO
        
        GPIO.setwarnings(False)
        
        GPIO.setmode(GPIO.BCM)      ## We will use board numbering instead of pin numbering. 
        GPIO.setup(23, GPIO.OUT)    ## RST
        GPIO.setup(0, GPIO.OUT)     ## SDA
        
        print "[init] Setting up RST on GPIO pin 23"
        print "[init] Setting up SDA on GPIO pin 0"

        GPIO.output(0, GPIO.LOW)    ## This block of code puts the Si4703 into 2-wire mode per instructions on page 7  of AN230
        sleep(.1)                   ## Actually, I'm not sure how this block of code works. According to the aforementioned page 7, it shouldn't
        GPIO.output(23, GPIO.LOW)   ## But I ripped this code off somewhere else, so I'm not gonna bash it. Great work to the OP
        sleep(.1)
        GPIO.output(23, GPIO.HIGH)
        sleep(0.5)
        
        # Get si4703 registry values
        si4703.updateLocalRegistry(self)
        
        # Start power sequence
        print "[init] Starting power up sequence..."
        si4703.TEST_1.POWER_SEQUENCE = True
        si4703.writeRegistry(self)
        si4703.TEST_1.POWER_SEQUENCE = False
        sleep(1)
        
        # Mute module
        print "[init] Mutting..."
        si4703.POWER_CONFIG.DMUTE = 1
        si4703.POWER_CONFIG.ENABLE = 1
        si4703.writeRegistry(self)
        sleep(1)
        
        # Set initial volume at 10
        print "[init] Setting volume = 10"
        si4703.SYS_CONFIG_2.VOLUME = 1
        si4703.writeRegistry(self)
        sleep(0.1)
        
        # Setting initial channel
        print "[init] Setting initial channel at 98.7MHz"
        initialChannel = float( 105.7 )
        si4703.CHANNEL.CHAN = int(((float( initialChannel*100 ))-8750)/20)
        si4703.writeRegistry(self)
        sleep(0.1)
        
        # Tunning the initial channel
        print "[init] Tunning at 98.7MHz..."
        si4703.CHANNEL.TUNE = 1
        si4703.writeRegistry(self)
        
        # Wait for tune...
        while si4703.STATUS_RSSI.STC == 0:
            sleep(0.1)
            si4703.updateLocalRegistry(self)
        si4703.CHANNEL.TUNE = 0
        si4703.writeRegistry(self)
        print "[init] Channel 98.7MHz tunned!"
        
        print "[init] Initialization ended!"
        
        si4703.getRdsData(self)
        
    def updateLocalRegistry(self):
        
        rawData = []
        
        cmd =   str(si4703.POWER_CONFIG.DSMUTE) + str(si4703.POWER_CONFIG.DMUTE) + str(si4703.POWER_CONFIG.MONO) + "0" + str(si4703.POWER_CONFIG.RDSM) + str(si4703.POWER_CONFIG.SKMODE) + str(si4703.POWER_CONFIG.SEEKUP) + str(si4703.POWER_CONFIG.SEEK)
        print "[updateLocalRegistry] str(cmd) = %s" % cmd
        
        cmd = int(cmd, 2)
        print "[updateLocalRegistry] int(cmd) = %d" % cmd
        
        try:
            rawData = si4703.i2c.read_i2c_block_data(0x10,cmd,32)
            print "[updateLocalRegistry] rawData = ", rawData
        except:
            print "Exception in method 'updateLocalRegistry' while trying to read from si4703"
            
        # Reorders the entire registry
        reorderedRegistry = si4703.convertRegisterReadings(self, rawData, 1)
        print "[updateLocalRegistry] reorderedRegistry = ", reorderedRegistry
        
        currentReg = []
        
        ## DEVICE_ID                    #0x00
        currentReg = reorderedRegistry[0]
        si4703.DEVICE_ID.PN = si4703.getRegisterValue(self, currentReg, 0, 4)
        si4703.DEVICE_ID.MFGID = si4703.getRegisterValue(self, currentReg, 4, 12)
        
        ## CHIP_ID                      #0x01
        currentReg = reorderedRegistry[1]
        si4703.CHIP_ID.REV = si4703.getRegisterValue(self, currentReg, 0, 6)
        si4703.CHIP_ID.DEV = si4703.getRegisterValue(self, currentReg, 6, 4)
        si4703.CHIP_ID.FIRMWARE = si4703.getRegisterValue(self, currentReg, 10, 6)
        
        ## POWER_CONFIG                 #0x02
        currentReg = reorderedRegistry[2]
        si4703.POWER_CONFIG.DSMUTE = si4703.getRegisterValue(self, currentReg, 0, 1)
        si4703.POWER_CONFIG.DMUTE = si4703.getRegisterValue(self, currentReg, 1, 1)
        si4703.POWER_CONFIG.MONO = si4703.getRegisterValue(self, currentReg, 2, 1)
        ##si4703.POWER_CONFIG.UNUSED = si4703.getRegisterValue(self, currentReg, 3, 1)
        si4703.POWER_CONFIG.RDSM = si4703.getRegisterValue(self, currentReg, 4, 1)
        si4703.POWER_CONFIG.SKMODE = si4703.getRegisterValue(self, currentReg, 5, 1)
        si4703.POWER_CONFIG.SEEKUP = si4703.getRegisterValue(self, currentReg, 6, 1)
        si4703.POWER_CONFIG.SEEK = si4703.getRegisterValue(self, currentReg, 7, 1)
        ##si4703.POWER_CONFIG.UNUSED = si4703.getRegisterValue(self, currentReg, 8, 1)
        si4703.POWER_CONFIG.DISABLE = si4703.getRegisterValue(self, currentReg, 9, 1)
        ##si4703.POWER_CONFIG.UNUSED = si4703.getRegisterValue(self, currentReg, 10, 1)
        ##si4703.POWER_CONFIG.UNUSED = si4703.getRegisterValue(self, currentReg, 11, 1)
        ##si4703.POWER_CONFIG.UNUSED = si4703.getRegisterValue(self, currentReg, 12, 1)
        ##si4703.POWER_CONFIG.UNUSED = si4703.getRegisterValue(self, currentReg, 13, 1)
        ##si4703.POWER_CONFIG.UNUSED = si4703.getRegisterValue(self, currentReg, 14, 1)
        si4703.POWER_CONFIG.ENABLE = si4703.getRegisterValue(self, currentReg, 15, 1)
        
        ## CHANNEL                      #0x03
        currentReg = reorderedRegistry[3]
        si4703.CHANNEL.TUNE = si4703.getRegisterValue(self, currentReg, 0, 1)
        ##si4703.CHANNEL.UNUSED = si4703.getRegisterValue(self, currentReg, 1, 1)
        ##si4703.CHANNEL.UNUSED = si4703.getRegisterValue(self, currentReg, 2, 1)
        ##si4703.CHANNEL.UNUSED = si4703.getRegisterValue(self, currentReg, 3, 1)
        ##si4703.CHANNEL.UNUSED = si4703.getRegisterValue(self, currentReg, 4, 1)
        ##si4703.CHANNEL.UNUSED = si4703.getRegisterValue(self, currentReg, 5, 1)
        si4703.CHANNEL.CHAN = si4703.getRegisterValue(self, currentReg, 6, 10)
        
        ## SYS_CONFIG_1                 0x04
        currentReg = reorderedRegistry[4]
        si4703.SYS_CONFIG_1.RDSIEN = si4703.getRegisterValue(self, currentReg, 0, 1)
        si4703.SYS_CONFIG_1.STCIEN = si4703.getRegisterValue(self, currentReg, 1, 1)
        ##si4703.SYS_CONFIG_1.UNUSED = si4703.getRegisterValue(self, currentReg, 2, 1)
        si4703.SYS_CONFIG_1.RDS = si4703.getRegisterValue(self, currentReg, 3, 1)
        si4703.SYS_CONFIG_1.DE = si4703.getRegisterValue(self, currentReg, 4, 1)
        si4703.SYS_CONFIG_1.AGCD = si4703.getRegisterValue(self, currentReg, 5, 1)
        ##si4703.SYS_CONFIG_1.UNUSED = si4703.getRegisterValue(self, currentReg, 6, 1)
        ##si4703.SYS_CONFIG_1.UNUSED = si4703.getRegisterValue(self, currentReg, 7, 1)
        si4703.SYS_CONFIG_1.BLNDADJ = si4703.getRegisterValue(self, currentReg, 8, 2)
        si4703.SYS_CONFIG_1.GPIO3 = si4703.getRegisterValue(self, currentReg, 10, 2)
        si4703.SYS_CONFIG_1.GPIO2 = si4703.getRegisterValue(self, currentReg, 12, 2)
        si4703.SYS_CONFIG_1.GPIO1 = si4703.getRegisterValue(self, currentReg, 14, 2)
        
        ## SYS_CONFIG_2                 0x05
        currentReg = reorderedRegistry[5]
        si4703.SYS_CONFIG_2.SEEKTH = si4703.getRegisterValue(self, currentReg, 0, 8)
        si4703.SYS_CONFIG_2.BAND = si4703.getRegisterValue(self, currentReg, 8, 2)
        si4703.SYS_CONFIG_2.SPACE = si4703.getRegisterValue(self, currentReg, 10, 2)
        si4703.SYS_CONFIG_2.VOLUME = si4703.getRegisterValue(self, currentReg, 12, 4)

        ## SYS_CONFIG_3                 0x06
        currentReg = reorderedRegistry[6]
        si4703.SYS_CONFIG_3.SMUTER = si4703.getRegisterValue(self, currentReg, 0, 2)
        si4703.SYS_CONFIG_3.SMUTEA = si4703.getRegisterValue(self, currentReg, 2, 2)
        ##si4703.SYS_CONFIG_3.UNUSED = si4703.getRegisterValue(self, currentReg, 4, 1)
        ##si4703.SYS_CONFIG_3.UNUSED = si4703.getRegisterValue(self, currentReg, 5, 1)
        ##si4703.SYS_CONFIG_3.UNUSED = si4703.getRegisterValue(self, currentReg, 6, 1)
        si4703.SYS_CONFIG_3.VOLEXT = si4703.getRegisterValue(self, currentReg, 7, 1)
        si4703.SYS_CONFIG_3.SKSNR = si4703.getRegisterValue(self, currentReg, 8, 4)
        si4703.SYS_CONFIG_3.SKCNT = si4703.getRegisterValue(self, currentReg, 12, 4)
        
        ## TEST_1                       0x07
        currentReg = reorderedRegistry[7]
        si4703.TEST_1.XOSCEN = si4703.getRegisterValue(self, currentReg, 0, 1)
        si4703.TEST_1.AHIZEN = si4703.getRegisterValue(self, currentReg, 1, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 2, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 3, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 4, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 5, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 6, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 7, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 8, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 9, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 10, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 11, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 12, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 13, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 14, 1)
        ##si4703.TEST_1.UNUSED = si4703.getRegisterValue(self, currentReg, 15, 1)

        ## TEST_2                       0x08        ALL BITS UNUSED
        currentReg = reorderedRegistry[8]
        ##si4703.TEST_2.UNUSED = si4703.getRegisterValue(self, currentReg, 0, 16)

        ## BOOT_CONFIG                  0x09        ALL BITS UNUSED
        currentReg = reorderedRegistry[9]
        ##si4703.BOOT_CONFIG.UNUSED = si4703.getRegisterValue(self, currentReg, 0, 16)

        ## STATUS_RSSI                  0x0A
        currentReg = reorderedRegistry[10]
        si4703.STATUS_RSSI.RDSR = si4703.getRegisterValue(self, currentReg, 0, 1)
        si4703.STATUS_RSSI.STC = si4703.getRegisterValue(self, currentReg, 1, 1)
        si4703.STATUS_RSSI.SFBL = si4703.getRegisterValue(self, currentReg, 2, 1)
        si4703.STATUS_RSSI.AFCRL = si4703.getRegisterValue(self, currentReg, 3, 1)
        si4703.STATUS_RSSI.RDSS = si4703.getRegisterValue(self, currentReg, 4, 1)
        si4703.STATUS_RSSI.BLER_A = si4703.getRegisterValue(self, currentReg, 5, 2)
        si4703.STATUS_RSSI.ST = si4703.getRegisterValue(self, currentReg, 7, 1)
        si4703.STATUS_RSSI.RSS = si4703.getRegisterValue(self, currentReg, 8, 8)

        ## READ_CHAN                    0x0B
        currentReg = reorderedRegistry[11]
        si4703.READ_CHAN.BLER_B = si4703.getRegisterValue(self, currentReg, 0, 2)
        si4703.READ_CHAN.BLER_C = si4703.getRegisterValue(self, currentReg, 2, 2)
        si4703.READ_CHAN.BLER_D = si4703.getRegisterValue(self, currentReg, 4, 2)
        si4703.READ_CHAN.READ_CHAN = si4703.getRegisterValue(self, currentReg, 6, 10)

        ## RDS_A                        0x0C
        currentReg = reorderedRegistry[12]
        si4703.RDS_A.RDS_A = si4703.getRegisterValue(self, currentReg, 0, 16)

        ## RDS_B                        0x0D
        currentReg = reorderedRegistry[13]
        si4703.RDS_B.RDS_B = si4703.getRegisterValue(self, currentReg, 0, 16)

        ## RDS_C                        0x0E
        currentReg = reorderedRegistry[14]
        si4703.RDS_C.RDS_C = si4703.getRegisterValue(self, currentReg, 0, 16)

        ## RDS_D                        0x0F
        currentReg = reorderedRegistry[15]
        si4703.RDS_D.RDS_D = si4703.getRegisterValue(self, currentReg, 0, 16)
        
        # si4703.printRegistry(self)
        
    def convertRegisterReadings (self, oldRegistry, reorder):
        '''
        (list, int) ->>> list
        When Python reads  the registry of the si4703 it places all 16 registers into a 32 item list (each item being a single byte). 
        This functioon gives each register its own item.
        The register at index 0 is 0x0A. If reorder is set to 1, then index 0 will be 0x00. 
        '''
        i = 0
        response = []
        while i <=31:
            firstByte = str(bin(oldRegistry[i]))
            secondByte = str(bin(oldRegistry[i+1]))
            
            firstByte = firstByte.replace("0b", "", 1)
            secondByte = secondByte.replace("0b", "", 1)

            while len(firstByte) < 8:
                firstByte = "0" + firstByte
            while len(secondByte) < 8:
                secondByte = "0" + secondByte
                
            fullRegister = firstByte + secondByte
            fullRegister = int(fullRegister, 2)
            
            response.append(fullRegister)
            i += 2
            
        if reorder == 1:
            response = si4703.reorderRegisters(self, response)

        return response
    
    def reorderRegisters (self, sixteenItemList):
        '''
        Since the si4703 starts reading at register 0x0A and wraps back around at 0x0F, the data can be hard to understand.
        This re-orders the data such that the first itme in the list is 0x00, the second item is 0x01.....twelfth item is 0x0C
        '''
        original = sixteenItemList
        response = []

        ##The item at index 6  is register 0x00
        response.append(original[6])    #0x00
        response.append(original[7])    #0x01
        response.append(original[8])    #0x02
        response.append(original[9])    #0x03
        response.append(original[10])   #0x04
        response.append(original[11])   #0x05
        response.append(original[12])   #0x06
        response.append(original[13])   #0x07
        response.append(original[14])   #0x08
        response.append(original[15])   #0x09
        response.append(original[0])    #0x0A
        response.append(original[1])    #0x0B
        response.append(original[2])    #0x0C
        response.append(original[3])    #0x0D
        response.append(original[4])    #0x0E
        response.append(original[5])    #0x0F

        return response
    
    def getRegisterValue(self, register, begin, length):
        '''
        This class continually has to copy the contents of the Si4703's registers to the Pi's internal memory. This function helps parse the data from the Si4703.
        In order to parse the data, we need the raw data, along with the location of a property and its length in bits (ie READCHAN's location would be index 6 and its length would be 9 bits)

        Internally, Python converts any hex, octal, or binary number into an integer for storage. This is why the register is represented as an integer at first. We then convert it to a string of nothing but 1s and 0s, and add extra zeros until it is 16 bits long.
        After doing this, we can use the location and length information to return the value of a property.
        '''
        intRegister = register                         ##give this a friendlier name
        strRegister = str(bin(intRegister))            ##Convert the register to a string (ie 15 becomes "0b1111") 
        strRegister = strRegister.replace("0b", "")    ##Get rid of the "0b" prefix (ie 15 would now become "1111") 
        while len(strRegister) < 16:                   ##We want the output to be 16 bits long 
            strRegister = "0" + strRegister            ##Add preceeding zeros until it IS 16 characters long
        response = strRegister[begin : begin + length] ##Weed out all the bits we don't need
        response = int(response, 2)                    ##Convert it back to an assignable integer
        
        return response
    
    def writeRegistry(self):
        '''
        Refreshes the registers on the device with the ones stored in local memory on the Pi.
        It will only refresh the registers 0x02-07, as all other registers cannot be written to
        '''
        mainList = []
        crazyFirstNumber = 0
        
        firstByte = 0
        secondByte = 0

        ## POWER_CONFIG                 #0x02
        firstByte = str(si4703.POWER_CONFIG.DSMUTE) + str(si4703.POWER_CONFIG.DMUTE) + str(si4703.POWER_CONFIG.MONO) + "0" + str(si4703.POWER_CONFIG.RDSM) + str(si4703.POWER_CONFIG.SKMODE) + str(si4703.POWER_CONFIG.SEEKUP) + str(si4703.POWER_CONFIG.SEEK)
        secondByte = "0" + str(si4703.POWER_CONFIG.DISABLE) + "00000" + str(si4703.POWER_CONFIG.ENABLE)
        firstByte = int(firstByte, 2)
        crazyFirstNumber = firstByte
        secondByte = int(secondByte, 2)
        mainList.append(secondByte)

        ## CHANNEL                      #0x03
        firstByte = str(si4703.CHANNEL.TUNE) + "0000000"
        secondByte =si4703.returnWithPadding(self, si4703.CHANNEL.CHAN, 10)
        firstByte = int(firstByte, 2)
        secondByte = int(secondByte, 2)
        mainList.append(firstByte)
        mainList.append(secondByte)

        ## SYS_CONFIG_1                 0x04
        firstByte = str(si4703.SYS_CONFIG_1.RDSIEN) + str(si4703.SYS_CONFIG_1.STCIEN) + "0" + str(si4703.SYS_CONFIG_1.RDS) + str(si4703.SYS_CONFIG_1.DE) + str(si4703.SYS_CONFIG_1.AGCD) + "00"
        secondByte = si4703.returnWithPadding(self, si4703.SYS_CONFIG_1.BLNDADJ, 2) + si4703.returnWithPadding(self, si4703.SYS_CONFIG_1.GPIO3, 2) + si4703.returnWithPadding(self, si4703.SYS_CONFIG_1.GPIO2, 2) + si4703.returnWithPadding(self, si4703.SYS_CONFIG_1.GPIO1, 2)
        firstByte = int(firstByte, 2)
        secondByte = int(secondByte, 2)
        mainList.append(firstByte)
        mainList.append(secondByte)

        ## SYS_CONFIG_2                 0x05
        firstByte = si4703.returnWithPadding(self, si4703.SYS_CONFIG_2.SEEKTH, 8)
        secondByte = si4703.returnWithPadding(self, si4703.SYS_CONFIG_2.BAND, 2) + si4703.returnWithPadding(self, si4703.SYS_CONFIG_2.SPACE, 2) + si4703.returnWithPadding(self, si4703.SYS_CONFIG_2.VOLUME, 4)
        firstByte = int(firstByte, 2)
        secondByte = int(secondByte, 2)
        mainList.append(firstByte)
        mainList.append(secondByte)

        ## SYS_CONFIG_3                 0x06
        firstByte = si4703.returnWithPadding(self, si4703.SYS_CONFIG_3.SMUTER, 2) + si4703.returnWithPadding(self, si4703.SYS_CONFIG_3.SMUTEA, 2) + "000" + str(si4703.SYS_CONFIG_3.VOLEXT)
        secondByte = si4703.returnWithPadding(self, si4703.SYS_CONFIG_3.SKSNR, 4) + si4703.returnWithPadding(self, si4703.SYS_CONFIG_3.SKCNT, 4)
        firstByte = int(firstByte, 2)
        secondByte = int(secondByte, 2)
        mainList.append(firstByte)
        mainList.append(secondByte)
        
        ## TEST_1                       0x07
        if si4703.TEST_1.POWER_SEQUENCE == 55:   ##Since all but the first two bits in this register are unused, and we only write to this to power up/down the device, it seems unessary to write this registry every time. Especially considering that writing 0 to the remaining register while in operation can prove fatal
            firstByte = str(si4703.TEST_1.XOSCEN) + str(si4703.TEST_1.AHIZEN) + si4703.returnWithPadding(self, si4703.TEST_1.RESERVED_FIRST_BYTE, 4)
            secondByte = si4703.returnWithPadding(self, si4703.TEST_1.RESERVED_SECOND_BYTE, 8)
            firstByte = int(firstByte, 2)
            secondByte = int(secondByte, 2)
            mainList.append(firstByte)
            mainList.append(secondByte)
        if si4703.TEST_1.POWER_SEQUENCE == True:##debug code for TEST_1. remove after debugging
            mainList.append(129) 

        print "[writeRegistry] mainList: ", mainList
        print "[writeRegistry] crazyFirstNumber: ", crazyFirstNumber
        
        w6 = si4703.i2c.write_i2c_block_data(0x10, crazyFirstNumber, mainList)
        si4703.updateLocalRegistry(self)

    def returnWithPadding (self, itemAsInteger, length):
        itemAsInteger = str(bin(itemAsInteger))
        itemAsInteger = itemAsInteger.replace("0b", "")

        while len(itemAsInteger) < length:
            itemAsInteger = "0" + itemAsInteger

        return itemAsInteger
    
    def printRegistry(self):
        print "[printRegistry]\n"
        
        print"\tDEVICE_ID: 0x00"
        print"\t\t", "PN:", si4703.DEVICE_ID.PN
        print"\t\t", "MFGID:", si4703.DEVICE_ID.MFGID
        
        print"\tCHIP_ID: 0x01"
        print"\t\t", "REV:", si4703.CHIP_ID.REV
        print"\t\t", "DEV:", si4703.CHIP_ID.DEV
        print"\t\t", "FIRMWARE:", si4703.CHIP_ID.FIRMWARE
        
        print"\tPOWER_CONFIG: 0x02"
        print"\t\t", "DSMUTE:", si4703.POWER_CONFIG.DSMUTE
        print"\t\t", "DMUTE:", si4703.POWER_CONFIG.DMUTE
        print"\t\t", "MONO:", si4703.POWER_CONFIG.MONO
        print"\t\t", "RDSM:", si4703.POWER_CONFIG.RDSM
        print"\t\t", "SKMODE:", si4703.POWER_CONFIG.SKMODE
        print"\t\t", "SEEKUP:", si4703.POWER_CONFIG.SEEKUP
        print"\t\t", "SEEK:", si4703.POWER_CONFIG.SEEK
        print"\t\t", "DISABLE:", si4703.POWER_CONFIG.DISABLE
        print"\t\t", "ENABLE:", si4703.POWER_CONFIG.ENABLE
        
        print"\tCHANNEL: 0x03"
        print"\t\t", "TUNE:", si4703.CHANNEL.TUNE 
        fmchan = si4703.CHANNEL.CHAN
        fmchan = (((fmchan*20)+8750)/10)
        print"\t\t", "CHAN:", si4703.CHANNEL.CHAN, "(", fmchan, ")"
    
        print"\tSYS_CONFIG_1: 0x04"
        print"\t\t", "RDSIEN:", si4703.SYS_CONFIG_1.RDSIEN
        print"\t\t", "STCIEN:", si4703.SYS_CONFIG_1.STCIEN
        print"\t\t", "RDS:", si4703.SYS_CONFIG_1.RDS
        print"\t\t", "DE:", si4703.SYS_CONFIG_1.DE
        print"\t\t", "AGCD:", si4703.SYS_CONFIG_1.AGCD
        print"\t\t", "BLNDADJ:", si4703.SYS_CONFIG_1.BLNDADJ
        print"\t\t", "GPIO3:", si4703.SYS_CONFIG_1.GPIO3
        print"\t\t", "GPIO2:", si4703.SYS_CONFIG_1.GPIO2
        print"\t\t", "GPIO1:", si4703.SYS_CONFIG_1.GPIO1
        
        print"\tSYS_CONFIG_2: 0x05"
        print"\t\t", "SEEKTH:", si4703.SYS_CONFIG_2.SEEKTH
        print"\t\t", "BAND:", si4703.SYS_CONFIG_2.BAND
        print"\t\t", "SPACE:", si4703.SYS_CONFIG_2.SPACE
        print"\t\t", "VOLUME:", si4703.SYS_CONFIG_2.VOLUME
        
        print"\tSYS_CONFIG_3: 0x06"
        print"\t\t", "SMUTER:", si4703.SYS_CONFIG_3.SMUTER
        print"\t\t", "SMUTEA:", si4703.SYS_CONFIG_3.SMUTEA
        print"\t\t","VOLEXT:", si4703.SYS_CONFIG_3.VOLEXT
        print"\t\t", "SKSNR:", si4703.SYS_CONFIG_3.SKSNR
        print"\t\t", "SKCNT:", si4703.SYS_CONFIG_3.SKCNT
        
        print"\tTEST_1: 0x07"
        print"\t\t", "XOSCEN:", si4703.TEST_1.XOSCEN
        print"\t\t", "AHIZEN:", si4703.TEST_1.AHIZEN
        print"\t\t", "RESERVED_FIRST_BYTE:", si4703.TEST_1.RESERVED_FIRST_BYTE
        print"\t\t", "RESERVED_SECOND_BYTE:", si4703.TEST_1.RESERVED_SECOND_BYTE
              
        print"\tTEST_2: 0x08"
        
        print"\tBOOT_CONFIG: 0x09"
              
        print"\tSTATUS_RSSI: 0x0A"
        print"\t\t", "RDSR:", si4703.STATUS_RSSI.RDSR
        print"\t\t", "STC:", si4703.STATUS_RSSI.STC
        print"\t\t", "SFBL:", si4703.STATUS_RSSI.SFBL
        print"\t\t", "AFCRL:", si4703.STATUS_RSSI.AFCRL
        print"\t\t", "RDSS:", si4703.STATUS_RSSI.RDSS
        print"\t\t", "BLER_A:", si4703.STATUS_RSSI.BLER_A
        print"\t\t", "ST:", si4703.STATUS_RSSI.ST
        print"\t\t", "RSS:", si4703.STATUS_RSSI.RSS
        
        print"\tREAD_CHAN: 0x0B"
        print"\t\t", "BLER_B:", si4703.READ_CHAN.BLER_B
        print"\t\t", "BLER_C:", si4703.READ_CHAN.BLER_C
        print"\t\t", "BLER_D:", si4703.READ_CHAN.BLER_D
        print"\t\t", "READ_CHAN:", si4703.READ_CHAN.READ_CHAN
              
        print"\tRDS_A: 0x0C"
        print"\t\t", "RDS_A:", si4703.RDS_A.RDS_A
        
        print"\tRDS_B: 0x0D"
        print"\t\t", "RDS_B:", si4703.RDS_B.RDS_B
        
        print"\tRDS_C: 0x0E"
        print"\t\t", "RDS_C:", si4703.RDS_C.RDS_C
        
        print"\tRDS_D: 0x0F"
        print"\t\t", "RDS_D:", si4703.RDS_D.RDS_D
              
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    
    def getRdsData(self):
        from time import sleep
        
        print "[getRdsData] Getting RDS data..."
        
        for retry in range(1,4):
            si4703.updateLocalRegistry(self)
            print si4703.RDS_A.RDS_A
            sleep(0.04)
              
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    
    class DEVICE_ID:                    #0x00
        PN      = 0
        MFGID   = 0
    class CHIP_ID:                      #0x01
        REV     = 0
        DEV     = 0
        FIRMWARE= 0
    class POWER_CONFIG:                 #0x02
        DSMUTE = 0
        DMUTE  = 0
        MONO   = 0
        ##     = 0
        RDSM   = 0
        SKMODE = 0
        SEEKUP = 0
        SEEK   = 0
        ##     = 0
        DISABLE= 0
        ##     = 0
        ##     = 0
        ##     = 0
        ##     = 0
        ##     = 0
        ENABLE = 0
        def FULL_REGISTER (self):  
            first_byte = str(DSMUTE) + str(DMUTE) + str(MONO) + "0" + str(RDSM) + str(SKMODE) + str(SEEKUP) + str(SEEK)
            first_byte = int(first_byte, 2)
            
            second_byte = "0" + str(DISABLE) + "00000" + str(ENABLE)
            second_byte = int(second_byte, 2)
            return [first_byte, second_byte]
    class CHANNEL:                      #0x03
        TUNE   = 0
        ##     = 0
        ##     = 0
        ##     = 0
        ##     = 0
        ##     = 0
        CHAN   = 0
    class SYS_CONFIG_1:                 #0x04
        RDSIEN = 0
        STCIEN = 0
        ##     = 0
        RDS    = 0
        DE     = 0
        AGCD   = 0
        ##     = 0
        ##     = 0
        BLNDADJ= 0
        GPIO3  = 0
        GPIO2  = 0
        GPIO1  = 0
    class SYS_CONFIG_2:                 #0x05
        SEEKTH = 0
        BAND   = 0
        SPACE  = 0
        VOLUME = 0
    class SYS_CONFIG_3:                 #0x06
        SMUTER = 0
        SMUTEA = 0
        ##     =
        ##     =
        ##     = 0
        VOLEXT = 0
        SKSNR  = 0
        SKCNT  = 0
    class TEST_1:                       #0x07
        XOSCEN = 0
        AHIZEN = 0
        RESERVED_FIRST_BYTE = 0 ## These bits are reserved, but their reset values are known, so they must be set-able 
        RESERVED_SECOND_BYTE = 0
        POWER_SEQUENCE = False
    class TEST_2:                       #0x08
        TEST_2 = 0
        ##ALL BITS IN THIS REGISTER ARE UNUSED
    class BOOT_CONFIG:                  #0x09
        BOOT_CONFIG = 0
        ##ALL BITS IN THIS REGISTER ARE UNUSED
    class STATUS_RSSI:                  #0x0A
        RDSR   = 0
        STC    = 0
        SFBL   = 0
        AFCRL  = 0
        RDSS   = 0
        BLER_A = 0
        ST     = 0
        RSSI   = 0
    class READ_CHAN:                    #0x0B
        BLER_B = 0 ##SEE THE STATUS_RSI REGISTER ABOVER FOR BLER-A
        BLER_C = 0
        BLER_D = 0
        READ_CHAN = 0
    class RDS_A:                        #0x0C
        RDS_A  = 0
    class RDS_B:                        #0x0D
        RDS_B  = 0
    class RDS_C:                        #0x0E
        RDS_C  = 0
    class RDS_D:                        #0x0F
        RDS_D  = 0
