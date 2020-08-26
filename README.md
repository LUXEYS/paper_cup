Paper Cup
--------

Microservices communication using publish and subscribe.

Paper Cup Pypi
--------

#### dependencies
> pip3 install -r requirements.txt

#### test
> make test
> OR python3 -m unittest paper_cup.test
For unit test you must have moto running

#### PyPi package
- In your local dist directory remove any old version of the package.
- Create the new version of the package run: make build
- Upload to pypi run: make package_upload
- Install pip install paper-cup.
