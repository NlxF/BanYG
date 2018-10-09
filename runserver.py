#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bwg360 import create_app

app = create_app()

if __name__ == "__main__":

    app.run(debug=app.debug, port=5001, host='0.0.0.0')
