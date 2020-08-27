import json

from .client import SNSClient, SQSClient


class PaperCup(object):
  """Publisher and subscribe settings."""
  PC_ENABLE = True
  PC_TOPIC = 'topic' # Publisher (SNS)
  PC_QUEUE = 'queue' # Consumer (SQS)
  PC_LISTEN = ['service'] # list of service name for message to process ex: cas listen only 'booking' so for cas PC_LISTEN = ['booking']
  PC_SENDER = 'service' # name of the app that send the message ex: 'booking'

  # default values set for test
  PC_AWS_ACCESS_KEY_ID = 'test'
  PC_AWS_SECRET_ACCESS_KEY_ID = 'test'
  PC_AWS_LOCAL_ENDPOINT = 'http://192.168.56.1:9010' # we use moto

  # set default attribut values
  sns = False
  sqs = False

  def __init__(self):
    """Deprecated As we never need Publish and Consume in same time."""
    if self.PC_ENABLE:
      self.sns = SNSClient(self.PC_AWS_LOCAL_ENDPOINT, aws_access_key_id=self.PC_AWS_ACCESS_KEY_ID, aws_secret_access_key=self.PC_AWS_SECRET_ACCESS_KEY_ID)
      self.topic_arn = self.sns.get_topic_arn(self.PC_TOPIC)

      self.sqs = SQSClient(self.PC_AWS_LOCAL_ENDPOINT, aws_access_key_id=self.PC_AWS_ACCESS_KEY_ID, aws_secret_access_key=self.PC_AWS_SECRET_ACCESS_KEY_ID)

  def publish(self, message, action):
    """Send message to sns."""
    if self.sns:
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

  def bulk_publish(self, list_message, list_action):
    """Send message by bulk to sns.
      Please limit the list to 50 messages (Need to be done in the call as it depends on the message).
    """
    message = ''
    msg_list = []
    if self.sns:
      for i, one_message in enumerate(list_message):
        full_message = self._add_more_data(one_message, list_action[i])
        temp_message = json.dumps(full_message)
        # check max size of the message to publish under the limit
        if (len(message) + len(temp_message)) > 256000:
          self.sns.publish(message, self.topic_arn)
          msg_list = [full_message]
        else:
          msg_list.append(one_message)
        message = json.dumps(msg_list)

      if message:
        self.sns.publish(message, self.topic_arn)

  def run(self):
    """Deprecated as bad naming.
      Read the message in queue and use the class that will handle the action. (Consume the message)
    """
    if self.sqs:
      queue = self.sqs.get_queue_by_name(self.PC_QUEUE)
      # get all the consumer classes that will handle actions
      action_classes = {cls.__name__: cls() for cls in self.__class__.__subclasses__() if 'Consume' in cls.__name__}
      messages = queue.receive_messages(WaitTimeSeconds=20, MaxNumberOfMessages=10, VisibilityTimeout=30)
      while messages:
        for message in messages:
          body = json.loads(message.body)
          msg = json.loads(body['Message'])

          if isinstance(msg, list):
            for one_msg in msg:
              self._consume_msg(one_msg, action_classes)
          else:
            self._consume_msg(msg, action_classes)

          message.delete()

        messages = queue.receive_messages(MaxNumberOfMessages=10, VisibilityTimeout=30)

  def _consume_msg(self, msg, action_classes):
    """Common call to consume a message."""
    action = msg.get('action')
    sender = msg.get('sender')

    # check that the consumer listen from the sender and do the action
    if sender in self.PC_LISTEN:
      consumer_action_class = msg.get('consumer_action_class')
      action_class = action_classes.get(consumer_action_class)
      # only handle the action with consumers
      if action_class:
        action_class._do_action(msg, action)

  def _do_action(self, message, action):
    """Call the action of the consumer class."""
    method = getattr(self, action)
    method(message)


class PublishPC(PaperCup):
  """Public class for Publisher."""

  def __init__(self, *args, **kwargs):
    """"""
    if self.PC_ENABLE:
      self.sns = SNSClient(self.PC_AWS_LOCAL_ENDPOINT, aws_access_key_id=self.PC_AWS_ACCESS_KEY_ID, aws_secret_access_key=self.PC_AWS_SECRET_ACCESS_KEY_ID)
      self.topic_arn = self.sns.get_topic_arn(self.PC_TOPIC)


class ConsumePC(PaperCup):
  """Public class for Consume ."""

  def __init__(self, *args, **kwargs):
    """"""
    if self.PC_ENABLE:
      self.sqs = SQSClient(self.PC_AWS_LOCAL_ENDPOINT, aws_access_key_id=self.PC_AWS_ACCESS_KEY_ID, aws_secret_access_key=self.PC_AWS_SECRET_ACCESS_KEY_ID)
      self.sqs_queue = self.sqs.get_queue_by_name(self.PC_QUEUE)

  def consume(self):
    """Read the message in queue and use the class that will handle the action. (Consume the message)"""
    if self.sqs_queue:
      # get all the consumer classes that will handle actions
      action_classes = {cls.__name__: cls() for cls in self.__class__.__subclasses__() if 'Consume' in cls.__name__}
      messages = self.sqs_queue.receive_messages(WaitTimeSeconds=20, MaxNumberOfMessages=10, VisibilityTimeout=30)

      while messages:
        for message in messages:
          body = json.loads(message.body)
          msg = json.loads(body['Message'])

          if isinstance(msg, list):
            for one_msg in msg:
              self._consume_msg(one_msg, action_classes)
          else:
            self._consume_msg(msg, action_classes)

          message.delete()

        messages = self.sqs_queue.receive_messages(MaxNumberOfMessages=10, VisibilityTimeout=30)
