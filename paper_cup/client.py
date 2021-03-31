import boto3
from botocore.exceptions import NoCredentialsError
from paper_cup.decorators import retry


class SNSClient:
  """Common sns usages."""

  RETRY_TRIES = 3
  RETRY_DELAY = 0.1
  RETRY_BACKOFF = 2
  CUSTOM_RETRY_RULE = {'tries': RETRY_TRIES, 'delay': RETRY_DELAY, 'backoff': RETRY_BACKOFF}

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def __init__(self, endpoint_url, region='ap-northeast-1', aws_access_key_id=None, aws_secret_access_key=None):
    """Constructor with already set in options."""

    session = boto3.Session(region_name=region, aws_access_key_id=aws_secret_access_key, aws_secret_access_key=aws_secret_access_key)
    self._sns_client = session.client('sns', endpoint_url=endpoint_url)

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def get_topic_arn(self, topic_name, token=None):
    """Get sns topic by name and paginate until is found."""

    if token:
      list_topics = self._sns_client.list_topics(NextToken=token)
    else:
      list_topics = self._sns_client.list_topics()

    next_token = list_topics.get('NextToken')
    topic_list = list_topics['Topics']

    for topic in topic_list:
      if topic_name in topic['TopicArn'].split(':')[5]:
        return topic['TopicArn']
    else:
      if next_token:
        return self.get_topic_arn(topic_name=topic_name, token=next_token)
      else:
        raise NotImplementedError('SNS topic not found!')

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def publish(self, message, topic_name):
    """Send message to all subscriber of this topic."""
    return self._sns_client.publish(
        TopicArn=self.get_topic_arn(topic_name),
        Message=message,
    )

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def subscribe_to_queue(self, topic_name, queue_arn):
    """Topic subscribe to queue."""
    return self._sns_client.subscribe(
        Protocol='sqs',
        TopicArn=self.get_topic_arn(topic_name),
        Endpoint=queue_arn,
    )

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def create_topic(self, topic_name):
    """Create SNS topic by name."""
    return self._sns_client.create_topic(Name=topic_name)['TopicArn']

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def delete_topic(self, topic_name):
    """Delete a given SNS topic from it arn."""
    return self._sns_client.delete_topic(TopicArn=self.get_topic_arn(topic_name))


class SQSClient:
  """Common sqs usages."""

  RETRY_TRIES = 3
  RETRY_DELAY = 0.1
  RETRY_BACKOFF = 2
  CUSTOM_RETRY_RULE = {'tries': RETRY_TRIES, 'delay': RETRY_DELAY, 'backoff': RETRY_BACKOFF}

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def __init__(self, endpoint_url, region='ap-northeast-1', aws_access_key_id=None, aws_secret_access_key=None):
    """Constructor with already set in options."""
    session = boto3.Session(region_name=region, aws_access_key_id=aws_secret_access_key, aws_secret_access_key=aws_secret_access_key)
    self._sqs_client = session.client('sqs', endpoint_url=endpoint_url)
    self._sqs_resource = session.resource('sqs', endpoint_url=endpoint_url)

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def create_queue(self, queue_name):
    """Create SQS queue by name."""
    return self._sqs_client.create_queue(QueueName=queue_name)

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def delete_queue(self, queue_name):
    """Delete a given SQS queue from it url."""
    return self._sqs_client.delete_queue(QueueUrl=self.get_queue_url(queue_name))

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def get_queue_by_name(self, queue_name):
    """Get SQS queue object by name."""
    return self._sqs_resource.get_queue_by_name(QueueName=queue_name)

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def get_queue_url(self, queue_name):
    """Get SQS queue url by it name."""
    return self._sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']

  @retry(NoCredentialsError, **CUSTOM_RETRY_RULE)
  def get_queue_arn(self, queue_name):
    """Get SQS queue arn by it name."""
    sqs_queue_attrs = self._sqs_client.get_queue_attributes(QueueUrl=self.get_queue_url(queue_name), AttributeNames=['All'])['Attributes']
    return sqs_queue_attrs['QueueArn']
