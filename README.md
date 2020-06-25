Paper Cup
--------

Microservices communication using publish and subscribe.

Paper Cup Pypi
--------

Create test package in https://test.pypi.org:
- Login to your account to check the project.
- In your local dist directory remove any old version of the package.
- Create the new version of the package run: make build
- Upload to pypi test run: make package_upload_test
- Go: https://test.pypi.org/project/paper-cup/ and copy the install link for testing.

Publish package to https://pypi.org:
- Login to your account to check the project.
- In your local dist directory remove any old version of the package.
- Create the new version of the package run: make build
- Upload to pypi run: make package_upload
- Install pip install paper-cup.
