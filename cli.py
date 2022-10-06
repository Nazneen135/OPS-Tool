Final ops-tool cli





#!/usr/bin/env python



import logging

import argparse

import json

import os

import subprocess

import time

# import socket



import getpass

import datetime

import re

import sys

from six.moves import input



parent_parser = argparse.ArgumentParser()

sub_parser = parent_parser.add_subparsers(title="Commands", dest='command', description='Available commands for '

                                                                                        'this tool')

sub_parser.add_parser('list', help='list registered scripts')



sub_parser2 = sub_parser.add_parser('exec', help='execute registered script, please enter script\'s alias name')

sub_parser2.add_argument('--script', help='enter the script\'s alias', required=True)

sub_parser2.add_argument('--node', help='enter the node\'s ip where you want to execute', required=True)

sub_parser2.add_argument('--scriptargs', help='enter the script argument\'s where you want to execute')



args = parent_parser.parse_args()



FORMAT = '%(asctime)-15s  %(user)-8s %(operationName)-8s %(message)s'

logging.basicConfig(format=FORMAT)

d = {'user': 'ops', 'operationName': 'exec'}

logger = logging.getLogger('tcpserver')

logger.warning('Protocol problem: %s', 'connection reset', extra=d)





def upload(filename, ip):

    upload.has_been_called = True

    newScName = datetime.datetime.now().strftime('{f}_{user}_%d-%m-%Y_%H_%M{ext}').format(

        f=os.path.splitext(filename)[0], user=getpass.getuser(), ext=os.path.splitext(filename)[1])

    with open('/root/ops-tool/scripts/{f}'.format(f=filename), 'r') as rf:

        with open("/tmp/{f}".format(f=newScName), 'w') as wf:

            for line in rf:

                wf.write(line)

    print('Uploading script: {filename} to remote host:{ip}'.format(filename=newScName, ip=ip))

    result = os.system('sudo scp -i /root/opc_rsa /tmp/{f} opc@{ip}:/tmp/'.format(f=newScName, ip=ip))

    print("Result value found is: ", result)

    if (result):

        raise Exception("upload script failed")

    # os.system('sudo rm -f /tmp/{f}'.format(f=newScName))

    time.sleep(3)

    return newScName





def execute(filename, ip, scriptarg):

    if filename.endswith(".sh"):

        print('Executing Bash script: {filename} on remote host:{ip}'.format(filename=filename, ip=ip))

        ssh = subprocess.Popen(

            "sudo ssh -i /root/opc_rsa opc@{host} {cmd}".format(host=ip, cmd='sudo bash /tmp/%s' % filename),

            shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        print(ssh[0].replace('\\n', '\n'))



    elif filename.endswith(".jar"):

        path = {}

        print('Executing Java script: {filename} on remote host:{ip}'.format(filename=filename, ip=ip))

        #tmp = 'sudo java -jar /tmp/' + filename

        #print("Executing " + tmp)

        #cmd = "sudo ssh -i /root/opc_rsa opc@" + ip + "  " + tmp

        #print(cmd)

        command = "sudo java -jar /tmp/{0}".format(filename)

        ssh = subprocess.Popen(

            "sudo ssh -i /root/opc_rsa opc@{host} {cmd}".format(host=ip, cmd=command),

            # "sudo ssh -i /root/opc_rsa opc@10.0.40.4  java -jar /tmp/repository-ops-util-0.0.1.jar",



            shell=True, stderr=subprocess.PIPE).communicate()

        print(ssh[0].replace('\\n', '\n'))



    elif filename.endswith(".py"):

        print('Executing Python script: {filename} on remote host:{ip}'.format(filename=filename, ip=ip,

                                                                               scriptarg=scriptarg))

       # tmp = 'sudo python  /tmp/' + filename + " " + scriptarg

        #print("Executing " + tmp)

        #sudo python /tmp/getkiev_opc_17-03-2021_09:49.py

        command = "sudo python /tmp/{0} {1}".format(filename, scriptarg)

        ssh = subprocess.Popen(

            "sudo ssh -i /root/opc_rsa opc@{host} {cmd}".format(host=ip, cmd=command),

            shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        print(ssh[0].replace('\\n', '\n'))

        time.sleep(3)





def download(outputPath, ip):

    print('Downloading generated artifacts:{output} back to jump host'.format(output=outputPath))

    os.system('sudo scp -i /root/opc_rsa opc@%s:%s /tmp/ops-tool-output/' % (node, outputPath))

    time.sleep(3)





def delete(filename, ip):

    filePrefix = re.split('(\\d+)', filename)[0]

    #print(filePrefix)

    print('Deleting script: {filename} from Jump Host and remote host: {ip}'.format(filename=filename, ip=ip))

    #os.system('find /tmp/%s* -exec rm {} \\;' % filename)

    #command = 'sudo find /tmp/%s* -mmin +1 -exec rm {} \\;'.format(filename)

    #qq = 'sudo rm /tmp/{0}*'.format(filePrefix)

    #print(qq)

    command = 'sudo rm /tmp/{0}*'.format(filePrefix)

    subprocess.Popen("sudo ssh -i /root/opc_rsa opc@{host} {cmd}".format(host=ip,

                                                                         cmd=command),

                     shell=True, stderr=subprocess.PIPE).communicate()

    time.sleep(3)





if not os.path.exists('/tmp/ops-tool-output/'):

    os.mkdir('/tmp/ops-tool-output/')



if args.command == 'list':

    print('Below are the available scripts to execute')

    with open('/root/ops-tool/scripts.json') as f:

        data = json.load(f)

        for i in data['scripts']:

            print('Alias: {alias} ; Artifact Location : {output}'.format(alias=i['alias'], output=i['artifact']))



if args.command == 'exec':

    script = args.script

    node = args.node

    scriptargs = args.scriptargs

    # jhostIp = socket.gethostbyname(socket.gethostname())

    upload.has_been_called = False

    file = []

    with open('/root/ops-tool/scripts.json') as f:

        data = json.load(f)

    for i in data['scripts']:

        try:

            if script == i['alias']:

                newScript = upload(filename=i['filename'], ip=node)

                execute(filename=newScript, ip=node, scriptarg=scriptargs)

                download(outputPath=i['artifact'], ip=node)

                delete(filename=newScript, ip=node)

                print('Execution Completed!')

            else:

                file.append(i['alias'])

        except Exception as ex:

            print(ex)

            sys.exit(-1)

    if not upload.has_been_called and script not in file:

        print("Alias entered is wrong, Please enter correct Alias name in --script switch")


