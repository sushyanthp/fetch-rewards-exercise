#!/usr/local/bin/python3

"""
This exercise takes a YAML configuration file as input and,
- Deploys a Linux AWS EC2 instance
- Configures it with two EBS volumes
- Configures two user accounts on the EC2 instance for SSH

It uses Boto3 which is a Amazon Web Services (AWS) SDK for Python.
"""

import yaml
import boto3
import random

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')


def read_yaml():
    """ This function is used to read the input file written in YAML (ec2_config.yaml) and return a dictionary object.
    """
    with open("./ec2_config.yaml", 'r') as file:
        try:
            return(yaml.safe_load(file))
        except yaml.YAMLError as exc:
            print(exc)


def get_user_volume_details(ec2_config_dict):
    """ This function parses the dictionary from input and returns required user and volume information from it.
    """
    for key, value in ec2_config_dict.items():
        # Parsing Users Information
        users_info = value['users']
        user1_login = users_info[0]['login']
        user1_key = users_info[0]['ssh_key']

        user2_login = users_info[1]['login']
        user2_key = users_info[1]['ssh_key']

        volumes_info = value['volumes']
        datavol_device = volumes_info[1]['device']
        datavol_type = volumes_info[1]['type']
        datavol_mount = volumes_info[1]['mount']

        return(user1_login, user1_key, user2_login, user2_key, datavol_device, datavol_type, datavol_mount)


def get_ami_id(ami_type, architecture, root_device_type, virtualization_type, device_name, root_volume_size):
    """ This function called during the EC2 instance creation call is responsible for returning a random AMI Id 
    satisfying the requirements in input like architecture, owner, virtualization type and root volume type.
    """
    response = ec2_client.describe_images(
        ExecutableUsers=[
            'all',
        ],
        Filters=[
            {
                'Name': 'architecture',
                'Values': [
                        architecture,
                ]
            },
            {
                'Name': 'root-device-type',
                'Values': [
                        root_device_type,
                ]
            },
            {
                'Name': 'virtualization-type',
                'Values': [
                        virtualization_type,
                ]
            },
            {
                'Name': 'is-public',
                'Values': [
                        "true",
                ]
            },
            {
                'Name': 'block-device-mapping.device-name',
                'Values': [
                        device_name,
                ]
            },
        ],
        Owners=[
            'amazon',
        ]
    )

    image_list = []
    for image_info in response['Images']:
        for device_details in image_info['BlockDeviceMappings']:
            if device_details['Ebs']['VolumeSize'] <= root_volume_size:
                if ami_type in image_info['Name']:
                    image_list.append(image_info['ImageId'])
    return(random.choice(image_list))


def ec2_instance_setup(ec2_config_dict, user_data):
    """ This function parses the dictionary from input and utilizes the user_data script to create an EC2 instance
    and returns the EC2 instance' public IP upon creation.
    """
    for key, value in ec2_config_dict.items():
        volumes_info = value['volumes']

        instance = ec2.create_instances(
            BlockDeviceMappings=[
                {
                    'DeviceName': volumes_info[0]['device'],
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': volumes_info[0]['size_gb']
                    }
                },
                {
                    'DeviceName': volumes_info[1]['device'],
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': volumes_info[1]['size_gb']
                    }
                },
            ],
            ImageId=get_ami_id(value['ami_type'], value['architecture'], value['root_device_type'],
                               value['virtualization_type'], volumes_info[0]['device'], volumes_info[0]['size_gb']),
            InstanceType=value['instance_type'],
            MaxCount=value['min_count'],
            MinCount=value['max_count'],
            UserData=user_data,
            NetworkInterfaces=[
                {
                    'AssociatePublicIpAddress': True,
                    'DeleteOnTermination': True,
                    'Description': 'Public IP associated with Fetch DevOps EC2',
                    'DeviceIndex': 0
                },
            ],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'Fetch_DevOps_EC2'
                        },
                        {
                            'Key': 'Project',
                            'Value': 'Fetch_Hiring_Take_Home_Assignment'
                        },
                        {
                            'Key': 'Platform',
                            'Value': 'Fetch'
                        }
                    ]
                },
            ]
        )
    ec2_instance = instance[0]
    ec2_instance.wait_until_running()
    ec2_instance.load()
    return(ec2_instance.public_ip_address)


def main():
    """ Main function to call individual methods of this application and return the IP address of the EC2 instance
    created for users to connect to.
    """
    ec2_config_dict = read_yaml()
    (user1_login, user1_key, user2_login,
     user2_key, datavol_device, datavol_type, datavol_mount) = get_user_volume_details(ec2_config_dict)

    user_data = '''
#!/bin/bash -x
USER1={0}
adduser $USER1
echo "$USER1 ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/cloud-init
mkdir /home/$USER1/.ssh
echo {1} >> /home/$USER1/.ssh/authorized_keys

USER2={2}
adduser $USER2
echo "$USER2 ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/cloud-init
mkdir /home/$USER2/.ssh
echo {3} >> /home/$USER2/.ssh/authorized_keys

DEVICE={4}
FILESYSTEM={5}
MOUNT={6}
sudo mkdir -p $MOUNT
sudo mkfs -t $FILESYSTEM $DEVICE
sudo mount $DEVICE $MOUNT
df -hT
'''
    user_data_params = user_data.format(
        user1_login, user1_key, user2_login, user2_key, datavol_device, datavol_type, datavol_mount)

    print(ec2_instance_setup(ec2_config_dict, user_data_params))


if __name__ == "__main__":
    main()
