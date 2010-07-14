Pew
===

An experiment with Twitter's UserStreams.

Disclaimer
----------

The UserStream API is still in beta, and is not ready for released products.
Do not package this app for end users, the intended audience is limited to
[python] developers.

See `ChirpUserStreams`_ and `Implementation Suggestions`_ for more information.

.. _ChirpUserStreams: http://apiwiki.twitter.com/ChirpUserStreams
.. _Implementation Suggestions: http://apiwiki.twitter.com/User-Stream-Implementation-Suggestions

Usage
-----

* ``mkvirtualenv pew && easy_install pip && pip install -r requirements.txt``
* Register an app on https://twitter.com/apps/new
* Get a token for it (if you don't know how to do it, don't use this project)
* Put in ``~/.pewrc``:

  ::

      [OAuth]
      consumer_secret = your consumer secret
      consumer_key = your consumer key
      token_secret = your token secret
      token_key = your token key

* Run ``python src/pew/main.py``
