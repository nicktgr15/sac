clean:
	rm -rf dist sac.egg-info

register-upload-test: clean
	python setup.py register sdist upload -r pypitest

register-upload-live: clean
	python setup.py register sdist upload -r pypi
