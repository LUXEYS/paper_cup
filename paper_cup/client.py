import boto3


class SNSClient:
  """Common sns usages."""

  def __init__(self, endpoint_url=None, region='ap-northeast-1', aws_access_key_id=None, aws_secret_access_key=None):
      session = boto3.Session(region_name=region, aws_access_key_id=aws_secret_access_key, aws_secret_access_key=aws_secret_access_key)
      self.sns = session.client('sns', endpoint_url=endpoint_url)

  def get_topic_arn(self, topic_name, token=None):
    """Get sns topic by name and paginate until is found."""
    sns = self.sns

    if token:
      list_topics = sns.list_topics(NextToken=token)
    else:
      list_topics = sns.list_topics()

    next_token = list_topics.get('NextToken')
    topic_list = list_topics['Topics']

    for topic in topic_list:
      if topic_name in topic['TopicArn'].split(':')[5]:
        return topic['TopicArn']
    else:
      if next_token:
        self.get_topic(token=next_token)
      else:
        raise NotImplementedError('SNS topic not found!')

  def publish(self, message, topic_arn):
    """Send message to all subscriber of this topic."""
    return self.sns.publish(
      TopicArn=topic_arn,
      Message=message,
    )

  def subscribe(self, topic_arn, queue_arn):
    """Subscribe to topic."""
    return self.sns.subscribe(
      TopicArn=topic_arn,
      Protocol='sqs',
      Endpoint=queue_arn,
    )

  def create_topic(self, topic_name):
    return self.sns.create_topic(Name=topic_name)['TopicArn']

  def delete_topic(self, topic_arn):
    return self.sns.delete_topic(TopicArn=topic_arn)


class SQSClient:
  """Common sqs usages."""

  def __init__(self, endpoint_url=None, region='ap-northeast-1', aws_access_key_id=None, aws_secret_access_key=None):
      session = boto3.Session(region_name=region, aws_access_key_id=aws_secret_access_key, aws_secret_access_key=aws_secret_access_key)
      self.sqs = session.client('sqs', endpoint_url=endpoint_url)
      self.sqs_obj = session.resource('sqs', endpoint_url=endpoint_url)

  def create_queue(self, queue_name):
    return self.sqs.create_queue(QueueName=queue_name)

  def delete_queue(self, queue_url):
    return self.sqs.delete_queue(QueueUrl=queue_url)

  def get_queue_by_name(self, queue_name):
    return self.sqs_obj.get_queue_by_name(QueueName=queue_name)

  def get_queue_url(self, queue_name):
    return self.sqs.get_queue_url(QueueName=queue_name)['QueueUrl']

  def get_queue_arn(self, queue_url):
    sqs_queue_attrs = self.sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])['Attributes']
    get_queue_arn = sqs_queue_attrs['QueueArn']
    return get_queue_arn
