Name
====

boto3helper

## Overview

Boto3の使い勝手をよくする関数群。

## Description

スロットリング対応やページャーを考慮したイテレート処理などを実装。

## Requirement

boto3

## Usage

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

# EC2インスタンスごとに実行する関数
def show_ec2(instance, args):
    print(args['arg1']),
    print(instance[args['arg2']])

# EMRクラスタごとに実行する関数
def show_emr(cluster, args):
    print(args['arg1']),
    print(cluster[args['arg2']])

# CloudWatchLogsストリームごとに実行する関数
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

# ログイベントごとに実行する関数
def func_event(event, args):
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

    ret = o.describe_cluster_force('j-XXXXXXXXXXXXXXX')

    # CloudWatchLogs
    log_group   = '/aws/lambda/hoge'
    stream_name = '9999/12/31/[$LATEST]ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ'
    o = boto3helper.cloudwatchlogs_helper.CloudWatchLogs_Helper(credential)
    o.exec_func_each_streams(log_group,
                            func_stream,
                            arg1 = 'logStreamName: ',
                            arg2 = 'logStreamName',
                            arg3 = o,
                            arg4 = log_group
                            )
```

## Install

```
pip install boto3helper
```

## Licence

[MIT]

## Author

[Yutaka Hiroyama](https://github.com/Hiroyama-Yutaka)





インストール：
pip install

使用例：

