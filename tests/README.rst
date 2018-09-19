# README

To test with the client:

.. code-block:: python

    def test_with_the_client(client):
        response = client.get('<url>', query_string={'<key>': '<value>'})

        # To get json result
        response.json

`client` is a fixture for a flask test client
