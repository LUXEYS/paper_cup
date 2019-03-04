from setuptools import setup


def readme():
      with open('README.rst') as f:
            return f.read()

setup(name='paper_cup',
      version='19.3.1',
      url='labola.jp',
      license='MIT',
      author='Luxeys',
      author_email='bryan@luxeys.com',
      description='Common sns and sqs class for publisher and consumer action.',
      packages=['paper_cup'],
      install_requires=[
          'boto3',
      ],
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
      ],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],)
