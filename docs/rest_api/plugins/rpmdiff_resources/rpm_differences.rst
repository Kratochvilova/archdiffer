
.. _rpm_differences:

RPM Differences
===============

RPM Differences resource represents differences between two RPM Packages as a result of some RPM Comparison.

.. _rpm_differences_properties:

Properties
----------

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
differences             array                  List of the RPM Differences. See :ref:`rpm_differences_properties_specific`.
======================  ====================== ======================

.. _rpm_differences_properties_specific:

Properties of RPM Differences
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

======================  ====================== ======================
Attribute               Type                   Description
======================  ====================== ======================
id                      int                    Unique identifier of the RPM Difference.
category                string                 Category of the RPM Difference, options: tags, dependencies, files.
diff                    string                 Name of the object in the RPM Package that differs (e.g. name of changed file)
diff_type               string                 Type of the RPM Difference, options: added, removed, changed.
diff_info               string                 Other info about the difference - changed file attributes.
state                   string                 State of the RPM Difference (for future use), options: normal.
waived                  bool                   Whether the RPM Difference is waived.
======================  ====================== ======================

.. _rpm_differences_list:

List RPM Differences
--------------------

.. http:get:: /rpmdiff/rest/differences

   Lists RPM Comparisons together with their lists of RPM Differences.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/differences HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "differences": [
                  {
                      "category": "tags",
                      "diff": "DESCRIPTION",
                      "diff_info": "S.5.....",
                      "diff_type": "changed",
                      "id": 1853,
                      "state": "normal",
                      "waived": false
                  },
                  {
                      "category": "dependencies",
                      "diff": "REQUIRES libpython3.5m.so.1.0()(64bit)  ",
                      "diff_info": null,
                      "diff_type": "removed",
                      "id": 1858,
                      "state": "normal",
                      "waived": false
                  },
              ],
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
   :query difference_id: the RPM Difference id
   :query difference_category: the RPM Difference category, options: tags, dependencies, files
   :query difference_diff: name of the object that differs
   :query difference_diff_type: the RPM Difference type, options: added, removed, changed
   :query difference_diff_info: changed file attributes
   :query difference_state: the RPM Difference state, options: normal
   :query difference_waived: if the RPM Difference is waived, options: true, false
   :query offset: offset number, default is 0 - the offset is set on the individual differences
   :query limit: limit number, default is 100 - the limit is set on the individual differences
   :statuscode 200: no error


.. _rpm_differences_one:

Get RPM Differences of one RPM Comparison
---------------------------------------------

.. http:get:: /rpmdiff/rest/differences/(int:id)

   Get RPM Differences of one RPM Comparison based on id.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/differences/1 HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "differences": [
                  {
                      "category": "tags",
                      "diff": "DESCRIPTION",
                      "diff_info": "S.5.....",
                      "diff_type": "changed",
                      "id": 1853,
                      "state": "normal",
                      "waived": false
                  },
                  {
                      "category": "dependencies",
                      "diff": "REQUIRES libpython3.5m.so.1.0()(64bit)  ",
                      "diff_info": null,
                      "diff_type": "removed",
                      "id": 1858,
                      "state": "normal",
                      "waived": false
                  },
              ],
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
          }
      ]

   :param id: the RPM Comparison id
   :statuscode 200: no error

.. _rpm_differences_waive:

Waive RPM Difference
--------------------

.. http:put:: /rpmdiff/rest/differences/(int:id)

   Waive or unwaive RPM Difference. Authentication is required.

   **Example request**:

   .. sourcecode:: http

      PUT /rpmdiff/rest/differences/1 HTTP/1.1
      Host: archdiffer.example.com
      Authorization: Basic base64=encoded=string
      Content-Type: application/json

      "waive"

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT

   **Example error response**:

   .. sourcecode:: http

      HTTP/1.1 400 BAD REQUEST

      {
          "message": "No data: please provide string 'waive' or 'unwaive'."
      }

   :reqheader Authentication: basic authentication using api_login and api_token required
   :statuscode 204: NO CONTENT
   :statuscode 400: bad request - the data don't fulfill all the requirements
   :statuscode 401: the authentication failed
