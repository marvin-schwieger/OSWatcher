import tkinter as tk
from tkinter import messagebox
import datetime
import time
import os
import platform 
import socket 
import ipaddress
import json

class AgentGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OS AGENT")
        self.geometry("600x230")

        self.ip_var = tk.StringVar()
        self.port_var = tk.StringVar()
        self.interval_var = tk.StringVar()

        # Store validated values here
        self.valid_ip = None
        self.valid_port = None
        self.valid_interval = None

        self._configure_grid()
        self._create_widgets()

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)

    def _create_widgets(self):
        server_label = tk.Label(self, text="SERVER IP:", font=("calibre", 16, "bold"), anchor="w")
        port_label = tk.Label(self, text="SERVER PORT:", font=("calibre", 16, "bold"), anchor="w")
        interval_label = tk.Label(self, text="INTERVAL IN H:", font=("calibre", 16, "bold"), anchor="w")
        
        server_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        port_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        interval_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.server_entry = tk.Entry(self, textvariable=self.ip_var, font=("calibre", 16, "normal"))
        self.port_entry = tk.Entry(self, textvariable=self.port_var, font=("calibre", 16, "normal"))
        self.interval_entry = tk.Entry(self, textvariable=self.interval_var, font=("calibre", 16, "normal"))

        self.server_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.port_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.interval_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        start_button = tk.Button(
            self,
            text="START", 
            font=("calibre", 16, "bold"), 
            bg="green", 
            fg="white", 
            activebackground="darkgreen", 
            command=self._handle_start
        )
        
        start_button.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
    def _handle_start(self):
        ip_input = self.ip_var.get().strip()
        port_input = self.port_var.get().strip()
        interval_input = self.interval_var.get().strip()

        # Validate IP
        try:
            self.valid_ip = ipaddress.ip_address(ip_input)      # type IPv4Address
            self.valid_ip = str(self.valid_ip)                  # cast to str for connect function
        except ValueError:
            messagebox.showerror("Error", "Invalid IP address! Please enter a valid IPv4 or IPv6 address.")
            return
        
        # Validate port
        try:
            self.valid_port = int(port_input)
        except ValueError:
            messagebox.showerror("Error", "Port must be type Integer.")
            return

        # Validate interval
        try:
            self.valid_interval = int(interval_input)
            if not (1 <= self.valid_interval <= 23):
                raise ValueError("Interval out of range")
        except ValueError:
            messagebox.showerror("Error", "Interval must be a number between 1 and 23.")
            return

        # Start Agent: Yes / No 
        statement = messagebox.askyesno(
            title="STARTING AGENT",
            message=f"Valid input received!\n\nDo want to send data to Server {self.valid_ip} on Port {self.valid_port} every {self.valid_interval} hours?"
        )

        if statement:
            self.destroy()
            return 
    
    # Getter         
    def get_ip(self) -> str:
        return self.valid_ip
    
    def get_interval(self) -> int:
        return self.valid_interval
    
    def get_port(self) -> int:
        return self.valid_port
    
# Get actual IP address by connecting to a public DNS server
# This is a workaround to avoid getting VirtualBox host-only IP 
def get_actual_ip() -> str:

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    
    return ip

def get_os_info() -> str:
    t = datetime.datetime.now()
    t = t.strftime("%c")
    hostname = socket.gethostname()

    dic = {
        "dest": hostname,
        "dest-ip": get_actual_ip(),
        "user": os.getlogin(),
        "time": t,
        "os": platform.system(),
        "os-version": platform.version()        
    }
    # Convert into JSON aka String
    json_string = json.dumps(dic)
 
    return json_string

def connect(server_addr) -> socket.socket:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_addr)
    return client

if __name__ == "__main__":
    agent = AgentGUI()
    agent.mainloop()
    
    # Getter
    server_addr: tuple = (agent.get_ip(), agent.get_port())
    server_interval: int = agent.get_interval()
    print(get_os_info())
    
    # Establish a connection Try / Except is internally handled in connect function
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_addr)
    print("[CONNECTED] to ", server_addr)

    while True:
        
        msg = get_os_info().encode("utf-8")
        client.send(msg)
        print("[INFO] Data sent to server.")  
        
        # Wait for server response
        response = client.recv(1024)
        if response:
            print("[SUCCESS] Server response:", response.decode("utf-8"))
            time.sleep(server_interval)
        else:
            print("[ERROR] No response from server. Closing connection.")
            break
    
    client.close()
        
