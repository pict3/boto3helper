#!/usr/bin/python
# coding:utf-8

import boto3
from boto3.session import Session
import botocore

import sys
import time

class CloudWatchLogs_Helper:
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

        self.__client = session.client('logs')


    ################################################################################
    # Throttling対策関数群
    ################################################################################

    # describe_log_streams
    def __describe_log_streams_force_1st(self, group_name):
        try:
            streams = self.__client.describe_log_streams(
                logGroupName = group_name,
                descending   = True,
                orderBy      = 'LastEventTime',
            )
        except botocore.exceptions.ClientError:
            if not 'ThrottlingException' in sys.exc_info():
                raise
            time.sleep(CloudWatchLogs_Helper.INTERVAL)
            streams = self.__describe_log_streams_force(group_name)

        return streams

    def __describe_log_streams_force(self, group_name, next_token):
        try:
            streams = self.__client.describe_log_streams(
                logGroupName = group_name,
                descending   = True,
                orderBy      = 'LastEventTime',
                nextToken     = next_token,
            )
        except botocore.exceptions.ClientError:
            if not 'ThrottlingException' in sys.exc_info():
                raise
            time.sleep(CloudWatchLogs_Helper.INTERVAL)
            streams = self.__describe_log_streams_force(group_name, next_token)

        return streams

    # get_log_events
    def __get_log_events_force_1st(self, group_name, stream_name):
        try:
            log_events = self.__client.get_log_events(
                logGroupName  = group_name,
                logStreamName = stream_name,
                startFromHead = True
            )
        except botocore.exceptions.ClientError:
            if not 'ThrottlingException' in sys.exc_info():
                raise
            time.sleep(CloudWatchLogs_Helper.INTERVAL)
            log_events = self.__get_log_events_force_1st(group_name, stream_name)

        return log_events

    def __get_log_events_force(self, group_name, stream_name, next_token):
        try:
            log_events = self.__client.get_log_events(
                logGroupName  = group_name,
                logStreamName = stream_name,
                nextToken     = next_token,
                startFromHead = True
            )
        except botocore.exceptions.ClientError:
            if not 'ThrottlingException' in sys.exc_info():
                raise
            time.sleep(CloudWatchLogs_Helper.INTERVAL)
            log_events = self.__get_log_events_force(group_name, stream_name, next_token)

        return log_events


    ################################################################################
    # ヘルパー関数群
    ################################################################################

    # 各ストリームに特定の処理をする
    def exec_func_each_streams(self, group_name, func, **args):
        first_call = True
        while True:
            if first_call:
                streams = self.__describe_log_streams_force_1st(group_name)
                first_call = False
            else:
                streams = self.__describe_log_streams_force(group_name, next_token)

            for stream in streams['logStreams']:
                ret = func(stream, args)
                if not ret:
                    result = False

            # 次のページなし
            if not streams.has_key('nextToken'):
                break
            # 次のページへのポインタを取得
            next_token = streams['nextToken']

        return result

    # 各イベントに特定の処理をする
    def exec_func_each_events(self, group_name, stream_name, func, **args):
        first_call = True
        while True:
            if first_call:
                log_events = self.__get_log_events_force_1st(group_name, stream_name)
                first_call = False
            else:
                log_events = self.__get_log_events_force(group_name, stream_name, next_token)

            events = log_events['events']
            events_cnt = len(events)
            if events_cnt == 0:
                # CloudWatchLogsは取得イベント数がゼロの際にページャー末端となる
                break

            events.reverse()
            for event in events:
                time.sleep(0.0001)  # CPU張り付き対策

                ret = func(event, args)
                if not ret:
                    result = False

            # 次のページへのポインタを取得
            next_token = log_events['nextForwardToken']

        return result
