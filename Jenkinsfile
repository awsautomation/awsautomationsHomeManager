node ('Docker-EC2'){
    def app
    try {
        stage ('Checkout SCM') {
            checkout scm
        }
        stage ('Build Packer') {
            sh '''#!/bin/bash
            cd $WORKSPACE/Approvals
            sudo packer validate packer.json

            LOGSTOUTTEST=`aws ssm get-parameters --names LOGSOUTTEST --region us-east-1 --with-decryption --profile hardening | jq \'.Parameters[] | select(.Name=="LOGSOUTTEST").Value\' -r`
            LOGSENVIRONMENT=`aws ssm get-parameters --names LOGSENVIRONMENT --region us-east-1 --with-decryption --profile hardening | jq \'.Parameters[] | select(.Name=="LOGSENVIRONMENT").Value\' -r`
            NEWRELICLICENSEKEY=`aws ssm get-parameters --names NEWRELICLICENSEKEY --region us-east-1 --with-decryption --profile hardening | jq \'.Parameters[] | select(.Name=="NEWRELICLICENSEKEY").Value\' -r`


            cat $WORKSPACE/Approvals/ansible/src/filebeat.yml.j2 | sed "s@\\$LOGSOUTTEST@$LOGSTOUTTEST@g;s@\\$LOGSENVIRONMENT@$LOGSENVIRONMENT@g" > $WORKSPACE/Approvals/ansible/src/tmp/filebeat.yml.j2
            cat $WORKSPACE/Approvals/ansible/src/newrelic-infra.yml.j2 | sed "s@\\$NEWRELICLICENSEKEY@$NEWRELICLICENSEKEY@g" > $WORKSPACE/Approvals/ansible/src/tmp/newrelic-infra.yml.j2

            if [ $? -eq "0" ]
            then
        	    packer build -debug packer.json | tee output.txt
            else
        	    echo "This is not a valid packer.json file"
            fi

            tail -2 output.txt | head -2 | awk \'match($0, /ami-.*/) { print substr($0, RSTART, RLENGTH) }\' > $WORKSPACE/ami.txt

            if [ $(cat $WORKSPACE/ami.txt | grep "ami-") ]
            then
        	    export AMI=`cat $WORKSPACE/ami.txt`
            else
        	    echo -e "There is an issue with the AMI creation\\n"
                exit 1
            fi'''
                }
        stage ('AMI Hardening') {
            sh '''#!/bin/bash

            SG="sg-0246dfed862de1813"
            INSTANCETYPE="t2.micro"
            REGION="us-east-1"
            KEY="hardening"
            PROFILE="hardening"
            SUBNETID="subnet-fbf6c0d4"
            AMI=`cat $WORKSPACE/ami.txt`

            echo "Launching new instance from Packer AMI - $AMI..\\n"

            INSTANCEID=`aws ec2 run-instances --image-id $AMI --count 1 --key hardening --security-group-ids $SG --instance-type $INSTANCETYPE --region $REGION --subnet-id $SUBNETID --user-data file://$WORKSPACE/Approvals/userdata-lynis --profile $PROFILE | jq \'.Instances[].InstanceId\' -r`

            aws ec2 wait instance-running --instance-ids $INSTANCEID --region $REGION --profile $PROFILE

            aws ec2 create-tags --resources $INSTANCEID --tags Key=env,Value=ecs Key=type,Value=hardening Key=Customer,Value=global --region $REGION --profile $PROFILE

            IP=`aws ec2 describe-instances --region $REGION --instance-id $INSTANCEID --profile $PROFILE | jq \'.Reservations[].Instances[].NetworkInterfaces[].Association.PublicIp\' -r`

            aws ec2 associate-iam-instance-profile --iam-instance-profile Name=PackerSSM --instance-id $INSTANCEID  --profile $PROFILE --region $REGION

            sleep 60

            ssh -i /home/jenkinsauto/.ssh/hardening -o "StrictHostKeyChecking no" ec2-user@$IP \'sudo lynis audit system; sudo cp /var/log/lynis.log /tmp/; sudo cp /var/log/lynis-report.dat /tmp/; sudo chmod 777 /tmp/lynis.log /tmp/lynis-report.dat\'
            scp -i /home/jenkinsauto/.ssh/hardening -o "StrictHostKeyChecking no" ec2-user@$IP:/tmp/lynis.log $WORKSPACE
            scp -i /home/jenkinsauto/.ssh/hardening -o "StrictHostKeyChecking no" ec2-user@$IP:/tmp/lynis-report.dat $WORKSPACE

            aws inspector start-assessment-run --region $REGION --assessment-template-arn arn:aws:inspector:us-east-1:298246898045:target/0-DmfeRtRQ/template/0-ATmUKOvY --profile $PROFILE'''

        }
    } catch (err) {
        currentBuild.result = 'FAILED'
        throw err
    }
}