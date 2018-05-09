# Archdiffer

Archdiffer is a web service for generic archive comparison. The main purpose is to compare different versions of software packages in order to simplify version verification.

The web is written in Flask, the comparison tasks are managed using Celery. Archdiffer is extensible by plugins. So far, only plugin rpmdiff for comparing RPM packages is implemented.

<img src="images/Screenshot-2018-5-9 Rpmdiff-comps.png" width="425"/> <img src="images/Screenshot-2018-5-9 Rpmdiff-diffs.png" width="425"/>

## Getting Started

If you only want to try out Archdiffer without installation, for example during development, see [Quict Start](#quick-start).

Otherwise, see [Deploying Archdiffer](#deploying-archdiffer).

## Quick Start

To quickly try out Archdiffer (one system, sqlite database, no installation or configuration), follow these steps:

1. Download the Archdiffer git repository:
```
$ git clone https://github.com/Kratochvilova/archdiffer.git
```
2. Go to the project directory:
```
$ cd archdiffer
```
3. Install dependencies:
```
$ sudo dnf install rabbitmq-server python3-sqlalchemy python3-flask python3-flask-restful python3-flask-openid python3-celery python3-dnf python3-rpm rpmlint
```
4. Start rabbitmq server:
```
$ sudo systemctl start rabbitmq-server
```
5. Initialize database:
```
$ ARCHDIFFER_CONFIG=debug.conf python3 init_db.py
$ ARCHDIFFER_CONFIG=debug.conf python3 init_db_rpmdiff.py
```
6. Start Archdiffer worker and flask-frontend (on background or in separate terminals):
```
$ ARCHDIFFER_CONFIG=debug.conf python3 -m archdiffer.backend worker
$ ARCHDIFFER_CONFIG=debug.conf python3 debug_flask.py
```

(If you don't wish to run Archdiffer in debug mode, set DEBUG = False in debug.conf)

## Deploying Archdiffer

Archdiffer consists of two parts, flask-frontend and backend, and can be therefore installed on two separate systems.

### Prerequisites

To run archdiffer, you need to set up:

* database that is [supported by SQLAlchemy](http://docs.sqlalchemy.org/en/latest/core/engines.html#supported-databases) (in some cases you will also need to install some additional dependencies, for example python3-psycopg2 for postgresql)

* message broker that is [supported by Celery](docs.celeryproject.org/en/latest/getting-started/brokers/index.html) (for example RabbitMQ)

* HTTP server - for example Apache (requires httpd and python3-mod_wsgi), archdiffer provides .wsgi file and .conf file for Apache

### Installing

Either install separately frontend and backend:

```
$ sudo dnf install archdiffer-flask-frontend
$ sudo dnf install archdiffer-backend
```

Or install both at once:

```
$ sudo dnf install archdiffer
```

Then install all desired plugins, for example plugin rpmdiff:

```
$ sudo dnf install archdiffer-plugin-rpmdiff
```

or

```
$ sudo dnf install archdiffer-plugin-rpmdiff-flask-frontend
$ sudo dnf install archdiffer-plugin-rpmdiff-backend
```

### Configuration

Change configuration file:

```
/etc/archdiffer.conf
```

Set values for [DATABASE_URL](http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls), [MESSAGE_BROKER](http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html), SECRET_KEY.

Configure archdiffer-worker to automatically start on boot:

```
$ sudo systemctl enable archdiffer-worker
```

If you are running Apache and have SELinux in enforcing mode, you need to allow Apache to connect over HTTP for OpenID authentication:

```
$ sudo setsebool -P httpd_can_network_connect=1
```

### Initialization:

Initialize database:

```
$ sudo /usr/libexec/archdiffer/init_db
```

Initialize database for all desired plugins, for example rpmdiff:

```
$ sudo /usr/libexec/archdiffer/init_db_rpmdiff
```

### Start

Start backend:

```
$ sudo systemctl start archdiffer-worker
```

Start your web server. For example for apache:

```
$ sudo systemctl start httpd
```

## Database schema

Schema for archdiffer:

![archdiffer schema](images/erd-archdiffer.png)

Schema for archdiffer + plugin rpmdiff:

![rpmdiff schema](images/erd-rpmdiff.png)

## How to Develop Plugins

An example of very basic plugin is the `example_plugin` in the plugins directory.

To add new plugin, simply add a module in the plugins directory with submodules named `flask_frontend` and `worker`.

### Flask-frontend

If there is a module named `flask_frontend` directly in `plugin.some_plugin`, it will be imported by flask-frontend. You can create blueprints and define views, and then register the blueprints to extend the flask application. Example:

```
from ...flask_frontend.flask_app import flask_app
blueprint = Blueprint('example_plugin', __name__, template_folder='templates')

@blueprint.route('/', methods=['GET'])
def index():
    return render_template('example_plugin_index.html')

flask_app.register_blueprint(blueprint, url_prefix='/example_plugin')
```

### Backend

If there is a module named `worker` directly in `plugin.some_plugin`, it will be imported by backend. In this module, you can define celery tasks. Example:

```
from ...backend.celery_app import celery_app
@celery_app.task(name='example_plugin.example_task')
def example_task():
    pass
```

The name for the task should be a unique string, so it is recommended to use the plugin name as prefix.

### Sending tasks

To send tasks, you will also need to define celery app in the frontend (importing the app from backend would also work, but in that case it wouldn't be possible to have backend and frontend on two different systems). Example:

```
from celery import Celery
celery_app = Celery(broker=config['common']['MESSAGE_BROKER'])
```

Sending tasks:

```
celery_app.send_task('example_plugin.example_task')
```

### Comparison Type

If the plugin implements some type of comparison, you can extend the database with necessary tables and add new comparison type to an existing table named `comparison_types`. The name of the type must be unique.

In order to show your comparison type on the Archdiffer's web site:

1. Register blueprint with url_prefix=<comparison_type_name>.
2. Register view named `index` in this blueprint.

## Licence

MIT © Pavla Kratochvílová