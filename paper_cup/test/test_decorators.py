from unittest import TestCase
from paper_cup.decorators import retry


class RetryableError(Exception):
    pass


class UnexpectedError(Exception):
    pass


class TestDecorators(TestCase):
  """Taken from the blog https://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/

    Can be used as documentation on how we can use the decorator and case on the usage in the lib.

  """
  # reduce the delay otherwise unit test will take too much time
  FAST_RETRY = {'tries': 2, 'delay': 0.1, 'backoff': 1}
  FAST_MORE_RETRY = {'tries': 4, 'delay': 0.1, 'backoff': 1}

  def test_always_fail_case(self):
    """Try an "always fail" case"""
    @retry(Exception, **self.FAST_RETRY)
    def test_fail(text):
        raise Exception("Fail")

    with self.assertRaises(Exception):
      test_fail("it will fail!")

  def test_success_case(self):
    """Try a "success" case"""
    @retry(Exception, **self.FAST_RETRY)
    def test_success(text):
      return text

    success_text = "it works!"
    self.assertEqual(test_success(success_text), success_text)

  def test_random_fail_case(self):
    """Try a "random fail" case
      it will fail randomly but at the end it will return the expected result
    """
    import random
    # use FAST_MORE_RETRY as we can be really unlucky and get several time < 0.5

    @retry(Exception, **self.FAST_MORE_RETRY)
    def test_random(text):
        x = random.random()
        if x < 0.5:
            raise Exception("Fail")
        else:
            return text
    success_text = "it works!"
    self.assertEqual(test_random(success_text), success_text)

  def test_limit_is_reached(self):
    """Check that the number of retry is what we asked"""
    self.counter = 0

    @retry(RetryableError, **self.FAST_MORE_RETRY)
    def always_fails():
        self.counter += 1
        raise RetryableError('failed')

    with self.assertRaises(RetryableError):
        always_fails()

    self.assertEqual(self.counter, self.FAST_MORE_RETRY['tries'])

  def test_multiple_exception_types(self):
    """With multiple exception."""
    from botocore.exceptions import NoCredentialsError
    self.counter = 0

    @retry((Exception, NoCredentialsError), **self.FAST_MORE_RETRY)
    def raise_multiple_exceptions():
        self.counter += 1
        if self.counter == 1:
            raise Exception('a retryable error')
        elif self.counter == 2:
            raise NoCredentialsError()
        else:
            return 'success'

    self.assertEqual(raise_multiple_exceptions(), 'success')
    self.assertEqual(self.counter, 3)

  def test_unexpected_exception_does_not_retry(self):
    """"""
    @retry(UnexpectedError, **self.FAST_RETRY)
    def raise_unexpected_error():
        raise UnexpectedError('unexpected error')

    with self.assertRaises(UnexpectedError):
        raise_unexpected_error()

  def test_using_a_logger(self):
    """Copy this one even if we don't use logger yet. TODO update when we'll do:
      https://github.com/LUXEYS/paper_cup/issues/1
    """
    import logging

    self.counter = 0

    sh = logging.StreamHandler()
    logger = logging.getLogger(__name__)
    logger.addHandler(sh)

    @retry(RetryableError, logger=logger, **self.FAST_RETRY)
    def fails_once():
      self.counter += 1
      if self.counter < 2:
          raise RetryableError('failed')
      else:
          return 'success'

    fails_once()
