build:
	python setup.py sdist
test:
	python3 -m unittest
package_upload_test:
	twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*
package_upload:
	twine upload --verbose --repository pypi dist/*
