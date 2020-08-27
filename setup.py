from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='paper_cup',
    version='20.8.27',
    license='MIT',
    homepage='https://github.com/LUXEYS/paper_cup',
    author='Luxeys',
    url='https://github.com/LUXEYS/paper_cup',
    author_email='bryan@luxeys.com',
    description='Micro-service communication system powered with paper cup engine!',
    packages=find_packages(),
    install_requires=[
        'boto3',
    ],
    long_description_content_type="text/markdown",
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],
    zip_safe=False,
)
