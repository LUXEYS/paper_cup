from setuptools import setup


def readme():
      with open('README.rst') as f:
            return f.read()

setup(name='paper_cup',
      version='19.3.5',
      license='MIT',
      author='Luxeys',
      author_email='bryan@luxeys.com',
      description='Micro-service communication system powered with paper cup engine!',
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
