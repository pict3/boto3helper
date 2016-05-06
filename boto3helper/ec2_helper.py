#!/usr/bin/python
# coding:utf-8

import boto3
from boto3.session import Session
import botocore

import sys
import time

class EC2_Helper:
    ################################################################################
    # 定数群
    ################################################################################

    # コア数定義
    TYPE_CORE_1 = {
        't2.nano', 't2.micro', 't2.small',
        'm3.medium'
    }
    TYPE_CORE_2 = {
        't2.medium', 't2.large',
        'm4.large',
        'm3.large',
        'c4.large',
        'c3.large',
        'r3.large',
    }
    TYPE_CORE_4 = {
        'm4.xlarge',
        'm3.xlarge',
        'c4.xlarge',
        'c3.xlarge',
        'r3.xlarge',
        'i2.xlarge',
        'd2.xlarge',
    }
    TYPE_CORE_8 = {
        'm4.2xlarge',
        'm3.2xlarge',
        'c4.2xlarge',
        'c3.2xlarge',
        'g2.2xlarge',
        'r3.2xlarge',
        'i2.2xlarge',
        'd2.2xlarge',
    }
    TYPE_CORE_16 = {
        'm4.4xlarge',
        'c4.4xlarge',
        'c3.4xlarge',
        'r3.4xlarge',
        'i2.4xlarge',
        'd2.4xlarge',
    }
    TYPE_CORE_32 = {
        'c3.8xlarge',
        'g2.8xlarge',
        'r3.8xlarge',
        'i2.8xlarge',
        'd2.8xlarge',
    }
    TYPE_CORE_36 = {
        'c4.8xlarge',
    }
    TYPE_CORE_40 = {
        'm4.10xlarge',
    }

    # retry間隔
    INTERVAL = 1.0

    # コンストラクタ
    def __init__(self, credential):
        session = Session(aws_access_key_id     = credential['accessKey'],
                          aws_secret_access_key = credential['secretKey'],
                          region_name           = credential['region'])

        self.__client = session.client('ec2')


    ################################################################################
    # Throttling対策関数群
    ################################################################################
    def __describe_instances_force_1st(self):
        try:
            response = self.__client.describe_instances()
        except botocore.exceptions.ClientError:
            if not 'ThrottlingException' in sys.exc_info():
                raise
            time.sleep(EC2_Helper.INTERVAL)
            response = self.__describe_instances_force_1st()

        return response

    def __describe_instances_force(self, next_token):
        try:
            response = self.__client.describe_instances(
                NextToken = next_token
            )
        except botocore.exceptions.ClientError:
            if not 'ThrottlingException' in sys.exc_info():
                raise
            time.sleep(EC2_Helper.INTERVAL)
            response = self.__describe_instances_force(next_token)

        return response


    ################################################################################
    # ヘルパー関数群
    ################################################################################

    # 各リソースに特定の処理をする
    def exec_func_each_instances(self, func, **args):
        first_call = True
        result     = True
        while True:
            if first_call:
                resources = self.__describe_instances_force_1st()
                first_call = False
            else:
                resources = self.__describe_instances_force(next_token)

            for reservation in resources['Reservations']:
                instances = reservation['Instances']
                for instance in instances:
                    ret = func(instance, args)
                    if not ret:
                        result = False

            # 次のページなし
            if not resources.has_key('NextToken'):
                break
            # 次のページへのポインタを取得
            next_token = resources['NextToken']

        return result


    # インスタンスタイプからコア数を判定
    @staticmethod
    def judge_core_count(instance_type):
        if   instance_type in EC2_Helper.TYPE_CORE_1:
            return 1
        elif instance_type in EC2_Helper.TYPE_CORE_2:
            return 2
        elif instance_type in EC2_Helper.TYPE_CORE_4:
            return 4
        elif instance_type in EC2_Helper.TYPE_CORE_8:
            return 8
        elif instance_type in EC2_Helper.TYPE_CORE_16:
            return 16
        elif instance_type in EC2_Helper.TYPE_CORE_32:
            return 32
        elif instance_type in EC2_Helper.TYPE_CORE_36:
            return 36
        elif instance_type in EC2_Helper.TYPE_CORE_40:
            return 40

        return 0
