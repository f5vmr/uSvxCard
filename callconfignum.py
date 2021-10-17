#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# G4NAB 2021

import configparser, os
import json
import sys
import getopt

from configparser import ConfigParser

svxlinkcfg='/etc/spotnik/svxlink.cfg'
svxlinkel='/etc/spotnik/svxlink.el'
moduleecholinkconf='/etc/spotnik/svxlink.d/ModuleEchoLink.conf'
Json="/etc/spotnik/config.json"
fileId= '/var/lib/mmdvm/DMRIds.dat'
analogbridgeini= "/opt/Analog_Bridge/Analog_Bridge.ini"
mmdmvbridgeini="/opt/MMDVM_Bridge/MMDVM_Bridge.ini"
YSFGatewayini="/opt/YSFGateway/YSFGateway.ini"
mmdvmbridgedmr="/opt/MMDVM_Bridge/MMDVM_Bridge.dmr"


version="1.00"
call = " "
dept= " "
band = " "
usage= " "
Id = " "
test=0

# commit with arguements
    
def main(argv):
    global dept 
    global call
    global band

    try:
        options, remainder = getopt.getopt(argv, '', ['help', 'version', 'dept=', 'call=', 'band='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    for opt, arg in options:
        if opt == '--help':
            usage()
            sys.exit()
        elif opt == '--version':
            print(version)
            sys.exit()
        elif opt in ('--dept'):
            if arg != "":
                dept=str(arg)        
        elif opt in ('--call'):
            if arg != "":
                call=(arg)
                                            
        elif opt in ('--band'):
            if arg != "":
                band=str(arg)
                

    Input_control(dept,call,band)
                
            
    
def Input_control(dept,call,band):

    if dept==" " or call==" " or band==" ":
        print(dept+call+band)
        usage()
    else:
#updating the calls
        upcallsignSVX=(call)
        upcallsignEL=( "EL-" +call)
        upcallsignRRF=("(" +dept+ ") " +call+" "+band)

#writing the calls
        print(call)
        print( call + "-EL")
        print("(" +dept+ ") " +call+" "+band)

#CAPS in the config files
        updatecall(upcallsignSVX,upcallsignEL,upcallsignRRF)
        updatecallel(upcallsignSVX,upcallsignEL)
        updatecallelconf(upcallsignSVX)
        updatecall_json()
        searchId(call)
        updateIdMMDMV_Bridge(call,Id)
        updateIdANALOG_Bridge(call,Id)
        updateGateway(call,YSFGatewayini)
        updateMMDVM(call,mmdvmbridgedmr)

def usage():
    print('Usage: callconfig.py [options ...]')
    print()
    print('--help                           This help')
    print('--version                        Version number')
    print()
    print('Parameters:')
    print() 
    print('  --dept       number      Enter the departement ex:99 for the UK')
    print('  --call       textc       Enter your callsign ex:G4ABC')
    print('  --band       number      Enter the access type (H,V,U,10M,R,T,T10M,S)')
    print()
    print('73 de G4NAB Chris')


#Function writing svxlink.cfg
def updatecall(callsignSVX,callsignEL,callsignRRF):
 
    config = ConfigParser()
    config.optionxform = str

    config.read(svxlinkcfg)

    string_val = config.get('SimplexLogic', 'CALLSIGN')
    config.set('SimplexLogic', 'CALLSIGN', callsignSVX)

    string_val = config.get('LocationInfo', 'CALLSIGN')
    config.set('LocationInfo', 'CALLSIGN', callsignEL)

    string_val = config.get('ReflectorLogic', 'CALLSIGN')
    config.set('ReflectorLogic', 'CALLSIGN', callsignRRF)

    with open(svxlinkcfg, 'w') as configfile:
        config.write(configfile, space_around_delimiters=False)

#Function Writing in svxlink.el
def updatecallel(callsignSVX,callsignEL):

    config = ConfigParser()
    config.optionxform = str

    config.read(svxlinkel)

    string_val = config.get('SimplexLogic', 'CALLSIGN')
    config.set('SimplexLogic', 'CALLSIGN', callsignSVX)

    string_val = config.get('LocationInfo', 'CALLSIGN')
    config.set('LocationInfo', 'CALLSIGN', callsignEL)

    with open(svxlinkel, 'w') as configfile:
        config.write(configfile, space_around_delimiters=False)

#Function writing into moduleecholinkconf
def updatecallelconf(callsignSVX):

    config = ConfigParser()
    config.optionxform = str

    config.read(moduleecholinkconf)

    string_val = config.get('ModuleEchoLink', 'CALLSIGN')
    config.set('ModuleEchoLink', 'CALLSIGN', callsignSVX)

    with open(moduleecholinkconf, 'w') as configfile:
        config.write(configfile, space_around_delimiters=False)


#Function writing in config.json
def updatecall_json():

    #read data JSON
    with open(Json, 'r') as f:
        config = json.load(f)
        config['callsign'] = call
        config['Departement'] = dept
        config['band_type'] = band
    #write data JSON
    with open(Json, 'w') as f:
        json.dump(config, f)    
#
#Digital part
#

#looking up DMR Id with respect to call
def searchId(callsignId):
    global Id
    global test
    
    fichier = open(fileId,"r")
    print("Looking up Id ...")
    for ligne in fichier:
        if callsignId in ligne:
            Id = ((ligne).split())
            print(Id[0])
            Id = Id[0]
    fichier.close()

    if Id==" ":
            print('\x1b[7;37;41m'+"->Your callsign does not figure in the DATABASE DMRIds.dat "+'\x1b[0m')
            os.system('sh /usr/local/sbin/DMRIDUpdate.sh')
            
            if test==0:
                test=1
                searchId(callsignId)
                

            else:
                sys.exit()

    else:
        controlID(Id,analogbridgeini)

#Update Id in the digital folder

def updateIdMMDMV_Bridge(callsign,Id):
        
    config = ConfigParser()
    config.optionxform = str

    config.read(analogbridgeini)

    string_val = config.get('AMBE_AUDIO', 'gatewayDmrId')
    config.set('AMBE_AUDIO', 'gatewayDmrId', Id)

    string_val = config.get('AMBE_AUDIO', 'repeaterID')
    config.set('AMBE_AUDIO', 'repeaterID', Id+"01")

    with open(analogbridgeini, 'w') as configfile:
    #
        config.write(configfile, space_around_delimiters=False)
        print("Writing MMDMV_Bridge.ini ...")

def updateIdANALOG_Bridge(callsign,Id):

    config = ConfigParser()
    config.optionxform = str

    config.read(mmdmvbridgeini)

    string_val = config.get('General', 'Callsign')
    config.set('General', 'Callsign', callsign )

    string_val = config.get('General', 'Id')
    config.set('General', 'Id', Id)
      
    with open(mmdmvbridgeini, 'w') as configfile:
        config.write(configfile, space_around_delimiters=False)
        print("Ecriture ANALOG_Bridge.ini ...")

#Update gateway folders
def updateGateway(callsign,fileini):
        
    config = ConfigParser()
    config.optionxform = str

    config.read(fileini)

    string_val = config.get('General', 'Callsign')
    config.set('General', 'Callsign', callsign )
    
    string_val = config.get('General', 'Id')
    config.set('General', 'Id', Id)

    with open(fileini, 'w') as configfile:
        config.write(configfile, space_around_delimiters=False)
        print("Ecriture "+fileini+" ...")    

#Updating MMDVM_Bridge.dmr
def updateMMDVM(callsign,fileini):

    config = ConfigParser()
    config.optionxform = str

    config.read(fileini)

    string_val = config.get('General', 'Callsign')
    config.set('General', 'Callsign', callsign )

    string_val = config.get('General', 'Id')
    config.set('General', 'Id', Id)

    with open(fileini, 'w') as configfile:
        config.write(configfile, space_around_delimiters=False)
        print("Writing "+fileini+" ...")

def controlID(id,fileini):
    
    print(id)
    print(fileini)

    config = ConfigParser()
    config.optionxform = str

    config.read(fileini)

    string_val = config.get('AMBE_AUDIO', 'gatewayDmrId')
    
    if string_val==id:
        print(string_val+' already present...ending procedure')
        sys.exit()
     


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
