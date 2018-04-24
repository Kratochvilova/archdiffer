.. _rpm_repositories:

RPM Repositories
================

RPM Repositories resource represents repositories.

.. _rpm_repositories_properties:

Properties of RPM Repositories
------------------------------

======================  ====================== ======================
Attribute               Type                   Description
======================  ====================== ======================
id                      int                    Unique identifier of the RPM Repository.
path                    string                 URL of the RPM Repository.
======================  ====================== ======================

.. _rpm_repositories_list:

List RPM Repositories
---------------------

.. http:get:: /rpmdiff/rest/repositories

   Lists all RPM Repositories.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/repositories HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: text/javascript

      [
          {
              "id": 1,
              "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/25/Everything/x86_64/os/"
          },
          {
              "id": 2,
              "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/26/Everything/x86_64/os/"
          }
      ]

   :query id: the RPM Repository id
   :query path: the path to the RPM Repository
   :query offset: offset number, default is 0
   :query limit: limit number, default is 100
   :statuscode 200: no error


.. _rpm_repositories_one:

Get one RPM Repository
----------------------

.. http:get:: /rpmdiff/rest/repositories/(int:id)

   Get RPM Repository based on id.

   **Example request**:

   .. sourcecode:: http

      GET /rpmdiff/rest/repositories/1 HTTP/1.1
      Host: archdiffer.example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: text/javascript

      [
          {
              "id": 1,
              "path": "http://mirror.karneval.cz/pub/fedora/linux/releases/25/Everything/x86_64/os/"
          }
      ]

   :param id: the RPM Repository id
   :statuscode 200: no error
