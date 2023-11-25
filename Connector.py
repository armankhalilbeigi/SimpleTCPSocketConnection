from ghpythonlib.componentbase import executingcomponent as component
import GhPython
import Grasshopper
import Grasshopper as gh
import System
import Rhino
import rhinoscriptsyntax as rs
import threading
import System.Net as net
import time
import System.Drawing as sd


class Test:
    def __init__(self, ip, port, Timeout, comp ,as_server=True):
        self.compon = comp
        self.client = None
        self.socket_stream = None
        self.received_msg = "Streaming Started ..."
        self.try_connect = True
        self.receive_thread = None
        self.receiver_list = []
        self.kill_thread = False
        self.myip = net.IPAddress.Parse(str(ip))
        self.port = port
        self.rmsg = None #to Print Msgs in Log output
        self.timeout = Timeout
        self.msghistory = []
        if as_server:
            self.server = net.Sockets.TcpListener(self.myip, int(self.port))
            self.connection_thread = threading.Thread(target=self.connect_as_server, args =(lambda : self.kill_thread, ))
            self.rmsg = "111111111111111111" #to Print Msgs in Log output
        else:
            self.client = net.Sockets.TcpClient()
            self.connection_thread = threading.Thread(target=self.connect_as_client)
        self.connection_thread.daemon = True
    
    def __delete__(self):
        self.clean_up()
    
    def clean_up(self):
        self.rmsg =  "Cleaning up and restarting".center(100, '=')
        if self.socket_stream:
            try:
                self.socket_stream.Close()
            except Exception as e:
                print e
        if self.client:
            try:
                self.client.Dispose()
            except Exception as e:
                print e
        else:
            try:
                self.server.Stop()
            except Exception as e:
                print e
        
        self.received_msg = "Beginning of the Stream "
        self.receiver_list = []
        self.kill_thread = True
        self.server = None
        self.con = None
        self.socket_stream = None
        self.connection_thread = None
        self.receive_thread = None
        self.try_connect = True
        
        self.log()
    
    def connect(self):
        if not self.try_connect:
            return

        self.rmsg =  "Starting Listener Thread".center(10, '=') # Not Running
        
        if not self.connection_thread.is_alive() :
            self.rmsg =  "Starting Server".center(10, '=')
            try:
                self.connection_thread.start()
            except Exception as e:
                self.rmsg =  "Couldn't start the thread ! > ", e
        else:
            self.rmsg =  "Thread is already running".center(100, '-')
        self.log()
    
    def connect_as_client(self):
        self.rmsg =  "$>\tAttempting to Connect . . ."
        ipep = net.IPEndPoint(self.myip, self.port)
        self.client.Connect(ipep)
        self.socket_stream = self.client.GetStream()
        self.socket_stream.ReadTimeout = int(self.timeout)
        self.compon.ExpireSolution(True)
    
    def connect_as_server(self, kill_flag):
        self.rmsg =  "$>\tStarting to Connect . . ."
        try:
            self.server.Start()
            self.rmsg =  "$>\tListening . . ."
            while not kill_flag():
                if self.server.Pending():
                    self.rmsg =  "$>\tPending Connection Detected"
                    self.client = self.server.AcceptTcpClient()
                    self.socket_stream = self.client.GetStream()
                    self.socket_stream.ReadTimeout = int(self.timeout)   ##Timeout
                    break
        except Exception as e:
            self.rmsg =  "$>\tFailed to connect >>> ", e     #Mention to User to try to Set server Off and On 
        finally:
            if self.server:
                self.server.Stop()
            self.try_connect = False
            self.compon.ExpireSolution(True)
    
    def receiver_thread_start(self):
        if not self.receive_thread:
            self.receive_thread = threading.Thread(target=self.receive_message, args =(lambda : self.receiver_list, lambda : self.kill_thread, ))
            self.receive_thread.daemon = True
            self.receive_thread.start()
    
    def receive_message(self, comps, kill_flag):
        tempmsg = ""
        while not kill_flag():
            try:
                c = chr(self.socket_stream.ReadByte())
                tempmsg += c
                if c == '&':
                    self.received_msg = tempmsg
                    self.msghistory.append(tempmsg[:-1])
                    tempmsg = ""
                    for comp in comps():
                        comp.ExpireSolution(True)
            except:
                self.received_msg = "Server: Client was inactive for too long  or ended connection: Thread Stopped.."
                for comp in comps():
                    comp.ExpireSolution(True)
                break
    
    def log(self):
        return "###Report###", "\tIPENDP > ", self.myip, "\tCLIENT > ", self.client, "\tSTREAM > ", self.socket_stream, self.rmsg

class MyComponent(component):
    Reset = False
    
    def RunScript(self, IP, port, run_server, server_mode, Reset, TimeOut):
        """Provides a scripting component.
            Inputs:
                x: The x script variable
                y: The y script variable
            Output:
                a: The a output variable"""
        
        __author__ = "Arman Khalilbeigi"
        __version__ = "2022.06.15"
        
        if TimeOut == None:
            TimeOut = 1000000
        if Reset == None:
            Reset = False
        if IP == None:
            IP = '127.0.0.1'
        
#        try:
#            self.tcp_server = Test(IP, port, TimeOut, ghenv.Component, server_mode)
#        except:
#            self.Message = 'UnkownError: Cannot Create Tcp Server!'
        if (not run_server) or (not self.tcp_server):
            self.tcp_server = Test(IP, port, TimeOut, self, server_mode)
            self.Message = "Stopped"
            self.tcp_server.log()
            return
        
        if not (self.tcp_server.client and self.tcp_server.socket_stream):
            self.tcp_server.connect()
            self.Message = "Waiting" if server_mode else "Connecting"
        else:
            self.tcp_server.receiver_thread_start()
            self.Message = "Receiving"
            self.tcp_server.rmsg =  "Connection Exists".center(100, '-')

        ConData = self.tcp_server
        Log = self.tcp_server.log()
        
        if Reset and run_server == False :
            try:
                self.tcp_server.clean_up()
                return
            except:
                pass
        return (Log, ConData )

