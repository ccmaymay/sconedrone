from sconedrone import notify_if_good_month_day
import os
import logging


def lambda_handler(event, context):
    logging.getLogger().setLevel(logging.INFO)
    notify_if_good_month_day(
        topic_arn=os.environ['SCONEDRONE_TOPIC_ARN'],
        bucket_name=os.environ['SCONEDRONE_BUCKET_NAME'])
