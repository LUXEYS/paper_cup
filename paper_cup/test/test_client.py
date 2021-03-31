from unittest import TestCase

from paper_cup.client import SNSClient, SQSClient
from paper_cup import PaperCup


class TestSNSClient(TestCase):

  def setUp(self):
    """."""
    self.sns_client = SNSClient(PaperCup.PC_AWS_LOCAL_ENDPOINT)

  def test_instance(self):
    """Check that the instance initialize correctly."""
    # check that we correctly set an sns session
    self.assertTrue(self.sns_client._sns_client)

  def test_CruD(self):
    """Tests crud on topic, only Create and Delete part."""
    my_topic = self.sns_client.create_topic(PaperCup.PC_SNS_TOPIC)
    self.assertTrue(my_topic)
    # get the arn to delete it.
    deleted_response = self.sns_client.delete_topic(PaperCup.PC_SNS_TOPIC)
    # check the response and confirm that the topic is correctly deleted
    self.assertEqual(200, deleted_response['ResponseMetadata']['HTTPStatusCode'])

  def test_get_topic_arn(self):
    """Check that we can get the topic arn from it name."""
    # we don't have the topic so it will raise an exception
    with self.assertRaises(NotImplementedError):
      topic_arn = self.sns_client.get_topic_arn(PaperCup.PC_SNS_TOPIC)

    # create the topic
    self.sns_client.create_topic(PaperCup.PC_SNS_TOPIC)

    # now we can get the arn
    topic_arn = self.sns_client.get_topic_arn(PaperCup.PC_SNS_TOPIC)
    self.assertTrue(topic_arn)
    # the name of the topic is append at the end of the arn
    self.assertEqual(PaperCup.PC_SNS_TOPIC, topic_arn.split(':')[-1])

    # we are done so we cen delete the topic
    self.sns_client.delete_topic(PaperCup.PC_SNS_TOPIC)

  def test_get_topic_arn_with_token(self):
    """Test that the pagination work."""
    limit = 10
    # TODO

  def test_subscribe_error(self):
    """Check that it raise error if the topic or queue don't exist."""


  def test_subscribe_correct(self):
    """Check that the subscribtion work when linking a topic to a queue."""
    # create a topic
    self.sns_client.create_topic(PaperCup.PC_SNS_TOPIC)

    # create a queue
    sqs_client = SQSClient(PaperCup.PC_AWS_LOCAL_ENDPOINT)
    sqs_client.create_queue(PaperCup.PC_SQS_QUEUE)
    queue_arn = sqs_client.get_queue_arn(PaperCup.PC_SQS_QUEUE)

    # now we can subscribe the topic to the queue
    self.sns_client.subscribe_to_queue(PaperCup.PC_SNS_TOPIC, queue_arn)


class TestSQSClient(TestCase):

  def test_instance(self):
    """Check that the instance initialize correctly."""
    sqs_client = SQSClient(PaperCup.PC_AWS_LOCAL_ENDPOINT)
    # check that we correctly set an sqs session
    self.assertTrue(sqs_client._sqs_client)
    self.assertTrue(sqs_client._sqs_resource)
