[![Build Status](https://travis-ci.com/LUXEYS/paper_cup.svg?branch=master)](https://travis-ci.com/github/LUXEYS/paper_cup)


Paper Cup
--------

Microservices communication using publish and subscribe.

Paper Cup Pypi
--------

#### dependencies
> pip3 install -r requirements/dev.txt

#### test
> make test

For unit test you must have moto running

#### PyPi package
- In your local dist directory remove any old version of the package.
- Create the new version of the package: `make build`
- Upload to pypi: `make package_upload`
- Install: `pip install paper-cup`
