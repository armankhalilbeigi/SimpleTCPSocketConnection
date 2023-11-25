import rhinoscriptsyntax as rs
#import System.Net as net




if ConData:
    if not ghenv.Component in ConData.receiver_list:
        ConData.receiver_list.append(ghenv.Component)


    if ClearMsgHistory == False:
        RcvMsg= ConData.received_msg[:-1]
        #ConData.msghistory.append(RcvMsg)
    if ClearMsgHistory == True:
        ConData.msghistory = []
    MsgHistory = ConData.msghistory