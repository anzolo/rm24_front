from bottle import run, default_app

import conf
import common
import adminka
import remontas

# Run bottle internal test server when invoked directly ie: non-uxsgi mode
if __name__ == '__main__':
    run(host='0.0.0.0', port=8080)
# Run bottle in application mode. Required in order to get the application working with uWSGI!
else:
    app = application = default_app()

    # acc1aca627  55
