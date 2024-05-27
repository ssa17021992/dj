# Django App Template

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```bash
$ sudo apt install python3-dev python3-venv linux-headers-$(uname -r) build-essential
$ python -m venv /path/to/venv
$ source /path/to/venv/bin/activate
```

### Installing

A step by step series of examples that tell you have to get a development env running

Say what the step will be

```bash
(venv)$ pip install -U pip wheel
(venv)$ pip install -r requirements/base.freeze.txt
```

### Applying database migrations

```bash
(venv)$ python manage.py migrate
```

### Creating super user

```bash
(venv)$ python manage.py createsuperuser
```

### Running django development server

```bash
(venv)$ python manage.py runserver
```

### Opening django admin

```
Go to http://localhost:8000/admin/ in your web browser
```

### Running celery worker and beat

```bash
(venv)$ celery --app=conf.celery worker -B -E -c1 -l INFO
```

End with an example of getting some data out of the system or using it for a little demo

## Running tests

Explain how to run the automated tests for this system

```bash
(venv)$ python manage.py test --settings tests.settings --keepdb -v2 tests
```

## Running coverage report

* [Coverage.py](https://coverage.readthedocs.io)

```bash
(venv)$ pip install -r requirements/cov.freeze.txt
(venv)$ coverage run ./manage.py test --settings tests.settings --keepdb -v2 tests
(venv)$ coverage report
(venv)$ coverage html
```

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

* [Black](https://black.readthedocs.io)
* [Isort](https://pycqa.github.io/isort/)
* [Flake8](https://flake8.pycqa.org)
* [Pre-Commit](https://pre-commit.com)

```bash
(venv)$ pip install -r requirements/style.freeze.txt
(venv)$ black .
(venv)$ isort .
(venv)$ flake8 .
(venv)$ pre-commit install
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Django](https://www.djangoproject.com)
* [DRF](http://www.django-rest-framework.org)
* [Graphene](https://graphene-python.org)
* [Channels](https://channels.readthedocs.io)
* [Celery](https://docs.celeryq.dev)

## Contributing

Please read CONTRIBUTING file for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

See the list of contributors who participated in this project.

## License

This project is licensed under the BSD 3-Clause License - see the LICENSE file for details.
