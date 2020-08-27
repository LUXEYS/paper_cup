from unittest import TestCase

from paper_cup.client import SNSClient, SQSClient
from paper_cup import PaperCup


class TestSNSClient(TestCase):

  def test_instance(self):
    """Check that the instance initialize correctly."""
    sns_client = SNSClient(PaperCup.PC_AWS_LOCAL_ENDPOINT)
    # check that we correctly set an sns session
    self.assertTrue(sns_client.sns)


class TestSQSClient(TestCase):

  def test_instance(self):
    """Check that the instance initialize correctly."""
    sqs_client = SQSClient(PaperCup.PC_AWS_LOCAL_ENDPOINT)
    # check that we correctly set an sqs session
    self.assertTrue(sqs_client.sqs)
    self.assertTrue(sqs_client.sqs_obj)
