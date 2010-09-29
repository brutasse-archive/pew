Pew
===

A read-only, real-time command-line Twitter client.

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
* Profit
