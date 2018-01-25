.PHONY: clean test

clean:
	rm -rf dist sac.egg-info build

upload-live: clean test
	python setup.py sdist upload

venv:
	virtualenv venv

create_venv: venv
	. venv/bin/activate && pip install wheel
	. venv/bin/activate && pip install pip --upgrade
	. venv/bin/activate && pip install -r requirements.txt

test:
	-rm .coverage coverage.xml
	. venv/bin/activate; nosetests test/* -v --cover-inclusive --with-xcoverage --cover-package=sac --nocapture

install:
	python setup.py install
	rm -rf dist sac.egg-info build

build: clean test
	python setup.py sdist

build-install: clean test
	python setup.py sdist
	-pip uninstall sac -y
	pip install dist/sac*