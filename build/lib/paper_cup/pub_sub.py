import abc
import json

from .client import SNSClient, SQSClient

# abc that work for python 2 and 3
# https://gist.github.com/alanjcastonguay/25e4db0edd3534ab732d6ff615ca9fc1
ABC = abc.ABCMeta('ABC', (object,), {})


class SNSPublisher():
  """SNS message publisher common usages."""

  # settings
  TOPIC = 'topic'
  AWS_ACCESS_KEY_ID = 'id'
  AWS_SECRET_ACCESS_KEY_ID = 'password'
  AWS_LOCAL_ENDPOINT = 'http://localhost:1234'
  SNS_PUBLISHER_ENABLE = True
  CONSUMER_ACTION_CLASS = 'MyCosumerActionClass' # name of class that will handle this message actions

  def __init__(self, sns=None):
    """
    :param obj sns: SNS client in main module
    """

    if not sns:
      sns = SNSClient(self.AWS_LOCAL_ENDPOINT, aws_access_key_id=self.AWS_ACCESS_KEY_ID, aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY_ID)

    self.sns = sns

    # option to disable the call to aws
    if self.SNS_PUBLISHER_ENABLE:
      self.topic_arn = sns.get_topic_arn(self.TOPIC)

  def publish(self, message, action):
    """Send message to sqs for user updates."""

    # option to disable the call to aws
    if not self.SNS_PUBLISHER_ENABLE:
      return False

    message = self._add_more_data(message, action)
    message = json.dumps(message)
    self.sns.publish(message, self.topic_arn)

  def _add_more_data(self, message, action):
    message['consumer_action_class'] = self.CONSUMER_ACTION_CLASS
    message['action'] = action
    return message


class SQSConsumer(object):
  """Read from sqs and assign the class that will handle the action."""

  # settings
  TOPIC = 'topic'
  AWS_ACCESS_KEY_ID = 'id'
  AWS_SECRET_ACCESS_KEY_ID = 'password'
  AWS_LOCAL_ENDPOINT = 'http://localhost:1234'
  QUEUE = 'my_queue'

  def __init__(self, sqs=None):
    """
    :param obj sns: SNS client in main module
    """
    self.action_classes = {cls.__name__: cls() for cls in BaseCosumerAction.__subclasses__()}

    if not sqs:
      sqs = SQSClient(self.AWS_LOCAL_ENDPOINT, aws_access_key_id=self.AWS_ACCESS_KEY_ID, aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY_ID)

    self.sqs = sqs

  def run(self):
    queue = self.sqs.get_queue_by_name(self.QUEUE)
    messages = queue.receive_messages(WaitTimeSeconds=20, MaxNumberOfMessages=10, VisibilityTimeout=30)

    for message in messages:
      body = json.loads(message.body)
      msg = json.loads(body['Message'])
      action = msg.get('action')

      consumer_action_class = msg.get('consumer_action_class')
      action_class = self.action_classes.get(consumer_action_class)
      action_class.do_action(action, msg)

      message.delete()


class BaseCosumerAction(ABC):
  """Base class to enforce the cosumer action method."""
  ACTIONS = ('my_action',)

  @abc.abstractmethod
  def do_action(self):
    pass
