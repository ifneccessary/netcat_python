import sys,socket,threading,argparse,subprocess,shlex
class NetCat():
 def __init__(self,args):
  self.args=args
  self.sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  self.sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
 
 def run(self):
  if self.args.listen:
     self.listen()
  else:
     self.chat()      
 
 def listen(self):
    print(self.args.port)
    self.sk.bind((self.args.source,int(self.args.port)))
    self.sk.listen(5)
    print(f"Listening on {self.args.source}:{self.args.port}...")
    while True:
      conn,addr=self.sk.accept()
      print(f"Connection is estabilished with System: {addr}")
      self.handle(conn)
 
 def handle(self,sock):
  if self.args.upload:
    file=self.args.upload
    data=b""
    while True:
      recvd=sock.recv(4064)
      fetched=len(recvd)
      data+=recvd
      if fetched<4064:
       break
    with open(f"{file}","+w") as f:
     f.write(data.decode())    
    print(f"uploaded to file {file}")
    sys.exit()
  elif self.args.execute:
    cmd=self.args.execute
    output=subprocess.run(shlex.split(cmd),capture_output=True).stdout
    sent=0
    total=len(output)
    while True:
     sent=sock.send(output[sent:])
     if not (sent<total):
       break
    sock.close()
    print(f"{cmd} has been executed and sent to the remote system... \n")
    sys.exit()      
    
 def chat(self):
   try:
    self.sk.connect((self.args.target,self.args.port))
    print(f"Connection Estabilished with {self.args.target}")
   except ConnectionError:
     print(f"Connection could be estabilished")
     exit() 
   snd=threading.Thread(target=self.send_log,args=())
   rcv=threading.Thread(target=self.recv_log,args=())
   snd.start()
   rcv.start()
 def send_log(self,data=None):
   if not data:
     while True:
      data=input(">> ")
      total=len(data)
      on_wire=0
      on_wire+=self.sk.send(data.encode())
      while on_wire<total:
       on_wire+=self.sk.send(data[on_wire:].encode())
   else:
     total=len(data.encode())
     on_wire=0
     on_wire+=self.sk.send(data)
     while on_wire<total:
       on_wire+=self.sk.send(data[on_wire:])   

 def recv_log(self,mode="interactive"):
   while True:
    data=b""
    recvd_bytes=self.sk.recv(4064)
    data+=recvd_bytes
    while recvd_bytes==4064:
        recvd_bytes=self.sk.recv(4064)
        data+=recvd_bytes
    data=data.decode()
    if mode=="interactive":  
     print(f"Remote System: {data}\n")
    else: 
     return data  
 def execute(self,cmd):
   return subprocess.run(shlex.split(cmd),capture_output=True,stderr=subprocess.STDOUT).stdout

if __name__=='__main__':
 parser=argparse.ArgumentParser(
  description="...nc linux utility with python..."
 )
 parser.add_argument("-e","--execute")
 parser.add_argument("-t","--target")
 parser.add_argument("-l","--listen",action="store_true")
 parser.add_argument("-p","--port",type=int, required=True)
 parser.add_argument("-u","--upload", help="File name")
 parser.add_argument("-s","--source",default='0.0.0.0',help="Source IP for listener")
 parser.add_argument("-rsh","--reverse_shell",help="enables reverse shell options",action="store_true")
 parser.add_argument("-rp","--remote_port",help="remote port on attacker to get shell",type=int)
 parser.add_argument("-rip","--remote_ip",help="remote ip adress on attacker to get shell")

 args=parser.parse_args()
 nc=NetCat(args=args)
 nc.run()


# create dummy hackingtool whichinvoles reverseshell.