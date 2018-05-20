.. _rpm_comments:

RPM Comments
============

RPM Comments resource represents comments for RPM Comparisons of RPM Differences.

.. _rpm_comments_properties:

Properties of RPM Comments
--------------------------

======================  ====================== ======================
Attribute               Type                   Description
======================  ====================== ======================
id                      int                    Unique identifier of the RPM Comment.
text                    string                 Text of the RPM Comment.
time                    date-time              When the RPM Comment was created.
username                string                 Username of the author.
comparison              object                 RPM Comparison. See :ref:`rpm_comparisons_properties`.
difference              object                 RPM Difference. See :ref:`rpm_differences_properties_specific`.
======================  ====================== ======================

.. _rpm_comments_list:

List RPM Comments
-----------------

.. http:get:: /rpmdiff/rest/comments

   Lists all RPM Comments.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/comments HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "comparison": {
                  "id": 1,
                  "state": "done"
              },
              "id": 1,
              "text": "Example comment for RPM Comparison",
              "time": "2018-04-21 14:16:37",
              "username": "user1"
          },
          {
              "difference": {
                    "category": "tags",
                    "diff": "DESCRIPTION",
                    "diff_info": "S.5.....",
                    "diff_type": "changed",
                    "id": 1853,
                    "state": "normal",
                    "waived": false
              },
              "id": 2,
              "text": "Example comment for RPM Difference",
              "time": "2018-04-21 14:17:28",
              "username": "user1"
          },
      ]

   :query id: the RPM Comment id
   :query comparison_id: the RPM Comparison id
   :query comparison_state: the RPM Comparison state, options: new, done, error
   :query difference_id: the RPM Difference id
   :query difference_category: the RPM Difference category, options: tags, dependencies, files
   :query difference_diff: name of the object that differs
   :query difference_diff_type: the RPM Difference type, options: added, removed, changed
   :query difference_diff_info: changed file attributes
   :query difference_state: the RPM Difference state, options: normal
   :query difference_waived: if the RPM Difference is waived, options: true, false
   :query offset: offset number, default is 0
   :query limit: limit number, default is 100
   :statuscode 200: no error

.. _rpm_comments_create:

Create new RPM Comment
----------------------

.. http:post:: /rpmdiff/rest/comments

   Create new RPM Comment. Authentication is required.

   **Example request**:

   .. sourcecode:: http

      POST /rpmdiff/rest/comments HTTP/1.1
      Host: archdiffer.example.com
      Authorization: Basic base64=encoded=string
      Content-Type: application/json

      {
          "text": "Text of this new comment.",
          "id_comp": 1
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Location: /rpmdiff/rest/comments/<new comment id>

   **Example error response**:

   .. sourcecode:: http

      HTTP/1.1 400 BAD REQUEST

      {
          "message": "Incorrect data format: please provide dict with 'text' and either 'id_comp' or 'id_diff'."
      }

   :reqheader Authentication: basic authentication using api_login and api_token required
   :resheader Location: contains URL of the new RPM Comment
   :statuscode 201: created new RPM Comment
   :statuscode 400: bad request - the data don't fulfill all the requirements
   :statuscode 401: the authentication failed

.. _rpm_comments_one:

Get one RPM Comment
-------------------

.. http:get:: /rpmdiff/rest/comments/(int:id)

   Get RPM Comment based on id.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/comments/1 HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "comparison": {
                  "id": 1,
                  "state": "done"
              },
              "id": 1,
              "text": "Example comment for RPM Comparison",
              "time": "2018-04-21 14:16:37",
              "username": "user1"
          }
      ]

   :param id: the RPM Comment id
   :statuscode 200: no error


.. _rpm_comments_by_comp:

List RPM Comments by RPM Comparison id
--------------------------------------

.. http:get:: /rpmdiff/rest/comments/by_comp/(int:id)

   List RPM Comments based on associated RPM Comparison id.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/comments/by_comp/1 HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "comparison": {
                  "id": 1,
                  "state": "done"
              },
              "id": 1,
              "text": "Example comment for RPM Comparison",
              "time": "2018-04-21 14:16:37",
              "username": "user1"
          },
      ]

   :param id: the RPM Comparison id
   :statuscode 200: no error


.. _rpm_comments_by_diff:

List RPM Comments by RPM Difference id
--------------------------------------

.. http:get:: /rpmdiff/rest/comments/by_diff/(int:id)

   List RPM Comments based on associated RPM Difference id.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/comments/by_diff/1853 HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "difference": {
                    "category": "tags",
                    "diff": "DESCRIPTION",
                    "diff_info": "S.5.....",
                    "diff_type": "changed",
                    "id": 1853,
                    "state": "normal",
                    "waived": false
              },
              "id": 2,
              "text": "Example comment for RPM Difference",
              "time": "2018-04-21 14:17:28",
              "username": "user1"
          },
      ]

   :param id: the RPM Difference id
   :statuscode 200: no error


.. _rpm_comments_by_user:

List RPM Comments by username
-----------------------------

.. http:get:: /rpmdiff/rest/comments/by_user/(string:username)

   List RPM Comments based on username of its author.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/comments/by_user/user1 HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "comparison": {
                  "id": 1,
                  "state": "done"
              },
              "id": 1,
              "text": "Example comment for RPM Comparison",
              "time": "2018-04-21 14:16:37",
              "username": "user1"
          },
          {
              "difference": {
                    "category": "tags",
                    "diff": "DESCRIPTION",
                    "diff_info": "S.5.....",
                    "diff_type": "changed",
                    "id": 1853,
                    "state": "normal",
                    "waived": false
              },
              "id": 2,
              "text": "Example comment for RPM Difference",
              "time": "2018-04-21 14:17:28",
              "username": "user1"
          },
      ]

   :param username: username of the author
   :statuscode 200: no error
