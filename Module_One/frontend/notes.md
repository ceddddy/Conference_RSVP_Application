## Building the frontend

- aws ec2 create-security-group --group-name RSVPWebServerSG --description "Security group for web server" --region us-east-2

- aws ec2 authorize-security-group-ingress --group-id sg-0a29e9d4fcb9c49e6 --protocol tcp --port 80 --cidr 0.0.0.0/0 --region us-east-2

- aws ec2 authorize-security-group-ingress --group-id sg-0a29e9d4fcb9c49e6 --protocol tcp --port 22 --cidr 0.0.0.0/0 --region us-east-2

- aws ec2 run-instances \
  --image-id ami-04f167a56786e4b09 \
  --instance-type t2.micro \
  --key-name RSVssh \
  --security-group-ids sg-0a29e9d4fcb9c49e6 \
  --region us-east-2 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=RSVP-Web-Server}]'

  - aws ec2 describe-instances --instance-ids i-060b4d3b4130e833a --region us-east-2 --query 'Reservations[].Instances[].{PublicIp:PublicIpAddress,PublicDns:PublicDnsName}'

## Access the server and add the html file to the server that has apache installed

  - chmod 400 "RSVssh.pem"
  - ssh -i "RSVssh.pem" ubuntu@ec2-3-144-34-102.us-east-2.compute.amazonaws.com

  - sudo apt update -y
sudo apt install apache2 -y
sudo systemctl start apache2
sudo systemctl enable apache2
Verify: Run sudo systemctl status httpd/apache2 for ubuntu  to ensure Apache is active.

- scp -i RSVssh.pem /Users/drich/Desktop/aws-apprunner-rsvp-workshop/Module_One/frontend/index.html ubuntu@3.144.34.102:/home/ubuntu/index.html
index.html                                    100%   14KB  44.7KB/s   00:00

- sudo mv /home/ubuntu/index.html /var/www/html/index.html  (Moves the index.html file from the home directory to Apache’s default web root: /var/www/html/.)

- sudo chown www-data:www-data /var/www/html/index.html  (Sets the owner and group of the file to www-data, which is the user Apache runs as on Ubuntu.

This allows Apache to read and serve the file without permission issues.)

- sudo chmod 644 /var/www/html/index.html  (Sets file permissions to:

Owner (www-data) can read and write.

Group and others can only read.

This is standard for web files so they are publicly viewable but not modifiable.)

