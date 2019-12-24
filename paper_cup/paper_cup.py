import json

from .client import SNSClient, SQSClient


class PaperCup(object):
  """Publisher and subscribe settings."""
  PC_TOPIC = 'topic' # Publisher
  PC_QUEUE = 'my_queue' # Consumer
  PC_ENABLE = True
  PC_LISTEN = []
  PC_SENDER = 'this_app_name'

  # localhost
  PC_AWS_ACCESS_KEY_ID = 'id'
  PC_AWS_SECRET_ACCESS_KEY_ID = 'password'
  PC_AWS_LOCAL_ENDPOINT = 'http://localhost:1234'

  def __init__(self):
    sns = SNSClient(self.PC_AWS_LOCAL_ENDPOINT, aws_access_key_id=self.PC_AWS_ACCESS_KEY_ID, aws_secret_access_key=self.PC_AWS_SECRET_ACCESS_KEY_ID)
    self.sns = sns

    # option to disable the call to aws
    if self.PC_ENABLE:
      self.topic_arn = sns.get_topic_arn(self.PC_TOPIC)

    sqs = SQSClient(self.PC_AWS_LOCAL_ENDPOINT, aws_access_key_id=self.PC_AWS_ACCESS_KEY_ID, aws_secret_access_key=self.PC_AWS_SECRET_ACCESS_KEY_ID)
    self.sqs = sqs

  def publish(self, message, action):
    """Send message to sqs for user updates."""

    # option to disable the call to aws
    if not self.PC_ENABLE:
      return False

    message = self._add_more_data(message, action)
    message = json.dumps(message)
    self.sns.publish(message, self.topic_arn)

  def _add_more_data(self, message, action):
    """Add necessary data to detemine the consumer and action function."""
    # we expect the publish class name as PublishUser and it's cosumer will be ConsumeUser
    class_name = self.__class__.__name__
    message['consumer_action_class'] = class_name.replace('Publish', 'Consume')
    message['action'] = action
    message['sender'] = self.PC_SENDER
    return message

  def run(self):
    """Read the message in queue and use the class that will handle the action."""

    if not self.PC_ENABLE:
      return False

    queue = self.sqs.get_queue_by_name(self.PC_QUEUE)
    messages = queue.receive_messages(WaitTimeSeconds=20, MaxNumberOfMessages=10, VisibilityTimeout=30)
    # get all the cosumer classes that will handle actions
    action_classes = {cls.__name__: cls() for cls in self.__class__.__subclasses__() if 'Consume' in cls.__name__}

    for message in messages:
      body = json.loads(message.body)
      msg = json.loads(body['Message'])

      action = msg.get('action')
      sender = msg.get('sender')

      # check that the consumer listen from the sender and do the action
      if sender in self.PC_LISTEN:
        consumer_action_class = msg.get('consumer_action_class')
        action_class = action_classes.get(consumer_action_class)
        # only handle the action with consumers
        if action_class:
          action_class.do_action(msg, action)

      message.delete()

  def do_action(self, message, action):
    """Call the action of the consumer class."""
    method = getattr(self, action)
    method(message)
