# SimpleTCPSocketConnection
a simple connection created for McNeel's Grasshopper3D

---
A. Connection Start: With this function, both the client and server are started based on a Boolean input
to determine whether the output should be the client or the server. Other inputs are time-out (a time
limit (in milliseconds) to disconnect in case of inactivity), IP, Port, Reset (performs a clean-up to dispose
of the remaining threads), and Run.
B. Listener: Retrieves the incoming messages from other connected elements.
C. Sender: Sends outgoing messages to other connected elements.
