#!/usr/bin/python
# coding:utf-8

import boto3
from boto3.session import Session
import botocore

import sys
import time

class EMR_Helper:
    ################################################################################
    # 定数群
    ################################################################################


    # retry間隔
    INTERVAL = 1.0

    # コンストラクタ
    def __init__(self, credential):
        session = Session(aws_access_key_id     = credential['accessKey'],
                          aws_secret_access_key = credential['secretKey'],
                          region_name           = credential['region'])

        self.__client = session.client('emr')


    ################################################################################
    # Throttling対策関数群
    ################################################################################

    # list_clusters
    def __list_clusters_force_1st(self, cluster_states):
        try:
            clusters = self.__client.list_clusters(
                ClusterStates = cluster_states
            )
        except botocore.exceptions.ClientError:
            if not 'ThrottlingException' in sys.exc_info():
                raise
            time.sleep(EMR_Helper.INTERVAL)
            clusters = self.__list_clusters_force_1st(cluster_states)

        return clusters

    def __list_clusters_force(self, cluster_states, next_token):
        try:
            clusters = self.__client.list_clusters(
                ClusterStates = cluster_states,
                Marker        = next_token,
            )
        except botocore.exceptions.ClientError:
            if not 'ThrottlingException' in sys.exc_info():
                raise
            time.sleep(EMR_Helper.INTERVAL)
            clusters = self.__list_clusters_force(cluster_states, next_token)

        return clusters

    # describe_cluster
    def describe_cluster_force(self, cluster_id):
        try:
            cluster_info = self.__client.describe_cluster(
                ClusterId  = cluster_id,
            )
        except:
            if not 'ThrottlingException' in sys.exc_info():
                raise
            time.sleep(EMR_Helper.INTERVAL)
            cluster_info = self.describe_cluster_force(cluster_id)

        return cluster_info

    # list_steps
    def list_steps_force(self, cluster_id, states):
        try:
            steps = self.__client.list_steps(
                ClusterId  = cluster_id,
                StepStates = states
            )
        except botocore.exceptions.ClientError:
            if not 'ThrottlingException' in sys.exc_info():
                raise
            time.sleep(EMR_Helper.INTERVAL)
            steps = self.list_steps_force(cluster_id, states)

        return steps


    ################################################################################
    # ヘルパー関数群
    ################################################################################

    # 各リソースに特定の処理をする
    def exec_func_each_clusters(self, states_filter, func, **args):
        first_call = True
        result     = True
        while True:
            if first_call:
                resources = self.__list_clusters_force_1st(states_filter)
                first_call = False
            else:
                resources = self.__list_clusters_force(states_filter, next_token)

            for cluster in resources['Clusters']:
                ret = func(cluster, args)
                if not ret:
                    result = False

            # 次のページなし
            if not resources.has_key('Marker'):
                break
            # 次のページへのポインタを取得
            next_token = resources['Marker']

        return result
