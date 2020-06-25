from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
      name='paper_cup',
      version='20.6.25',
      license='MIT',
      homepage='https://github.com/LUXEYS/paper_cup',
      author='Luxeys',
      author_email='bryan@luxeys.com',
      description='Micro-service communication system powered with paper cup engine!',
      packages=find_packages(),
      install_requires=[
          'boto3',
      ],
      long_description_content_type="text/markdown",
      long_description=long_description,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
      ],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
)
