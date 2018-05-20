.. _rpm_packages:

RPM Packages
============

RPM Packages resource represents RPM packages.

.. _rpm_packages_properties:

Properties of RPM Packages
--------------------------

======================  ====================== ======================
Attribute               Type                   Description
======================  ====================== ======================
id                      int                    Unique identifier of the RPM Package.
name                    string                 Name of the RPM Package.
arch                    string                 Architecture of the RPM Package.
epoch                   string                 Epoch of the RPM Package.
version                 string                 Version of the RPM Package.
release                 string                 Release of the RPM Package.
filename                string                 Filename in the format {name}-{version}-{release}.{arch}.rpm.
repo                    object                 Repository. See :ref:`rpm_repositories_properties`.
======================  ====================== ======================

.. _rpm_packages_list:

List RPM Packages
-----------------

.. http:get:: /rpmdiff/rest/packages

   Lists all RPM Packages.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/packages HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "arch": "noarch",
              "epoch": "0",
              "filename": "tzdata-2016h-1.fc25.noarch.rpm",
              "id": 1,
              "name": "tzdata",
              "release": "1.fc25",
              "repo": {
                  "id": 1,
                  "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/25/Everything/x86_64/os/"
              },
              "version": "2016h"
          },
          {
              "arch": "x86_64",
              "epoch": "0",
              "filename": "python3-3.6.1-8.fc26.x86_64.rpm",
              "id": 4,
              "name": "python3",
              "release": "8.fc26",
              "repo": {
                  "id": 2,
                  "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/26/Everything/x86_64/os/"
              },
              "version": "3.6.1"
          },
      ]

   :query id: the RPM Package id
   :query name: the RPM Package name
   :query arch: the RPM Package architecture
   :query epoch: the RPM Package epoch
   :query version: the RPM Package version
   :query release: the RPM Package release
   :query repository_id: the id of the RPM Repository
   :query repository_path: the path to the RPM Repository
   :query offset: offset number, default is 0
   :query limit: limit number, default is 100
   :statuscode 200: no error


.. _rpm_packages_one:

Get one RPM Package
-------------------

.. http:get:: /rpmdiff/rest/packages/(int:id)

   Get RPM Package based on id.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/packages/1 HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "arch": "noarch",
              "epoch": "0",
              "filename": "tzdata-2016h-1.fc25.noarch.rpm",
              "id": 1,
              "name": "tzdata",
              "release": "1.fc25",
              "repo": {
                  "id": 1,
                  "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/25/Everything/x86_64/os/"
              },
              "version": "2016h"
          }
      ]

   :param id: the RPM Package id
   :statuscode 200: no error
