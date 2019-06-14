#!/bin/bash

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -agent|--agent)
    agent="$2"
    shift # past argument
    shift # past value
    ;;
    -user|--user)
    user="$2"
    shift # past argument
    shift # past value
    ;;
    -password|--password)
    password="$2"
    shift # past argument
    shift # past value
    ;;
    --default)
    DEFAULT=YES
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

###Connect via ssh to agent###
apt-get install sshpass
sshpass -p $password ssh -t -o StrictHostKeyChecking=no $user@$agent << EOF

###Install libraries###
apt-get install python3-pip;

libsList=("pyyaml" "requests" "argparse" "psutil" "psutil")
for lib in ${libsList[@]}; do
    pip3 install $lib
done
###Set python3 as interpretor
sh /local/rc-stop/velocity-agent;
sed -i -e 's/python2.7/python3/g' /local/agent/velocity-agent/configuration/script.interpreters.ini;
sed -i -e 's/--extensibleAuto/--extensibleLanguages \/local\/agent\/velocity-agent\/configuration\/script.interpreters.ini/g' /local/rc-start/velocity-agent;
sh /local/rc-start/velocity-agent;
EOF