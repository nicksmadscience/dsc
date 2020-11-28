import serial
import smtplib
import datetime
import time
import commands
import os
import sys
import socket

# LED behavior
# armed:  red
# entry delay:  red fast flash
# exit delay:   green flash
# garage ready: green
# garage not ready: yellow
# garage trouble: yellow flashing

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

pin_red = 3
GPIO.setup(pin_red, GPIO.OUT)
GPIO.output(pin_red, False)

pin_green = 7
GPIO.setup(pin_green, GPIO.OUT)
GPIO.output(pin_green, False)

pin_blue = 5
GPIO.setup(pin_blue, GPIO.OUT)
GPIO.output(pin_blue, False)

now = datetime.datetime.now()

# Here are the email package modules we'll need
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from threading import Thread


# import prowlpy
# apikey = ''
# p = prowlpy.Prowl(apikey)

UDP_IP = "10.0.0.83"
UDP_PORT = 1234

def sendCommandToPlayback(_command):
    sock = socket.socket(socket.AF_INET, # Internet
    socket.SOCK_DGRAM) # UDP
    sock.sendto(_command, (UDP_IP, UDP_PORT))

# sock = socket.socket(socket.AF_INET, # Internet
# socket.SOCK_DGRAM) # UDP
# sock.sendto("ks1,playonce:yelp1.wav,turnOffKitchenSpeakersWhenDone", (UDP_IP, UDP_PORT))

PORT_NUMBER = 8080

lcdMessage = ""

import httplib, urllib
#nick
# appToken = ""
# userKey  = ""

# alan
appToken = ""
userKey  = ""

def sendThatFunkyNotification(_message):
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.urlencode({
        "token": appToken,
        "user": userKey,
        "message": _message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

    #p.add('DSC', "DSC", _message, 0, None, "")

sendThatFunkyNotification("the alarm monitor just started running")

def requestHandler_index(_get):
    return """
<html>
    <head>
        <title>Alarm interface!</title>
        <script type="text/javascript">
        function buttonpress(_button)
        {
            console.log("button pressed: " + _button);
            loadXMLDoc("buttonpressed/" + _button, function(){});
        }

        function buttonrelease(_button)
        {
            console.log("button released: " + _button);
            loadXMLDoc("buttonreleased/" + _button, function(){});
        }

        var xmlhttp;
        function loadXMLDoc(url,cfunc)
        {
            if (window.XMLHttpRequest)
                  xmlhttp=new XMLHttpRequest();  // code for IE7+, Firefox, Chrome, Opera, Safari

            xmlhttp.onreadystatechange=cfunc;
            xmlhttp.open("GET",url,true);
            xmlhttp.send();
        }

        function replaceItemWithAJAX(_item, _request)
        {            
            // kill the status auto-update if it's running
            if(typeof autostatus!='undefined')
                window.clearInterval(autostatus);

            // then load up a text input to replace the text that was there before
            loadXMLDoc(_request, function()
            {
                if (xmlhttp.readyState==4 && xmlhttp.status==200)
                {
                    document.getElementById(_item).innerHTML = xmlhttp.responseText;
                    if (document.contains(document.getElementById('onElementLoad')))
                        eval(document.getElementById('onElementLoad').innerHTML);
                }
            });
        }

        function updateLCD()
        {
            replaceItemWithAJAX("display", "display");
        }

        function autoUpdateLCD()
        {
            if(typeof autoLCD!='undefined')
            window.clearInterval(autoLCD);

            autoLCD = setInterval(function(){updateLCD();},500);
        }
        </script>
    </head>
    <body onload="autoUpdateLCD()">
        <div id="display" style="width: 100px; height: 50px; background-color: #dddddd; font-family: monospace; font-size: 10px"></div>
        <div id="leds"></div>
        <div id="keyboard">
            <p>
                <button id="button_1" onmousedown="buttonpress('1')" onmouseup="buttonrelease('1')">1</button>
                <button id="button_2" onmousedown="buttonpress('2')" onmouseup="buttonrelease('2')">2</button>
                <button id="button_3" onmousedown="buttonpress('3')" onmouseup="buttonrelease('3')">3</button>
            </p>
            <p>
                <button id="button_4" onmousedown="buttonpress('4')" onmouseup="buttonrelease('4')">4</button>
                <button id="button_5" onmousedown="buttonpress('5')" onmouseup="buttonrelease('5')">5</button>
                <button id="button_6" onmousedown="buttonpress('6')" onmouseup="buttonrelease('6')">6</button>
            </p>
            <p>
                <button id="button_7" onmousedown="buttonpress('7')" onmouseup="buttonrelease('7')">7</button>
                <button id="button_8" onmousedown="buttonpress('8')" onmouseup="buttonrelease('8')">8</button>
                <button id="button_9" onmousedown="buttonpress('9')" onmouseup="buttonrelease('9')">9</button>
            </p>
            <p>
                <button id="button_*" onmousedown="buttonpress('*')" onmouseup="buttonrelease('*')">*</button>
                <button id="button_0" onmousedown="buttonpress('0')" onmouseup="buttonrelease('0')">0</button>
                <button id="button_#" onmousedown="buttonpress('#')" onmouseup="buttonrelease('#')">#</button>
            </p>
        </div>
    </body>
</html>
    """


def dscChecksum(_code):
    total = 0
    for character in _code:
        total += ord(character)

    return str(hex(total & 255))[2:].upper()  #the 2: is to get rid of the 0x


def pressButton(_button):
    outgoing = "070" + _button
    ser.write(outgoing + dscChecksum(outgoing) + chr(13) + chr(10))
    print ("sending: " + outgoing + dscChecksum(outgoing))


def releaseButton(_button):
    outgoing = "070^"
    ser.write(outgoing + dscChecksum(outgoing) + chr(13) + chr(10))
    print ("sending: " + outgoing + dscChecksum(outgoing))


def requestHandler_display(_get):
    global lcdMessage
    return lcdMessage[5:]

def requestHandler_buttonPressed(_get):
    pressButton(_get[2])
    return "button pressed: " + _get[2]

def requestHandler_buttonReleased(_get):
    releaseButton(_get[2])
    return "button released: " + _get[2]

httpRequests = {'index'          : requestHandler_index,
                'display'        : requestHandler_display,
                'buttonpressed'  : requestHandler_buttonPressed,
                'buttonreleased' : requestHandler_buttonReleased}

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
    
    #Handler for the GET requests
    def do_GET(self):
        elements = self.path.split('/')
        # elementCount = 0
        # for element in elements:
        #     self.wfile.write(str(elementCount) + ": " + element + '\n')
        #     elementCount += 1
        if elements[1] == 'static':
            try:
            #Check the file extension required and
            #set the right mime type
                sendReply = False
                if self.path.endswith(".html"):
                    mimetype='text/html'
                    sendReply = True
                if self.path.endswith(".jpg"):
                    mimetype='image/jpg'
                    sendReply = True
                if self.path.endswith(".gif"):
                    mimetype='image/gif'
                    sendReply = True
                if self.path.endswith(".js"):
                    mimetype='application/javascript'
                    sendReply = True
                if self.path.endswith(".css"):
                    mimetype='text/css'
                    sendReply = True
                if self.path.endswith(".png"):
                    mimetype='text/png'
                    sendReply = True

                if sendReply == True:
                    #Open the static file requested and send it
                    print "trying to open this path: " + self.path[8:]
                    f = open(self.path[8:]) 
                    self.send_response(200)
                    self.send_header('Content-type',mimetype)
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                return
            except IOError:
                self.send_error(404,'File Not Found: %s' % self.path)
        else:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            #self.wfile.write('<html><body><p>time to load something dynamic!</p></body></html>')

            responseFound = False
            for httpRequest, httpHandler in httpRequests.iteritems():
                if elements[1].find(httpRequest) == 0: # in other words, if the first part matches
                    response = httpHandler(elements)
                    responseFound = True

            # if elements[1] in httpRequests:
            #     response = httpRequests[elements[1]](elements[1])
                    self.wfile.write(response)
            if not responseFound:
                self.wfile.write('I don\'t know what to do with this request!')
                

            return

#import prowlpy
#apikey = ''
#p = prowlpy.Prowl(apikey)



dscIncomingCommands = {'500': 'Command Acknowledge',
    '501': 'Command Error',
    '502': 'System Error',
    '550': 'Time/Date Broadcast',
    '560': 'Ring Detected',
    '561': 'Indoor Temperature Broadcast',
    '562': 'Outdoor Temperature Broadcast',
    '563': 'Thermostat Set Points',
    '570': 'Broadcast Labels',
    '580': 'Baud Rate Set',
    '601': 'Zone Alarm',
    '602': 'Zone Alarm Restore',
    '603': 'Zone Tamper',
    '604': 'Zone Tamper Restore',
    '605': 'Zone Fault',
    '606': 'Zone Fault Restore',
    '609': 'Zone Open',
    '610': 'Zone Restored',
    '620': 'Duress Alarm',
    '621': '[F] Key Alarm',
    '622': '[F] Key Restoral',
    '623': '[A] Key Alarm',
    '624': '[A] Key Restoral',
    '625': '[P] Key Alarm',
    '626': '[P] Key Restoral',
    '631': 'Auxiliary Input Alarm',
    '632': 'Auxiliary Input Alarm Restored',
    '650': 'Partition Ready',
    '651': 'Partition Not Ready',
    '652': 'Partition Armed - Descriptive Mode',
    '653': 'Partition in Ready to Force Arm',
    '654': 'Partition In Alarm',
    '655': 'Partition Disarmed',
    '656': 'Exit Delay in Progress',
    '657': 'Entry Delay in Progress',
    '658': 'Keypad Lock-out',
    '659': 'Keypad Blanking',
    '660': 'Command Output in Progress',
    '670': 'Invalid Access Code',
    '671': 'Function Not Avaiable',
    '672': 'Fail to Arm',
    '673': 'Partition Busy',
    '700': 'User Closing',
    '701': 'Special Closing',
    '702': 'Partial Closing',
    '750': 'User Opening',
    '751': 'Special Opening',
    '800': 'Panel Battery Trouble',
    '801': 'Panel Battery Trouble Restore',
    '802': 'Panel AC Trouble',
    '803': 'Panel AC Restore',
    '806': 'System Bell Trouble',
    '807': 'System Bell Trouble Restoral',
    '810': 'TLM Line 1 Trouble',
    '811': 'TLM Line 1 Trouble Restored',
    '812': 'TLM Line 2 Trouble',
    '813': 'TLM Line 2 Trouble Restored',
    '814': 'FTC Trouble',
    '816': 'Buffer Near Full',
    '821': 'General Device Low Battery',
    '822': 'General Device Low Battery Restore',
    '825': 'Wireless Key Low Battery Trouble',
    '826': 'Wireless Key Low Battery Trouble Restore',
    '827': 'Handheld Keypad Low Battery Trouble',
    '828': 'Handheld Keypad Low Battery Restored',
    '829': 'General System Tamper',
    '830': 'General System Tamper Restore',
    '831': 'Home Automation Trouble',
    '832': 'Home Automation Trouble Restore',
    '840': 'Trouble Status (LED ON)',
    '841': 'Trouble Status Restore (LED OFF)',
    '842': 'Fire Trouble Alarm',
    '843': 'Fire Trouble Alarm Restored',
    '896': 'Keybus Fault',
    '897': 'Keybus Fault Restore',
    '900': 'Code Required',
    '901': 'LCD Update',
    '902': 'LCD Cursor',
    '903': 'LED Status',
    '904': 'Beep Status',
    '905': 'Tone Status',
    '906': 'Buzzer Status',
    '907': 'Door Chime Status',
    '908': 'Software Version'}

def incomingParse_timeDateBroadcast(_message):
    print "time date broadcast woo"

def incomingParse_zoneOpen(_message):
    print "Zone " + _message[0:3].lstrip('0') + " Open"

def incomingParse_zoneRestored(_message):
    print "Zone " + _message[0:3].lstrip('0') + " Restored"

def incomingParse_lcdUpdate(_message):
    global lcdMessage
    print "LCD update: " + _message[5:]
    lcdMessage = _message



dscIncomingParsers = {
    '550': incomingParse_timeDateBroadcast,
    '609': incomingParse_zoneOpen,
    '610': incomingParse_zoneRestored,
    '901': incomingParse_lcdUpdate}


eventHooks = dict()

def addEventHook(_event, _hook):
    try:
        eventHooks[_event].append(_hook)
    except:
        eventHooks[_event] = []
        eventHooks[_event].append(_hook)




ledcolors = {
    'red'   : [True,  False, False],
    'yellow': [True,  True,  False],
    'green' : [False, True,  False],
    'cyan'  : [False, True,  True ],
    'blue'  : [False, False, True ],
    'purple': [True,  False, True ],
    'white' : [True,  True,  True ],
    'off'   : [False, False, False]}

print ledcolors


def setLEDTo(_color, _pulse = 'steady', _altcolor=''):
    global ledcolors

    newcolor = ledcolors[_color]
    print "*** " + _color
    print "*** " + str(newcolor)

    GPIO.output(pin_red,   newcolor[0])
    GPIO.output(pin_green, newcolor[1])
    GPIO.output(pin_blue,  newcolor[2])







def eventHook_ledReady(_message):
    if _message[3] == '2':
        setLEDTo('green', 'steady')

    print "*** LED READY (" + str(_message) + ") ***"

def eventHook_ledArmed(_message):
    if _message[3] == '2':
        setLEDTo('red', 'steady')

def eventHook_ledEntryDelay(_message):
    if _message[3] == '2':
        setLEDTo('red', 'fastflash')

def eventHook_ledExitDelay(_message):
    if _message[3] == '2':
        setLEDTo('green', 'fastflash')

def eventHook_ledInAlarm(_message):
    if _message[3] == '2':
        setLEDTo('red', 'alternate', 'blue')

def eventHook_ledNotReady(_message):
    if _message[3] == '2':
        setLEDTo('yellow', 'steady')

addEventHook('652', eventHook_ledArmed)
addEventHook('657', eventHook_ledEntryDelay)
addEventHook('656', eventHook_ledExitDelay)
addEventHook('650', eventHook_ledReady)
addEventHook('651', eventHook_ledNotReady)
addEventHook('654', eventHook_ledInAlarm)
#addEventHook('655', eventHook_ledDisarmed)


# doorTimerActive17 = False
# doorTimerTime17   = 1.0
# doorTimerPreviouslyAlarmed17 = False
# doorTimerNotificationSent17 = False
# doorTimerActive18 = False
# doorTimerTime18   = 1.0
# doorTimerPreviouslyAlarmed18 = False
# doorTimerNotificationSent18 = False

# def eventHook_doorAlarm(_message):
#     global doorTimerActive18
#     global doorTimerTime18
#     global doorTimerActive17
#     global doorTimerTime17
#     global doorTimerNotificationSent18
#     global doorTimerNotificationSent17

#     if _message[3:6] == '018':
#         print "back door is open; starting door timer"
#         doorTimerActive18 = True
#         doorTimerTime18   = time.clock() + 15.0
#     elif _message[3:6] == '017':
#         print "front door is open; starting door timer"
#         doorTimerActive17 = True
#         doorTimerTime17   = time.clock() + 15.0

# def eventHook_doorAlarmReset(_message):
#     global doorTimerActive18
#     global doorTimerPreviouslyAlarmed18
#     global doorTimerActive17
#     global doorTimerPreviouslyAlarmed17
#     global doorTimerNotificationSent18
#     global doorTimerNotificationSent17

#     if _message[3:6] == '018':
#         doorTimerActive18 = False
#         if doorTimerNotificationSent18:
#             doorTimerNotificationSent18 = False
#         if doorTimerPreviouslyAlarmed18:
#             doorTimerPreviouslyAlarmed18 = False
#             sendNotificationEmail("The BACK DOOR has been closed", "yay")
#         print "back door closed; timer canceled"
#     elif _message[3:6] == '017':
#         doorTimerActive17 = False
#         if doorTimerNotificationSent17:
#             doorTimerNotificationSent17 = False
#         if doorTimerPreviouslyAlarmed17:
#             doorTimerPreviouslyAlarmed17 = False
#             sendNotificationEmail("The FRONT DOOR has been closed", "yay")
#         print "front door closed; timer canceled"




### MOUSE DOOR PUSH NOTIFICATION ###

def eventHook_mouseDoorOpen(_message):
    print "mouse door open function"
    #print _message
    if _message[3:6] == '001':
        print "THE MOUSE DOOR IS OPEN"
        ##p.add('Burglar alarm', "Burglar alarm", "The Mouse door is open", 0, None, "")

    if _message[3:6] == '006':
        sendThatFunkyNotification("power fail!")
        

def eventHook_mouseDoorClosed(_message):
    print "mouse door closed function"
    #print _message
    if _message[3:6] == '001':
        print "THE MOUSE DOOR IS CLOSED"
        ##p.add('Burglar alarm', "Burglar alarm", "The Mouse door is closed", 0, None, "")

    if _message[3:6] == '006':
        sendThatFunkyNotification("power restored!")

def eventHook_powerLoss(_message):
    sendThatFunkyNotification('power loss!')

def eventHook_powerRestored(_message):
    sendThatFunkyNotification('power restored!')

def eventHook_alarm(_message):
    sendThatFunkyNotification('alarm!' + _message)
    sendCommandToPlayback("ks1,superyelp,turnOffKitchenSpeakersWhenDone")

def eventHook_zoneAlarmRestored(_message):
    sendThatFunkyNotification('zone alarm restored' + _message)
    sendCommandToPlayback("ks0,stop")


ser = serial.Serial("/dev/ttyUSB0")
print ser

# addEventHook('609', eventHook_doorAlarm)
# addEventHook('610', eventHook_doorAlarmReset)

#addEventHook('609', eventHook_mouseDoorOpen)
#addEventHook('610', eventHook_mouseDoorClosed)
addEventHook('802', eventHook_powerLoss)
addEventHook('803', eventHook_powerRestored)
addEventHook('654', eventHook_alarm)
addEventHook('602', eventHook_zoneAlarmRestored)

ser.write("00191" + chr(13) + chr(10))

with open('dsclog.txt', 'a') as the_file:
    the_file.write(now.strftime('\n\n%F %T Started program\n'))

def serialLoop():
    while True:
        if ser.inWaiting():
            line = ser.readline()

            print "CODE! " + line

            try:
                dscIncomingParsers.get(line[0:3])(line[3:len(line) - 4])
            except:
                incoming = dscIncomingCommands.get(line[0:3])
                if incoming == None:
                    print line
                else:
                    print incoming + " " + line[3:len(line) - 4]

            try:
                # find and call hooks
                hookList = eventHooks.get(line[0:3])
                if hookList is not None:
                    for hook in hookList:
                        hook(line)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(e, exc_type, fname, exc_tb.tb_lineno)
                print "could not find and call hooks"
                with open('dsclog.txt', 'a') as the_file:
                    the_file.write(now.strftime('%F %T Could not find and call hooks\n'))

serialLoopThread = Thread(target=serialLoop)
serialLoopThread.daemon = True
serialLoopThread.start()

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ' , PORT_NUMBER

    server.serve_forever()


except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()
    GPIO.cleanup()

    # try:
    #     # quick HACK for door timer
    #     if doorTimerActive18 and time.clock() > doorTimerTime18:
    #         #doorTimerActive18 = False
    #         doorTimerTime18 = time.clock() + 25.0
    #         doorTimerPreviouslyAlarmed18 = True
    #         print "the BACK DOOR has been open for 25 seconds; playing alarm message"
    #         if not doorTimerNotificationSent18:
    #             sendNotificationEmail("the BACK DOOR has been open for", "25 seconds")
    #             doorTimerNotificationSent18 = True
    #         try:
    #             os.system('mplayer "audio/Back Door Left Open.wav" &')
    #         except:
    #             print "couldn't play Back Door Left Open.wav"
    #             with open('dsclog.txt', 'a') as the_file:
    #                 the_file.write(now.strftime('%F %T couldn\'t play Back Door Left Open\n'))
    # except:
    #     print "could not do door timer 18"
    #     with open('dsclog.txt', 'a') as the_file:
    #         the_file.write(now.strftime('%F %T couldn\'t do door timer 18\n'))

    # try:
    #     if doorTimerActive17 and time.clock() > doorTimerTime17:
    #         #doorTimerActive17 = False
    #         doorTimerTime17 = time.clock() + 25.0
    #         doorTimerPreviouslyAlarmed17 = True
    #         print "the FRONT DOOR has been open for 25 seconds; playing alarm message"
    #         if not doorTimerNotificationSent17:
    #             sendNotificationEmail("the FRONT DOOR has been open for", "25 seconds")
    #             doorTimerNotificationSent17 = True
    #         try:
    #             os.system('mplayer "audio/Front Door Left Open.wav" &')
    #         except:
    #             print "couldn't play Front Door Left Open.wav"
    #             with open('dsclog.txt', 'a') as the_file:
    #                 the_file.write(now.strftime('%F %T couldn\'t play Front Door Left Open\n'))
    # except:
    #     print "could not do door timer 18"
    #     with open('dsclog.txt', 'a') as the_file:
    #         the_file.write(now.strftime('%F %T couldn\'t do door timer 17\n'))

ser.close()
