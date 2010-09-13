Pew
===

A read-only, real-time command-line Twitter client.

Disclaimer
----------

The UserStream API is still in beta, and is not ready for released products.
Do not package this app for end users, the intended audience is limited to
[python] developers.

See `ChirpUserStreams`_ and `Implementation Suggestions`_ for more information.

.. _ChirpUserStreams: http://dev.twitter.com/pages/user_streams
.. _Implementation Suggestions: http://dev.twitter.com/pages/user_streams_suggestions

Usage
-----

* ``mkvirtualenv pew && easy_install pip && pip install -r requirements.txt``
* Register an app on https://twitter.com/apps/new
* Get a token for it using `this script`_ for instance
* Put in ``~/.pewrc``:

.. _this script: http://gist.github.com/545143

  ::

      [OAuth]
      consumer_secret = your consumer secret
      consumer_key = your consumer key
      token_secret = your token secret
      token_key = your token key

* Run ``python src/pew/main.py``
