import json
from .client import SNSClient, SQSClient


class PaperCup(object):
  """Publisher and subscribe settings."""
  PC_ENABLE = True
  PC_SERVICE_LISTEN = ['service'] # list of service name for message to process ex: ['my_other_app']
  PC_SERVICE_SENDER = 'service' # name of the app that send the message ex: 'my_app'

  PC_DEFAULT_CONSUME_CLIENT = 'SQS'
  PC_DEFAULT_PUBLISH_CLIENT = 'SNS'

  PC_SUPPORTED_PUBLISH_CLIENT = ['SNS', 'SQS']
  PC_SUPPORTED_CONSUME_CLIENT = ['SQS']

  PC_SNS_TOPIC = 'topic'
  PC_SQS_QUEUE = 'queue'

  # default values set for test
  PC_AWS_ACCESS_KEY_ID = 'test'
  PC_AWS_SECRET_ACCESS_KEY_ID = 'test'
  PC_AWS_LOCAL_ENDPOINT = 'http://192.168.56.1:9010' # we use moto

  PC_AWS_REGION = 'ap-northeast-1'

  # set default attribut values
  sns_client = False
  sqs_client = False


class PublishPC(PaperCup):
  """Public class for Publisher."""

  def __init__(self, *args, **kwargs):
    """"""
    if self.PC_ENABLE:
      client = kwargs.get('client', PaperCup.PC_DEFAULT_PUBLISH_CLIENT)
      assert(client in PaperCup.PC_SUPPORTED_PUBLISH_CLIENT)

      if client == 'SNS':
        self.sns_client = SNSClient(self.PC_AWS_LOCAL_ENDPOINT, region=self.PC_AWS_REGION, aws_access_key_id=self.PC_AWS_ACCESS_KEY_ID, aws_secret_access_key=self.PC_AWS_SECRET_ACCESS_KEY_ID)
      elif client == 'SQS':
        self.sqs_client = SQSClient(self.PC_AWS_LOCAL_ENDPOINT, region=self.PC_AWS_REGION, aws_access_key_id=self.PC_AWS_ACCESS_KEY_ID, aws_secret_access_key=self.PC_AWS_SECRET_ACCESS_KEY_ID)
        self.sqs_client.queue = self.sqs_client.get_queue_by_name(self.PC_SQS_QUEUE)

  def publish(self, message, action):
    """Send message to sns."""
    if self.sns_client:
      message = self._add_more_data(message, action)
      message = json.dumps(message)
      self.sns_client.sns.publish(message, self.PC_SNS_TOPIC)

  def _add_more_data(self, message, action):
    """Add necessary data to detemine the consumer and action function."""
    # we expect the publish class name as PublishUser and it's cosumer will be ConsumeUser
    class_name = self.__class__.__name__
    message['consumer_action_class'] = class_name.replace('Publish', 'Consume')
    message['action'] = action
    message['sender'] = self.PC_SERVICE_SENDER
    return message

  def bulk_publish(self, list_message, list_action):
    """Send message by bulk to sns.
      Please limit the list to 50 messages (Need to be done in the call as it depends on the message).
    """
    message = ''
    msg_list = []
    if self.sns_client:
      for i, one_message in enumerate(list_message):
        full_message = self._add_more_data(one_message, list_action[i])
        temp_message = json.dumps(full_message)
        # check max size of the message to publish under the limit
        if (len(message) + len(temp_message)) > 256000:
          self.sns_client.publish(message, self.PC_SNS_TOPIC)
          msg_list = [full_message]
        else:
          msg_list.append(one_message)
        message = json.dumps(msg_list)

      if message:
        self.sns_client.publish(message, self.PC_SNS_TOPIC)


class ConsumePC(PaperCup):
  """Public class for Consume."""

  def __init__(self, *args, **kwargs):
    """"""
    if self.PC_ENABLE:
      client = kwargs.get('client', PaperCup.PC_DEFAULT_CONSUME_CLIENT)
      assert(client in PaperCup.PC_SUPPORTED_CONSUME_CLIENT)

      if client == 'SQS':
        self.sqs_client = SQSClient(self.PC_AWS_LOCAL_ENDPOINT, region=self.PC_AWS_REGION, aws_access_key_id=self.PC_AWS_ACCESS_KEY_ID, aws_secret_access_key=self.PC_AWS_SECRET_ACCESS_KEY_ID)
        self.sqs_client.queue = self.sqs_client.get_queue_by_name(self.PC_SQS_QUEUE)

  def consume(self):
    """Read the message in queue and use the class that will handle the action."""
    if self.sqs_client.queue:
      # get all the consumer classes that will handle actions
      action_classes = {cls.__name__: cls() for cls in self.__class__.__subclasses__() if 'Consume' in cls.__name__}
      messages = self.sqs_client.queue.receive_messages(WaitTimeSeconds=20, MaxNumberOfMessages=10, VisibilityTimeout=30)

      while messages:
        for message in messages:
          body = json.loads(message.body)
          msg = json.loads(body['Message'])

          # remove the message before consuming to prevent queue stuck if consume loop take time
          message.delete()
          
          if isinstance(msg, list):
            raised_exception = []
            for one_msg in msg:
              try:
                self._consume_msg(one_msg, action_classes)
              except Exception as e:
                raised_exception.append(e)
            if raised_exception:
              # raise the first one
              raise raised_exception[0]
          else:
            self._consume_msg(msg, action_classes)

        messages = self.sqs_client.queue.receive_messages(MaxNumberOfMessages=10, VisibilityTimeout=30)

  def _consume_msg(self, msg, action_classes):
    """Common call to consume the queue."""
    action = msg.get('action')
    sender = msg.get('sender')

    # check that the consumer listen from the sender and do the action
    if sender in self.PC_SERVICE_LISTEN:
      consumer_action_class = msg.get('consumer_action_class')
      action_class = action_classes.get(consumer_action_class)
      # only handle the action with consumers
      if action_class:
        action_class._do_action(msg, action)

  def _do_action(self, message, action):
    """Call the action of the consumer class."""
    method = getattr(self, action)
    method(message)
