#!/usr/bin/env python3

import os
import datetime
import logging

import requests
from bs4 import BeautifulSoup
import boto3


URL = 'http://www.carmascafe.com/'
BUCKET_KEY = 'last_good_month_day'

LOGGER = logging.getLogger(__name__)


def mocha_chip_filter(tag):
    return tag.name == 'span' and \
        'mocha chip' in ' '.join(tag.text.strip().split())


def post_has_mocha_chip(post):
    return post.find(mocha_chip_filter) is not None


def month_day_today():
    return datetime.date.today().strftime('%B %-d')


def post_is_today(post):
    title = post.find('h3', class_='entry-title').text.strip()
    return month_day_today() in title


def has_mocha_chip_today():
    html = requests.get(URL).text
    soup = BeautifulSoup(html, 'html.parser')
    posts = soup.find_all('div', class_='post')
    return post_is_today(posts[0]) and post_has_mocha_chip(posts[0])


def read_last_good_month_day(client, bucket_name):
    try:
        response = client.get_object(Bucket=bucket_name, Key=BUCKET_KEY)
        return response['Body'].read().decode('utf-8')
    except client.exceptions.NoSuchKey as e:
        return None


def write_good_month_day(client, bucket_name, month_day):
    client.put_object(Bucket=bucket_name, Key=BUCKET_KEY,
                      Body=month_day.encode('utf-8'))


def notify_if_good_month_day(topic_arn, bucket_name, message='mocha chip! <3'):
    month_day = month_day_today()

    session = boto3.Session()
    s3 = session.client('s3')

    LOGGER.info('reading last good day from {}'.format(bucket_name))
    if read_last_good_month_day(s3, bucket_name) != month_day:
        if has_mocha_chip_today():
            LOGGER.info('today is a good day!')

            LOGGER.info('notifying {}'.format(topic_arn))
            sns = session.client('sns')
            sns.publish(TopicArn=topic_arn,
                        Message='{}: {}'.format(month_day, message))

            LOGGER.info('updating good day in {}'.format(bucket_name))
            write_good_month_day(s3, bucket_name, month_day)

            return True

        else:
            LOGGER.info('today is not a good day :\'(')
            return False

    else:
        LOGGER.info('today is a good day!  (already sent notifications)')
        return False


def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Read the latest post from the Carma\'s Cafe website, '
                    'check if mocha chip scones look like they\'re on the '
                    'menu, and send an AWS SNS message if they are (and if we '
                    'haven\'t already sent one today).',
    )
    parser.add_argument('topic_arn',
                        help='ARN of AWS SNS topic to publish message to')

    parser.add_argument('bucket_name',
                        help='Name of AWS S3 bucket to write state to')
    parser.add_argument('--message', default='mocha chip! <3',
                        help='Message to send if it looks like they have '
                             'mocha chip scones')
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)-15s %(levelname)-9s %(message)s',
                        level=logging.INFO)
    notify_if_good_month_day(
        topic_arn=args.topic_arn,
        bucket_name=args.bucket_name,
        message=args.message,
    )


if __name__ == '__main__':
    main()
