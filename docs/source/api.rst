API Reference
============

The DTI Reviewer API provides endpoints for expert search.

Endpoints
--------

Search Experts
~~~~~~~~~~~~~

Find experts based on a research abstract.

.. code-block:: http

   POST /search
   Content-Type: application/json

   {
     "query": "Your research abstract text here..."
   }

Response:

.. code-block:: json

   {
    "message": "Success",
    "results": [
      {
        "orcid": "A",
        "author": "Alice",
        "similarity": 1.0,
        "name_variations": ["Alice"]
      }
    ]
  }

Parameters:
- ``query`` (string, required): The research abstract to search with

Response Fields:
- ``message`` (string): Status message
- ``results`` (array): List of matching experts
