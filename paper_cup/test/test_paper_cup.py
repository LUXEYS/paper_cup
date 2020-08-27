from unittest import TestCase
import warnings

from paper_cup.client import SNSClient, SQSClient
from paper_cup.paper_cup import PaperCup


class TestPaperCup(TestCase):

  def setUp(self):
    """Silent the warnings as explained here:
        https://github.com/boto/boto3/issues/454
      with solution from here:
        https://stackoverflow.com/questions/26563711/disabling-python-3-2-resourcewarning
    """
    warnings.simplefilter("ignore", ResourceWarning)

  def tearDown(self):
    """Put back the warnings."""
    warnings.simplefilter("default", ResourceWarning)

  def test_instance(self):
    """Check that the instance initialize correctly."""
    # We need to have a topic to connect to
    SNSClient(PaperCup.PC_AWS_LOCAL_ENDPOINT).create_topic(PaperCup.PC_TOPIC)
    paper_cup = PaperCup()

    # check that we correctly set sns and sqs sessions
    self.assertTrue(paper_cup.sns)
    self.assertTrue(paper_cup.topic_arn)
    self.assertTrue(paper_cup.sqs)

  def test_bulk_publish(self):
    """Check that it all the messages are sent."""
    import json
    # list of one message
    list_message = [DummyMessage()]
    list_action = ['index']
    paper_cup = pc_instance()
    paper_cup.bulk_publish(list_message, list_action)

    # FIXME remove this after refactor the constructors
    paper_cup.sqs_queue = paper_cup.sqs.get_queue_by_name(paper_cup.PC_QUEUE)

    # Get the Message
    sqs_msgs = paper_cup.sqs_queue.receive_messages()
    sqs_msgs_dict = json.loads(sqs_msgs[0].body)

    msg = json.loads(sqs_msgs_dict['Message'])
    # check that Message content is a list of messages
    self.assertTrue(isinstance(msg, list))

    # clean the queue and topic
    clean_after(paper_cup)

  def test_bulk_consume(self):
    """"Check that we can read bulk data."""

    list_message = [DummyMessage(), DummyMessage(qwe="qwe", abc="abc", number=1)]
    list_action = ['index', 'delete']
    paper_cup = pc_instance()
    paper_cup.bulk_publish(list_message, list_action)

    list_result = []

    class ConsumePaperCup(PaperCup):
      """Dummy class to have consume in the name"""

      def index(self, message):
        """Dummy method to test the consume action."""
        list_result.append(message)

      def delete(self, message):
        """Dummy method to test the consume action."""
        list_result.append(message)

    PaperCup().run()
    # check that we have the 2 messages in the list i.e that we consume correclty the two actions
    self.assertEqual(len(list_result), 2)


# ################ Other utils for test maybe better to move to their own file


def pc_instance():
  """Build and return a ready to use paper cup instance."""
  SNSClient(PaperCup.PC_AWS_LOCAL_ENDPOINT).create_topic(PaperCup.PC_TOPIC)

  class PublishPaperCup(PaperCup):
    """Dummy class to have Publish key in the name."""

  pc_instance = PublishPaperCup()

  # delete the queue if the unit test fail the queue may be here
  try:
    pc_instance.sqs.delete_queue(PaperCup.PC_QUEUE)
  except Exception:
    # if the queue don't exist it will raise but we don't care
    pass

  SQSClient(PaperCup.PC_AWS_LOCAL_ENDPOINT).create_queue(PaperCup.PC_QUEUE)

  pc_instance.topic_arn = pc_instance.sns.get_topic_arn(PaperCup.PC_TOPIC)
  pc_instance.queue_url = pc_instance.sqs.get_queue_url(PaperCup.PC_QUEUE)
  pc_instance.queue_arn = pc_instance.sqs.get_queue_arn(pc_instance.queue_url)

  # attach the topic to the queue so when we publish the message will go this queue
  pc_instance.sns.subscribe(pc_instance.topic_arn, pc_instance.queue_arn)

  return pc_instance


def clean_after(pc_instance):
  """Delete after usage."""
  pc_instance.sqs.delete_queue(pc_instance.queue_url)
  pc_instance.sns.delete_topic(pc_instance.topic_arn)


class DummyMessage(dict):
  """Build a dummy dict with data inside as the message can be any json valid data."""

  def __init__(self, *args, **kwargs):
    """Set dummy data by default."""
    if not kwargs:
      kwargs = {
          "Band": "Soilwork",
          "Album": "The living Infinity",
          "Tracklist": [
              {"track_num": 1, "title": "Spectrum of Eternity", "duration": "4:00"},
              {"track_num": 2, "title": "Memories Confined", "duration": "3:25"}
          ]
      }
    super().__init__(*args, **kwargs)
    self.__dict__ = self
