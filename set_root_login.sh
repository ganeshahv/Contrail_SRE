root@ip-192-168-1-235:/home/ubuntu# cat set_root_login.sh
#!/bin/bash
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
echo root:contrail123 | chpasswd
service sshd restart
