from __future__ import print_function
import json
import boto3
import logging
import time
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    ids = []

    try:
        print(event)
        region = event['region']
        logger.info('region: ' + str(region))
        detail = event['detail']
        state = detail['responseElements']['instancesSet']['items'][0]['instanceState']['name']
        logger.info('state: ' + str(state))
        instanceId = detail['responseElements']['instancesSet']['items'][0]['instanceId']
        logger.info('instanceId:' + str(instanceId))
        

        ec2 = boto3.resource('ec2')

        myitems = detail['responseElements']['instancesSet']['items']
        logger.info('myitems: ' + str(myitems))
        az = myitems[0]['placement']['availabilityZone']
        logger.info('az: ' + str(az))
        ip = myitems[0]['privateIpAddress']
        logger.info('ip: ' + str(ip))
        first,second,third,fourth = ip.split('.')
        logger.info('first: ' + str(first))
        logger.info('first: ' + str(second))
        logger.info('first: ' + str(third))
        logger.info('first: ' + str(fourth))
        json_items = json.dumps(myitems[0]['tagSet']['items'])
        json_obj = json.loads(json_items)
        logger.info(json_obj)
        
        for i in range(len(json_obj)):
            if json_obj[i]['key'] == 'type':
                typeof = json_obj[i]['value']
            if json_obj[i]['key'] == 'Customer':
                customer = json_obj[i]['value']
            if json_obj[i]['key'] == 'env':
                environment = json_obj[i]['value']
        
    
        logger.info('customer: ' + customer)
        logger.info('environment: ' + environment)
        logger.info('type: ' + typeof)
        
        for item in myitems:
            ids.append(item['instanceId'])
        
            logger.info(ids)
            logger.info('number of instances: ' + str(len(ids)))

            base = ec2.instances.filter(InstanceIds=ids)

        if ids:
            for resourceid in ids:
                print('Tagging resource ' + resourceid)
            ec2.create_tags(Resources=ids, Tags=[{'Key': 'Name', 'Value': typeof + fourth + "." + customer + "." + az + "." + environment + "." + "capriza.com"}])

        logger.info(' Remaining time (ms): ' + str(context.get_remaining_time_in_millis()) + '\n')
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False
