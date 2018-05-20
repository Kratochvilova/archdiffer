.. _rpm_groups:

RPM Groups
==========

RPM Groups resource represents groups of RPM Comparisons. It also corresponds to a Comparisons resource.

.. _rpm_groups_properties:

Properties of RPM Groups
------------------------

======================  ====================== ======================
Attribute               Type                   Description
======================  ====================== ======================
id                      int                    Unique identifier of the Comparison Group.
state                   string                 State of the Comparison Group, options: new, done, error.
time                    date-time              When the Comparison Group was created.
type                    string                 Comparison Type - rpmdiff.
comparisons             array                  List of RPM Comparisons in the group. See :ref:`rpm_comparisons_properties`.
======================  ====================== ======================

.. _rpm_groups_list:

List RPM Groups
---------------

.. http:get:: /rpmdiff/rest/groups

   Lists all RPM Groups.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/groups HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "comparisons": [
                  {
                      "id": 5,
                      "id_group": 5,
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
                      "time": "2018-04-20 12:19:19",
                      "type": "rpmdiff"
                  },
                  {
                      "id": 4,
                      "id_group": 5,
                      "pkg1": {
                          "arch": "i686",
                          "epoch": "0",
                          "filename": "python3-3.5.2-4.fc25.i686.rpm",
                          "id": 7,
                          "name": "python3",
                          "release": "4.fc25",
                          "repo": {
                              "id": 1,
                              "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/25/Everything/x86_64/os/"
                          },
                          "version": "3.5.2"
                      },
                      "pkg2": {
                          "arch": "i686",
                          "epoch": "0",
                          "filename": "python3-3.6.1-8.fc26.i686.rpm",
                          "id": 8,
                          "name": "python3",
                          "release": "8.fc26",
                          "repo": {
                              "id": 2,
                              "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/26/Everything/x86_64/os/"
                          },
                          "version": "3.6.1"
                      },
                      "state": "done",
                      "time": "2018-04-20 12:19:19",
                      "type": "rpmdiff"
                  }
              ],
              "id": 5,
              "state": "done",
              "time": "2018-04-20 12:19:19",
              "type": "rpmdiff"
          }
          (...)
      ]

   :query id: the Comparison Group id
   :query state: the Comparison Group state, options: new, done, error
   :query before: filter Comparison Groups created before given time,
                  formats: "YY-MM-DD", "YY-MM-DD hh:mm:ss"
   :query after: filter Comparison Groups created after given time,
                 formats: "YY-MM-DD", "YY-MM-DD hh:mm:ss"
   :query comparisons_id: the RPM Comparison id - however, the whole group
		          always appears in the result
   :query comparisons_state: the RPM Comparison state, options: new, done, error
			     - however, the whole group always appears in the result
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


.. _rpm_groups_one:

Get one RPM Group
-----------------

.. http:get:: /rpmdiff/rest/groups/(int:id)

   Get RPM Group based on id.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/groups/1 HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "comparisons": [
                  {
                      "id": 5,
                      "id_group": 5,
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
                      "time": "2018-04-20 12:19:19",
                      "type": "rpmdiff"
                  },
                  {
                      "id": 4,
                      "id_group": 5,
                      "pkg1": {
                          "arch": "i686",
                          "epoch": "0",
                          "filename": "python3-3.5.2-4.fc25.i686.rpm",
                          "id": 7,
                          "name": "python3",
                          "release": "4.fc25",
                          "repo": {
                              "id": 1,
                              "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/25/Everything/x86_64/os/"
                          },
                          "version": "3.5.2"
                      },
                      "pkg2": {
                          "arch": "i686",
                          "epoch": "0",
                          "filename": "python3-3.6.1-8.fc26.i686.rpm",
                          "id": 8,
                          "name": "python3",
                          "release": "8.fc26",
                          "repo": {
                              "id": 2,
                              "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/26/Everything/x86_64/os/"
                          },
                          "version": "3.6.1"
                      },
                      "state": "done",
                      "time": "2018-04-20 12:19:19",
                      "type": "rpmdiff"
                  }
              ],
              "id": 5,
              "state": "done",
              "time": "2018-04-20 12:19:19",
              "type": "rpmdiff"
          }
      ]

   :param id: the RPM Group id
   :statuscode 200: no error
