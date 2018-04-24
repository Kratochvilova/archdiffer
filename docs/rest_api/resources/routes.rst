.. _index:

Index
=====

The REST API provides information about available routes.

.. _routes_properties:

Properties of Routes
--------------------

======================  ====================== ======================
Attribute               Type                   Description
======================  ====================== ======================
methods                 list                   Available methods for this route.
routes                  object                 Dict of subroutes.
======================  ====================== ======================

.. _routes_list:

List Routes
-----------

.. http:get:: /rest

   Lists available Routes.

   **Example request**:

   .. sourcecode:: http

      GET /rest HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: text/javascript

      {
          "/rest": {
              "methods": [
                 "GET"
              ],
              "routes": {
                  "/rest/comparison_types": {
                      "methods": [
                          "GET"
                      ],
                      "routes": {
                          "/rest/comparison_types/<int:id>": {
                              "methods": [
                                  "GET"
                              ],
                              "routes": {}
                          }
                      }
                  },
                  "/rest/comparisons": {
                      "methods": [
                          "GET"
                      ],
                      "routes": {
                          "/rest/comparisons/<int:id>": {
                              "methods": [
                                  "GET"
                              ],
                              "routes": {}
                          }
                      }
                  }
              }
          }
      }

   :statuscode 200: no error
