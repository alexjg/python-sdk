Installing
==========

Install from pip::

    pip install kazoo


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
