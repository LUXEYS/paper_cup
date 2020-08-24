from unittest import TestCase

from paper_cup.client import SNSClient, SQSClient
from paper_cup.paper_cup import PaperCup


class TestSNSClient(TestCase):

  def test_instance(self):
    """Check that the instance initialize correctly."""
    sns_client = SNSClient()
    # check that we correctly set an sns session
    self.assertTrue(sns_client.sns)


class TestSQSClient(TestCase):

  def test_instance(self):
    """Check that the instance initialize correctly."""
    sqs_client = SQSClient()
    # check that we correctly set an sqs session
    self.assertTrue(sqs_client.sqs)
    self.assertTrue(sqs_client.sqs_obj)


class TestPaperCup(TestCase):

  def test_instance(self):
    """Check that the instance initialize correctly."""
    # We need to have a topic to connect to
    SNSClient(PaperCup.PC_AWS_LOCAL_ENDPOINT).create_topic(PaperCup.PC_TOPIC)
    paper_cup = PaperCup()

    # check that we correctly set sns and sqs sessions
    self.assertTrue(paper_cup.sns)
    self.assertTrue(paper_cup.topic_arn)
    self.assertTrue(paper_cup.sqs)