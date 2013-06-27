YHandler
========

Yahoo Fantasy Sports OAuth And Request Handler

This connects to the Yahoo Fantasy Sports API via OAuth. It's not robust, but following these steps should work:
- Place your client key, and client secret in a file, e.g. auth.csv
- call: import from YHandler *
- create a handler with: var_name = YHandler('auth.csv')

This is a fork of https://github.com/mleveck/YHandler refactored to work with the newer requests-1.0+ and requests-oauthlib, which you can install using pip:

**requests:** http://docs.python-requests.org/en/latest/

**requests-oauthlib:** https://github.com/requests/requests-oauthlib
