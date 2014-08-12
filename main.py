import httplib,urllib
import time
import xmlrpclib, ast
import socket

glances_server = "http://127.0.0.1"
PORT = 61209
user_ID = ""
app_Token = ""


DEF_CHECK_FREQ_MIN = 30
EMG_CHECK_FREQ_MIN = 10
TOGGLE_ALERT = False
DEBUG = False


global idle_CPU, idle_RAM

def pushAlert(title,messages,timestamp=int(time.time()),priority=0,sound='pushover',device='',):
    if DEBUG:
        print 'Sent Push-Notification'
    else:
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST","/1/messages.json",
            urllib.urlencode({
                "token": app_Token,
                "user":user_ID ,
                "title":title,
                "message": messages,
                "priority":priority,
                "timestamp":str(timestamp),
                'device': device,
                'sound': sound
                }),{"Content-type":"application/x-www-form-urlencoded"})
        conn.getresponse()
    time.sleep(60*EMG_CHECK_FREQ_MIN)

def is_alive():
    import urllib2
    try:
        response=urllib2.urlopen(glances_server,timeout=1)
        return True
    except urllib2.URLError as err:
        pass
    return False

def main():
    if DEBUG:
        print "DEBUG = True"
    try:
        server = xmlrpclib.ServerProxy(glances_server+':'+str(PORT))
        idle_CPU = ast.literal_eval(server.getCpu())['idle']
        tmp = ast.literal_eval(server.getMem())
        idle_RAM = round(float(tmp['available'])/float(tmp['total'])*100,1)
        if DEBUG:
            print "CPU : " + str(idle_CPU) + "%\t" + "RAM : " + str(idle_RAM) + "%"
        if idle_CPU < 25.0:
            TOGGLE_ALERT = True
            title="Warning!!!! [idle_CPU :  " + str(idle_CPU) + "%]"
            tmp = ast.literal_eval(server.getProcessList())
            lst = []
            for a in tmp:
                if a['cpu_percent'] != 0.0:
                    lst.append({
                        'name':a['name'],
                        'cpu_percent':a['cpu_percent'],
                        'mem_percent':a['memory_percent']
                        })
            msg = "Process List(Order by CPU Usage)\n"
            lst = sorted(lst,key=lambda i:i['cpu_percent'])
            for a in lst:
                msg += a['name'] + "\t" + a['cpu_percent'] + '\t' + a['mem_percent'] + '\n'
            pushAlert(title=title, messages=msg, priority=0)
        elif idle_RAM < 20.0:
            TOGGLE_ALERT = True
            title="Warning!!!! [idle_Mem :  " + str(idle_RAM) + "%]"
            tmp = ast.literal_eval(server.getProcessList())
            lst = []
            for a in tmp:
                if a['cpu_percent'] != 0.0:
                    lst.append({
                        'name':a['name'],
                        'cpu_percent':a['cpu_percent'],
                        'mem_percent':a['memory_percent']
                        })
            msg = "Process List(Order by Memory Usage)\n"
            lst = sorted(lst,key=lambda i:i['mem_percent'])
            for a in lst:
                msg += a['name'] + "\t" + a['cpu_percent'] + '\t' + a['mem_percent'] + '\n'
            pushAlert(title=title, messages = msg, priority=0)    
        else:
            TOGGLE_ALERT = False
            title = "Periodical Report"
            messages = "CPU : " + str(idle_CPU) + "%\t" + "RAM : " + str(idle_RAM) + "%"
            pushAlert(title=title, messages = messages, priority=-1, sound='none')
    except socket.error, (errno, msg):
        if DEBUG:
            print "Socket Error!! - [" + str(errno) +"] " + msg
        title="Emergency!!!! [socket.error " + str(errno) + "]"
        if not is_alive():
            messages = "[HTTP dead]\n" + msg
        else:
            messages = "[HTTP alive]\n" + msg
        pushAlert(title=title, messages = messages, priority=1, sound='alien')
    except Exception as e:
        if DEBUG:
            print "pyGlances Crush - ", e
        title="Error!!!! [pyGlances Crush]"
        if not is_alive():
            messages = "[HTTP dead]\n" + e.args[0]
        else:
            messages = "[HTTP alive]\n" + e.args[0]
        pushAlert(title=title, messages = messages, priority=1,sound='alien')
if __name__ == '__main__':
    while(1):
        main()
        if DEBUG:
            DEF_CHECK_FREQ_MIN = 0.02
        time.sleep(60*DEF_CHECK_FREQ_MIN)