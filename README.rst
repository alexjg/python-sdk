Installing
==========

Install from pip::

    pip install kazoo-api


Authentication
==============

Either authenticate using a username/password pair::

    >>>import kazoo
    >>>client = kazoo.Client(username="myusername", password="mypassword", account_name="my account name")
    >>>client.authenticate()

Or using an api key::

    >>>import kazoo
    >>>client = kazoo.Client(api_key="sdfasdfas")
    >>>client.authenticate()

API calls which require data take it in the form of a required argument
called 'data' which is the last argument to the method. For example ::

    >>>client.update_account(acct_id, {"name": "somename", "realm":"superfunrealm"})

Dictionaries and lists will automatically be converted to their appropriate
representation so you can do things like: ::

    >>>client.update_callflow(acct_id, callflow_id, {"flow":{"module":"somemodule"}})

Invalid data will result in an exception explaining the problem.

The server response is returned from each method as a python dictionary of
the returned JSON object, for example: ::

    >>>client.get_account(acct_id)
    {u'auth_token': u'abc437daf8517d0454cc984f6f09daf3',
     u'data': {u'billing_mode': u'normal',
      u'caller_id': {},
      u'caller_id_options': {},
      u'id': u'c4f64412ad0057222c12559a3e7da011',
      u'media': {u'bypass_media': u'auto'},
      u'music_on_hold': {},
      u'name': u'test3',
      u'notifications': {},
      u'realm': u'4c8b50.sip.2600hz.com',
      u'superduper_admin': False,
      u'timezone': u'America/Los_Angeles',
      u'wnm_allow_additions': False},
     u'request_id': u'ea6441422fb85f67ad21db4f1e2326c1',
     u'revision': u'3-c16dd0a629fe1da254fe1e7b3e5fb35a',
     u'status': u'success'}


You can see a list of available methods at: https://kazoo-api.readthedocs.org/en/latest/
