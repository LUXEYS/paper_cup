build:
	python setup.py sdist
test:
	python -m unittest
test_3:
	python3 -m unittest
test_2:
	python2 -m unittest discover -p 'test_*.py'
package_upload_test:
	twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*
package_upload:
	twine upload --verbose --repository pypi dist/*
