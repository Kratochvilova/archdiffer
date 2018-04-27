.. _rest_api:

********
REST API
********

Welcome to the documentation of REST API for Archdiffer and its plugins.

.. toctree::
   :maxdepth: 3
   :glob:

   common.rst
   plugins/*


Authentication
--------------

Accessing stored data is possible without authentication. For modifying data, the authentication is required.

To authenticate, provide login:token using the basic HTTP authentication.

The login and token can be obtained and renewed at the /api page.
