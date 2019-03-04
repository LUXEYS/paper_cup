from unittest import TestCase

from paper_cup.client import SNSClient


class TestSNSClient(TestCase):

    def test_istance(self):
        i = SNSClient
        self.assertEqual(i, SNSClient)
