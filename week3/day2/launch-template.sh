#!/bin/bash
sleep 30  # Wait for system to initialize

# Log current directory
pwd > /home/ec2-user/install-logs.txt

# Install Git
sudo yum install git -y

#Install python and venv 

sudo yum update -y
sudo yum install python3 python3-pip -y

# Clone repository
cd /home/ec2-user
git clone https://github.com/ste777V6/DevopsBootcamp2026.git

# Navigate to app directory
cd DevopsBootcamp2026/week3/day2/app

# Make script executable and run
sudo chmod u+x run.sh
sudo ./run.sh
#Important: No Nginx needed! ALB handles reverse proxy.