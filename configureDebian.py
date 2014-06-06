#!/usr/bin/python

import os

print '''
Debian Linux Linode configuration script
Copyright (c) 2014 Sasha Pavelovich
Freely available under the MIT license \n
'''

#Configure hostname

print 'Configure hostname: \n'
hostname = raw_input('Enter the hostname for the Linode > ')
linodeDomain = raw_input('Enter the domain hostname for reverse DNS > ')
linodeIP = raw_input('Enter the IP address of the Linode > ')

os.system('echo "'+hostname+'" > /etc/hostname')
os.system('hostname -F /etc/hostname')

hostsFile = open('/etc/hosts', 'a')
hostsFile.write('+linodeIP+'      '+linodeDomain+'        '+hostname+')
hostsFile.close()

print 'Configured '+hostname+' and '+linodeDomain+' as the Linode hostname for'+linodeIP+' \n \n '

#Update packages

print 'Updating package list... \n'
print os.system('apt-get update')
print 'Upgrading packages... \n'
print os.system('apt-get upgrade')

#Create new administrator account

adminName = raw_input('Enter the name of the adminstrator user > ')
print 'Installing sudo... \n '
print os.system('apt-get install sudo')
print 'sudo installed \n '
os.system('adduser '+adminName)
os.system('usermod -a -G sudo '+adminName)
print 'Added administrator user '+adminName

#Configure firewall

firewallRules = open('/etc/iptables.firewall.rules', 'w')
firewallRules.write('''
*filter

#  Allow all loopback (lo0) traffic and drop all traffic to 127/8 that doesn't use lo0
-A INPUT -i lo -j ACCEPT
-A INPUT -d 127.0.0.0/8 -j REJECT

#  Accept all established inbound connections
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

#  Allow all outbound traffic - you can modify this to only allow certain traffic
-A OUTPUT -j ACCEPT

#  Allow HTTP and HTTPS connections from anywhere (the normal ports for websites and SSL).
-A INPUT -p tcp --dport 80 -j ACCEPT
-A INPUT -p tcp --dport 443 -j ACCEPT

#  Allow SSH connections
#
#  The -dport number should be the same port number you set in sshd_config
#
-A INPUT -p tcp -m state --state NEW --dport 22 -j ACCEPT

#  Allow ping
-A INPUT -p icmp -j ACCEPT

#  Log iptables denied calls
-A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables denied: " --log-level 7

#  Drop all other inbound - default deny unless explicitly allowed policy
-A INPUT -j DROP
-A FORWARD -j DROP

COMMIT
''')
firewallRules.close()

os.system('iptables-restore < /etc/iptables.firewall.rules')
firewallStarter = open('/etc/network/if-pre-up.d/firewall', 'w')
firewallStarter.write('''
#!/bin/sh
/sbin/iptables-restore < /etc/iptables.firewall.rules
''')
firewallStarter.close()
os.system('chmod +x /etc/network/if-pre-up.d/firewall')

os.system('apt-get install fail2ban')

#After installation activities

print '''
Installation from script complete
To finish configuring your Linode, please do the following:

*Run "dpkg-reconfigure tzdata" to set the timezone of the Linode
*Upload SSH keys
*Secure SSH login
**Open /etc/ssh/sshd_config
**Set "PasswordAuthentication no" and "PermitRootLogin no"
**Run "service ssh restart" to activate the changes
*Optionally run the script for configuring web services
'''
