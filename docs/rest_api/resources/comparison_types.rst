.. _comparison_types:

Comparison Types
================

Comparison Type resource represents types of comparisons, e.g. rpmdiff.

.. _comparison_types_properties:

Properties of Comparison Types
------------------------------

======================  ====================== ======================
Field                   Type                   Description
======================  ====================== ======================
id                      int                    Unique Comparison Type identifier.
name                    string                 Unique name of the Comparison Type.
======================  ====================== ======================

.. _comparison_types_list:

List Comparison Types
---------------------

.. http:get:: /rest/comparison_types

   Lists all Comparison Types.

   **Example request**:

   .. sourcecode:: http

      GET /rest/comparison_types HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "id": 1,
              "name": "rpmdiff"
          }
      ]

   :query id: the Comparison Type id
   :query name: the Comparison Type name
   :query offset: offset number, default is 0
   :query limit: limit number, default is 100
   :statuscode 200: no error


.. _comparison_types_one:

Get one Comparison Type
-----------------------

.. http:get:: /rest/comparison_types/(int:id)

   Get Comparison Type based on id.

   **Example request**:

   .. sourcecode:: http

      GET /rest/comparison_types/1 HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "id": 1,
              "name": "rpmdiff"
          }
      ]

   :param id: the Comparison Type id
   :statuscode 200: no error
