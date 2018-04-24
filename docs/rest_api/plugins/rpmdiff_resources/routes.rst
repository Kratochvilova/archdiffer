.. _rpmdiff_index:

Index
=====

The REST API provides information about available routes.

.. _rpmdiff_routes_properties:

Properties of routes
--------------------

==================  ==================== ===============
Attribute           Type                 Description
==================  ==================== ===============
methods             list                 available methods for this route
routes              object               dict of subroutes
==================  ==================== ===============

.. _rpmdiff_routes_list:

List routes
-----------

.. http:get:: /rest

   Lists available routes.

   **Example request**:

   .. sourcecode:: http

      GET /rest HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: text/javascript

      {
          "/rpmdiff/rest": {
              "methods": [
                  "GET"
              ],
              "routes": {
                  "/rpmdiff/rest/add_comment": {
                      "methods": [
                          "POST"
                      ],
                      "routes": {}
                  },
                  "/rpmdiff/rest/add_comparison": {
                      "methods": [
                          "POST"
                      ],
                      "routes": {}
                  },
                  "/rpmdiff/rest/comments": {
                      "methods": [
                          "GET"
                      ],
                      "routes": {
                          "/rpmdiff/rest/comments/<int:id>": {
                              "methods": [
                                  "GET"
                              ],
                              "routes": {}
                          },
                          "/rpmdiff/rest/comments/by_comp/<int:id_comp>": {
                              "methods": [
                                  "GET"
                              ],
                              "routes": {}
                          },
                          "/rpmdiff/rest/comments/by_diff/<int:id_diff>": {
                              "methods": [
                                  "GET"
                              ],
                              "routes": {}
                          },
                          "/rpmdiff/rest/comments/by_user/<string:username>": {
                              "methods": [
                                  "GET"
                              ],
                              "routes": {}
                          }
                      }
                  },
                  "/rpmdiff/rest/comparisons": {
                      "methods": [
                          "GET"
                      ],
                      "routes": {
                          "/rpmdiff/rest/comparisons/<int:id>": {
                              "methods": [
                                  "GET"
                              ],
                              "routes": {}
                          }
                      }
                  },
                  "/rpmdiff/rest/differences": {
                      "methods": [
                          "GET"
                      ],
                      "routes": {
                          "/rpmdiff/rest/differences/<int:id>": {
                              "methods": [
                                  "GET"
                              ],
                              "routes": {}
                          }
                      }
                  },
                  "/rpmdiff/rest/groups": {
                      "methods": [
                          "GET"
                      ],
                      "routes": {
                          "/rpmdiff/rest/groups/<int:id>": {
                              "methods": [
                                  "GET"
                              ],
                              "routes": {}
                          }
                      }
                  },
                  "/rpmdiff/rest/packages": {
                      "methods": [
                          "GET"
                      ],
                      "routes": {
                          "/rpmdiff/rest/packages/<int:id>": {
                              "methods": [
                                  "GET"
                              ],
                              "routes": {}
                          }
                      }
                  },
                  "/rpmdiff/rest/repositories": {
                      "methods": [
                          "GET"
                      ],
                      "routes": {
                          "/rpmdiff/rest/repositories/<int:id>": {
                              "methods": [
                                  "GET"
                              ],
                              "routes": {}
                          }
                      }
                  },
                  "/rpmdiff/rest/unwaive/<int:id>": {
                      "methods": [
                          "PUT"
                      ],
                      "routes": {}
                  },
                  "/rpmdiff/rest/waive/<int:id>": {
                      "methods": [
                          "PUT"
                      ],
                      "routes": {}
                  }
              }
          }
      }

   :statuscode 200: no error
