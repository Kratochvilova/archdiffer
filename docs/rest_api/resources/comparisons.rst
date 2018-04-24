.. _comparisons:

Comparisons
===========

Comparisons resource represents comparisons of package archives.

.. _comparisons_properties:

Properties of Comparisons
-------------------------

======================  ====================== ======================
Attribute               Type                   Description
======================  ====================== ======================
id                      int                    Unique identifier of the Comparison.
state                   string                 State of the Comparison, options: new, done, error.
time                    date-time              When the Comparison was created.
comparison_type         object                 Comparison Type. See :ref:`comparison_types_properties`.
======================  ====================== ======================

.. _comparisons_list:

List Comparisons
----------------

.. http:get:: /rest/comparisons

   Lists all Comparisons.

   **Example request**:

   .. sourcecode:: http

      GET /rest/comparisons HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: text/javascript

      [
          {
              "comparison_type": {
                  "id": 1,
                  "name": "rpmdiff"
              },
              "id": 1,
              "state": "done",
              "time": "2018-04-20 12:18:16"
          },
          {
              "comparison_type": {
                  "id": 1,
                  "name": "rpmdiff"
              },
              "id": 2,
              "state": "done",
              "time": "2018-04-20 12:18:26"
          },
      ]

   :query id: the Comparison id
   :query state: the Comparison state, options: new, done, error
   :query before: filter Comparisons created before given time,
                  formats: "YY-MM-DD", "YY-MM-DD hh:mm:ss"
   :query after: filter Comparisons created after given time,
                 formats: "YY-MM-DD", "YY-MM-DD hh:mm:ss"
   :query comparison_type_id: the Comparison Type id
   :query comparison_type_name: the Comparison Type name
   :query offset: offset number, default is 0
   :query limit: limit number, default is 100
   :statuscode 200: no error


.. _comparisons_one:

Get one Comparison
------------------

.. http:get:: /rest/comparisons/(int:id)

   Get Comparison based on id.

   **Example request**:

   .. sourcecode:: http

      GET /rest/comparisons/1 HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: text/javascript

      [
          {
              "comparison_type": {
                  "id": 1,
                  "name": "rpmdiff"
              },
              "id": 1,
              "state": "done",
              "time": "2018-04-20 12:18:16"
          }
      ]

   :param id: the Comparison id
   :statuscode 200: no error
