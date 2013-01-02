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

API calls which do not require data have a fixed number of required
arguments. Those which do need data take it in the form of optional keword
arguments. For example, ::

    client.update_account(acct_id, name="somename", realm="superfunrealm")

Dictionaries and lists will automatically be converted to their appropriate
representation so you can do things like: ::

    client.update_callflow(acct_id, callflow_id, flow={"module":"it"})

Invalid data will result in an exception explaining the problem.

You can see a list of available methods at: https://kazoo-api.readthedocs.org/en/latest/
