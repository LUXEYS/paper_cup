# -*- coding:utf-8 -*-
from unittest import TestCase

from moto import mock_sqs, mock_sns

# need to have it here to have single mock instance (in tearDown it can find the queue create in setUp)
@mock_sns
@mock_sqs
class TestPaperCup(TestCase):

  def setUp(self):
    """"""
    from paper_cup.client import SNSClient, SQSClient
    from paper_cup.paper_cup import PaperCup, ConsumePC, PublishPC

    sqs = SQSClient(endpoint_url=None, region=PaperCup.PC_AWS_REGION)

    try:
      sqs.create_queue(PaperCup.PC_SQS_QUEUE)
    except Exception:
      pass # if it fail it's because the queue already exist

    sns = SNSClient(endpoint_url=None, region=PaperCup.PC_AWS_REGION)
    sns.create_topic(PaperCup.PC_SNS_TOPIC)

    # mock instance don't need these constants
    ConsumePC.PC_AWS_LOCAL_ENDPOINT = None
    ConsumePC.PC_AWS_ACCESS_KEY_ID = None
    ConsumePC.PC_AWS_SECRET_ACCESS_KEY_ID = None
    PublishPC.PC_AWS_LOCAL_ENDPOINT = None
    PublishPC.PC_AWS_ACCESS_KEY_ID = None
    PublishPC.PC_AWS_SECRET_ACCESS_KEY_ID = None

    self.consumer = ConsumePC()
    self.publisher = PublishPC()

    # Subscribe SQS queue to SNS
    self.publisher.sns_client.add_sqs_subscription(PaperCup.PC_SNS_TOPIC, self.consumer.sqs_client.get_queue_arn(PaperCup.PC_SQS_QUEUE))

  def test_consume_instance(self):
    """Check that the Consume instance initialize correctly."""
    # check that we correctly set sqs
    self.assertTrue(self.consumer.sqs_client)
    self.assertTrue(self.consumer.sqs_client.queue)

  def test_publish_instance(self):
    """Check that the Publish instance initialize correctly."""
    # check that we correctly set sns and sqs sessions
    self.assertTrue(self.publisher.sns_client)

  def test_bulk_publish(self):
    """Check that all the messages are sent."""
    import json
    # list of one message
    list_message = [DummyAppMessage()]
    list_action = ['index']

    self.publisher.bulk_publish(list_message, list_action)

    # Get the Message
    sqs_msgs = self.consumer.sqs_client.queue.receive_messages()
    sqs_msgs_dict = json.loads(sqs_msgs[0].body)

    msg = json.loads(sqs_msgs_dict['Message'])
    # check that Message content is a list of messages
    self.assertTrue(isinstance(msg, list))

  def test_bulk_consume(self):
    """"Check that we can read bulk data."""
    from paper_cup.paper_cup import ConsumePC, PublishPC

    class PublishDummyPC(PublishPC):
      """Dummy Publish class that will send message to make the Consume defined above consume the message."""

    class ConsumeDummyPC(ConsumePC):
      """Dummy class to Consume the upper publish class."""

      result = {} # to store the action done

      def index(self, message):
        """Dummy method to test the consume action, just store the action and the message."""
        self.result.update({'index': message})

      def delete(self, message):
        """Dummy method to test the consume action, just store the action and the message."""
        self.result.update({'delete': message})

    index_message = DummyAppMessage()
    delete_message = DummyAppMessage(qwe="qwe", abc="abc", number=1)

    list_message = [index_message, delete_message]
    list_action = ['index', 'delete']

    dummy_publisher = PublishDummyPC()
    dummy_publisher.bulk_publish(list_message, list_action)

    dummy_consumer = ConsumeDummyPC()

    # trigg the access to the queue and read the message
    ConsumePC().consume()

    # check that we have both action
    self.assertTrue(dummy_consumer.result['index'])
    self.assertTrue(dummy_consumer.result['delete'])
    # check that the message send for index is correctly handled by the index method
    self.assertEqual(dummy_consumer.result['index']['Band'], index_message['Band'])
    self.assertEqual(dummy_consumer.result['delete']['qwe'], delete_message['qwe'])

# ################ Dummy Data class


class DummyAppMessage(dict):
  """Build a dummy message as we expect to have it in the app.
    The message is a dict with any json valid data.
  """

  def __init__(self, *args, **kwargs):
    """Set dummy data by default."""
    if not kwargs:
      kwargs = {
          "Band": "Soilwork",
          "Album": "The living Infinity",
          "Tracklist": [
              {"track_num": 1, "title": "Spectrum of Eternity", "duration": "4:00", "active": "False"},
              {"track_num": 2, "title": "Memories Confined", "duration": "3:25", "active": "True"}
          ]
      }
    super(DummyAppMessage, self).__init__(*args, **kwargs)
    self.__dict__ = self


class DummyQueueMessage(dict):
  """Build a dummy message as it exist in the queue."""

  def __init__(self, *args, **kwargs):
    """Set dummy data by default."""
    if not kwargs:
      kwargs = {
          "action": "index",
          "consumer_action_class": "ConsumeDummyPC",
          "sender": "test-sevice",
          "my_data": {
              "name_kana": u"テスト太郎",
              "status": "ok",
              "updated_at": "2021-03-17 14:13:44",
              "is_active": True,
              "is_blocked": False,
              "work": None
          }
      }
    super(DummyQueueMessage, self).__init__(*args, **kwargs)
    self.__dict__ = self
