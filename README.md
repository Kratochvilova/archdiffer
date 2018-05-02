# Archdiffer

Archdiffer is a web service for generic archive comparison. The main purpose is to compare different versions of software packages in order to simplify version verification.

The web is written in Flask, the comparison tasks are managed using Celery. Archdiffer is extensible by plugins. So far, only plugin rpmdiff for comparing RPM packages is implemented.

## Getting Started

## Database schema

Schema for archdiffer:

# ![archdiffer schema](images/erd_archdiffer.png)

Schema for archdiffer + plugin rpmdiff:

# ![rpmdiff schema](images/erd_rpmdiff.png)

## How to add plugins

## Licence

MIT © Pavla Kratochvílová