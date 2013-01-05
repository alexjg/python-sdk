Installing
==========

Install from pip::

    pip install kazoo-api


Authentication
==============

Either authenticate using a username/password pair::

    import kazoo
    client = kazoo.Client(username="myusername", password="mypassword", account_name="my account name")
    client.authenticate()

Or using an api key::

    import kazoo
    client = kazoo.Client(api_key="sdfasdfas")
    client.authenticate()

API calls which require data take it in the form of a required argument
called 'data' which is the last argument to the method. For example ::

    client.update_account(acct_id, {"name": "somename", "realm":"superfunrealm"})

Dictionaries and lists will automatically be converted to their appropriate
representation so you can do things like: ::

    client.update_callflow(acct_id, callflow_id, {"flow":{"module":"somemodule"}})

Invalid data will result in an exception explaining the problem.

You can see a list of available methods at: https://kazoo-api.readthedocs.org/en/latest/
