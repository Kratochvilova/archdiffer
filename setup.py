#!/usr/bin/env python

from distutils.core import setup

setup(
    name='archdiffer',
    version='1.1',
    description='Web service for generic archive comparison',
    author='Pavla Kratochvilova',
    author_email='pavla.kratochvilova@gmail.com',
    url='https://github.com/Kratochvilova/archdiffer',
    license='MIT',
    packages=[
        'archdiffer',
        'archdiffer.flask_frontend',
        'archdiffer.backend',
        'archdiffer.plugins.rpmdiff',
        'archdiffer.plugins.rpmdiff.flask_frontend',
        'archdiffer.plugins.rpmdiff.worker'
    ],
    package_data={
        'archdiffer.flask_frontend': [
            'templates/*.html', 'static/*', 'static/css/*'
        ],
        'archdiffer.plugins.rpmdiff.flask_frontend': [
            'templates/*.html'
        ],
    },
    data_files=[
        ('/etc', ['contrib/archdiffer.conf']),
        ('/etc/httpd/conf.d', ['contrib/apache/archdiffer.conf']),
        ('/lib/systemd/system', ['contrib/systemd/archdiffer-worker.service']),
        ('/usr/share/archdiffer', ['contrib/apache/archdiffer.wsgi']),
        ('/usr/libexec/archdiffer',
         ['contrib/scripts/init_db', 'contrib/scripts/init_db_rpmdiff']),
    ],
    install_requires=[
        'Flask',
        'Flask-RESTful',
        'Flask-OpenID',
        'celery',
        'SQLAlchemy',
        'rpmlint',
        'dnf',
        'rpm',
    ],
)
