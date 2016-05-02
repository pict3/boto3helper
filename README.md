boto3helper



使用例：
```
#!/usr/bin/python
# coding:utf-8

import sys,os
import boto3helper

import getopt
from optparse import OptionParser

import pprint
pp = pprint.PrettyPrinter(indent=2)

import yaml


# yamlパーサー
def parse_yaml(file_name):
    file = open(file_name,'r')
    parse_data = yaml.load(file)
    file.close()

    return parse_data


def show_ec2(instance, args):
    print(args['arg1']),
    print(instance[args['arg2']])

def show_emr(cluster, args):
#    pp.pprint(cluster)
    print(args['arg1']),
    print(cluster[args['arg2']])

def func_stream(stream, args):
    print(args['arg1']),
    print(stream[args['arg2']])

    args['arg3'].exec_func_each_events(
                            args['arg4'],
                            stream[args['arg2']],
                            func_event,
                            arg1 = 'message: ',
                            arg2 = 'message'
                            )


def func_event(event, args):
#    pp.pprint(event)
    print(args['arg1']),
    print(event[args['arg2']]),



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f",)

    (options, args) = parser.parse_args(sys.argv)

    credential       = parse_yaml(options.f)

    # EC2
    ret = boto3helper.ec2_helper.EC2_Helper.judge_core_count('m3.large')
    print ret

    o = boto3helper.ec2_helper.EC2_Helper(credential)
    o.exec_func_each_instances(show_ec2,
                               arg1 = 'InstanceId: ',
                               arg2 = 'InstanceId')

    # EMR
    o = boto3helper.emr_helper.EMR_Helper(credential)
    o.exec_func_each_clusters(
                               ['TERMINATED'],
                               show_emr,
                               arg1 = 'Cluster ID: ',
                               arg2 = 'Id')

    ret = o.describe_cluster_force('j-2ECY3WKB45H3Z')
#    pp.pprint(ret)

    # CloudWatchLogs
    log_group   = '/aws/lambda/ami-backup-other-account'
    stream_name = '2015/12/07/[$LATEST]66db92f92710404ba8a063cd7763257a'
    o = boto3helper.cloudwatchlogs_helper.CloudWatchLogs_Helper(credential)
#    ret = o.describe_log_streams_force('/aws/lambda/ami-backup-other-account')
    o.exec_func_each_streams(log_group,
                            func_stream,
                            arg1 = 'logStreamName: ',
                            arg2 = 'logStreamName',
                            arg3 = o,
                            arg4 = log_group
                            )
```
