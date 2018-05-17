.. _rpm_comparisons:

RPM Comparisons
===============

RPM Comparisons resource represents comparisons of two RPM Packages.

.. _rpm_comparisons_properties:

Properties of RPM Comparisons
-----------------------------

======================  ====================== ======================
Attribute               Type                   Description
======================  ====================== ======================
id                      int                    Unique identifier of the RPM Comparison.
id_group                int                    Unique identifier of the Comparison group.
state                   string                 State of the RPM Comparison, options: new, done, error
time                    date-time              When the Comparison group was created.
type                    string                 Type of the Comparison group: rpmdiff
pkg1                    object                 First Package. See :ref:`rpm_packages_properties`.
pkg1                    object                 Second Package. See :ref:`rpm_packages_properties`.
======================  ====================== ======================


.. _rpm_comparisons_list:

List RPM Comparisons
--------------------

.. http:get:: /rpmdiff/rest/comparisons

   Lists all RPM Comparisons.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/comparisons HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: text/javascript

      [
          {
              "id": 1,
              "id_group": 1,
              "pkg1": {
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
              "pkg2": {
                  "arch": "noarch",
                  "epoch": "0",
                  "filename": "tzdata-2017b-1.fc26.noarch.rpm",
                  "id": 2,
                  "name": "tzdata",
                  "release": "1.fc26",
                  "repo": {
                      "id": 2,
                      "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/26/Everything/x86_64/os/"
                  },
                  "version": "2017b"
              },
              "state": "done",
              "time": "2018-04-20 12:18:16",
              "type": "rpmdiff"
          },
          {
              "id": 2,
              "id_group": 2,
              "pkg1": {
                  "arch": "x86_64",
                  "epoch": "0",
                  "filename": "python3-3.5.2-4.fc25.x86_64.rpm",
                  "id": 3,
                  "name": "python3",
                  "release": "4.fc25",
                  "repo": {
                      "id": 1,
                      "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/25/Everything/x86_64/os/"
                  },
                  "version": "3.5.2"
              },
              "pkg2": {
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
              "state": "done",
              "time": "2018-04-20 12:18:26",
              "type": "rpmdiff"
          },
      ]

   :query id: the RPM Comparison id
   :query state: the RPM Comparison state, options: new, done, error
   :query group_id: the Comparison group id
   :query group_state: the state of the Comparison group, options: new, done, error
   :query group_before: filter RPM Comparisons with groups created before given time,
                  formats: "YY-MM-DD", "YY-MM-DD hh:mm:ss"
   :query group_after: filter RPM Comparisons with groups created after given time,
                 formats: "YY-MM-DD", "YY-MM-DD hh:mm:ss
   :query pkg1_id: the pkg1 id
   :query pkg1_name: the pkg1 name
   :query pkg1_arch: the pkg1 architecture
   :query pkg1_epoch: the pkg1 epoch
   :query pkg1_version: the pkg1 version
   :query pkg1_release: the pkg1 release
   :query pkg2_id: the pkg2 id
   :query pkg2_name: the pkg2 name
   :query pkg2_arch: the pkg2 architecture
   :query pkg2_epoch: the pkg2 epoch
   :query pkg2_version: the pkg2 version
   :query pkg2_release: the pkg2 release
   :query repo1_id: the id of the RPM Repository of pkg1
   :query repo1_path: the path to the RPM Repository of pkg1
   :query repo2_id: the id of the RPM Repository of pkg2
   :query repo2_path: the path to the RPM Repository of pkg2
   :query offset: offset number, default is 0
   :query limit: limit number, default is 100
   :statuscode 200: no error


.. _rpm_comparisons_create:

Create new RPM Comparison
-------------------------

.. http:post:: /rpmdiff/rest/comparisons

   Create new RPM Comparison. Authentication is required.


   **Example minimal request**:

   .. sourcecode:: http

      POST /rpmdiff/rest/comparisons HTTP/1.1
      Host: archdiffer.example.com
      Authorization: Basic base64=encoded=string
      Content-Type: text/javascript

      {
          "pkg1": {
              "name": "python3",
              "repository":"http://mirror.karneval.cz/pub/fedora/linux/releases/25/Everything/x86_64/os/"
          },
          "pkg2": {
              "name": "python3",
              "repository":"http://mirror.karneval.cz/pub/fedora/linux/releases/26/Everything/x86_64/os/"
          }
      }

   **Example full request**:

   .. sourcecode:: http

      POST /rpmdiff/rest/comparisons HTTP/1.1
      Host: archdiffer.example.com
      Authorization: Basic base64=encoded=string
      Content-Type: text/javascript

      {
          "pkg1": {
              "name": "python3",
              "arch": "x86_64",
              "epoch": 0,
              "version": "3.5.2",
              "release": "4.fc25",
              "repository":"http://mirror.karneval.cz/pub/fedora/linux/releases/25/Everything/x86_64/os/"
          },
          "pkg2": {
              "name": "python3",
              "arch": "x86_64",
              "epoch": 0,
              "version": "3.6.1",
              "release": "8.fc26",
              "repository":"http://mirror.karneval.cz/pub/fedora/linux/releases/26/Everything/x86_64/os/"
          }
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Location: /rpmdiff/rest/comparisons/<new comparison id>

   **Example error response**:

   .. sourcecode:: http

      HTTP/1.1 400 BAD REQUEST

      {
          "message": "Incorrect data format: please provide dict with 'pkg1' and 'pkg2' dicts."
      }

   :reqheader Authentication: basic authentication using api_login and api_token required
   :resheader Location: contains URL of the new RPM Comparison
   :statuscode 201: created new RPM Comparison
   :statuscode 400: bad request - the data don't fulfill all the requirements
   :statuscode 401: the authentication failed

.. _rpm_comparisons_one:

Get one RPM Comparison
----------------------

.. http:get:: /rpmdiff/rest/comparisons/(int:id)

   Get RPM Comparison based on id.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/comparisons/1 HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: text/javascript

      [
          {
              "id": 1,
              "id_group": 1,
              "pkg1": {
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
              "pkg2": {
                  "arch": "noarch",
                  "epoch": "0",
                  "filename": "tzdata-2017b-1.fc26.noarch.rpm",
                  "id": 2,
                  "name": "tzdata",
                  "release": "1.fc26",
                  "repo": {
                      "id": 2,
                      "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/26/Everything/x86_64/os/"
                  },
                  "version": "2017b"
              },
              "state": "done",
              "time": "2018-04-20 12:18:16",
              "type": "rpmdiff"
          }
      ]

   :param id: the RPM Comparison id
   :statuscode 200: no error
