import rhinoscriptsyntax as rs
import System.Net as net
from System import Array, Byte

msgbazak = str(MsgtoSend) + '&'
if send:
    msg = Array[Byte](bytearray(msgbazak))
    ConData.socket_stream.Write(msg, 0, msg.Length)