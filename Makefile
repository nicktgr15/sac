.PHONY: clean test

clean:
	rm -rf dist sac.egg-info build

register-upload-test: clean
	python setup.py register sdist upload -r pypitest

register-upload-live: clean
	python setup.py register sdist upload -r pypi

venv:
	virtualenv venv

create_venv: venv
	. venv/bin/activate && pip install wheel
	. venv/bin/activate && pip install pip --upgrade
	. venv/bin/activate && pip install -r requirements.txt

test:
	-rm .coverage coverage.xml
	. venv/bin/activate; nosetests test/* -v --with-xcoverage --cover-package=sac --nocapture

install:
	python setup.py install
	rm -rf dist sac.egg-info build

build: test
	python setup.py sdist