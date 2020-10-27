# Fetch Rewards Coding Exercise
This exercise uses Boto3 which is a Amazon Web Services (AWS) SDK for Python. It enables Python developers to create, configure, and manage AWS services. This exercise takes a YAML configuration file as input and,
- Deploys a Linux AWS EC2 instance
- Configures it with two EBS volumes
- Configures two user accounts on the EC2 instance for SSH

## System Requirements
- Python 3.8

## Python Dependencies
- pyyaml - PyYAML is a YAML parser and emitter for Python
- boto3  - Amazon Web Services (AWS) SDK for Python

## Package Prerequisites
- Create a YAML configuration file as input to the application. A sample configuration file is provided for reference as part of this package (ec2_config.yaml)
- Use existing SSH keys for two users or generate new keys via ssh-keygen command. Command for reference is below. For complete instructions, please refer this URL -  https://www.ssh.com/ssh/keygen/. Once the keys are created, paste them in the ec2_config.yaml file as inputs to the ssh_key property for each user.
```console
(venv) $ ssh-keygen -t rsa -b 4096
```
- Create and configure AWS IAM keys (if not already setup) under the default profile. For detailed instructions, please refer this document - https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey_CLIAPI
```console
(venv) $ aws iam create-access-key      # Creates a new IAM secret access key
(venv) $ aws configure                  # Configure a default profile on work station
```


## Local Development
A dedicated Python virtual environment is highly recommended for this project to isolate Python dependencies from your system's Python installation and from other Python projects. Instructions to install and setup a Python virutal environment can be found here - https://sourabhbajaj.com/mac-setup/Python/virtualenv.html

For local developement within a virtual environment, use commands listed below:

```console
(venv) $ git clone 
(venv) $ pip install -r requirements.txt
(venv) $ python3 ec2_setup.py
```

## Package Usage Instructions
NOTE: Below are notes regarding existing configurations for this application. Please refer this document for configuring specific values for below listed properties and more - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.ServiceResource.create_instances
- Details of subnet-id, security groups are being passed by default. An EC2 instance will be created in the default VPC public subnets and assigned the default security group. Please ensure inbound traffic on port 22 for SSH from your work station is enabled in the default security group prior to connecting.
- EC2 instance is launched without a key pair. If SSH key's are passed in ec2_config.yaml, use the private key to SSH to the instance.

1. Running the application as shown below will create an EC2 instance in the AWS region and account per the default AWS configuration on your work station.
    ```console
    (venv) spamu00@USPLSSPAMULLM1 ~/WS/Fetch $ python3 ec2_setup.py 
    3.14.136.100                      # EC2 Instance Public IP to SSH
    ```
2. SSH to the instance as user1. Sample output below.
    ```console
    (venv) spamu00@USPLSSPAMULLM1 ~/WS/Fetch $ ssh -i ~/.ssh/user1 user1@3.14.136.100
    Last failed login: Mon Oct 26 23:38:37 UTC 2020 from c-73-202-140-32.hsd1.ca.comcast.net on ssh:notty
    There were 3 failed login attempts since the last successful login.

        __|  __|_  )
        _|  (     /   Amazon Linux 2 AMI
        ___|\___|___|

    https://aws.amazon.com/amazon-linux-2/
    89 package(s) needed for security, out of 376 available
    Run "sudo yum update" to apply all updates.
    [user1@ip-172-31-7-253 ~]$    
    ``` 

3. SSH to the instance as user2. Sample output below.
    ```console
    (venv) spamu00@USPLSSPAMULLM1 ~/WS/Fetch $ ssh -i ~/.ssh/user2 user2@3.14.136.100
    Last failed login: Mon Oct 26 23:37:29 UTC 2020 from c-73-202-140-32.hsd1.ca.comcast.net on ssh:notty
    There was 1 failed login attempt since the last successful login.

        __|  __|_  )
        _|  (     /   Amazon Linux 2 AMI
        ___|\___|___|

    https://aws.amazon.com/amazon-linux-2/
    89 package(s) needed for security, out of 376 available
    Run "sudo yum update" to apply all updates.
    [user2@ip-172-31-7-253 ~]$
    ```
4. Write data to the root volume and read from it. Sample output below.
    ```console
    [user2@ip-172-31-7-253 ~]$ touch root_vol_user2.txt
    [user2@ip-172-31-7-253 ~]$ vim root_vol_user2.txt 
    [user2@ip-172-31-7-253 ~]$ cat /home/user2/root_vol_user2.txt 
    File on the root volume.
    ```
5. Read data from the root volume and /data mount. Sample output below.
    ```console
    [user2@ip-172-31-7-253 ~]$ sudo cp root_vol_user2.txt data_vol_user2.txt 
    [user2@ip-172-31-7-253 ~]$ vim data_vol_user2.txt
    [user2@ip-172-31-7-253 data]$ cat /data/data_vol_user2.txt 
    File on the data volume.   
    ```