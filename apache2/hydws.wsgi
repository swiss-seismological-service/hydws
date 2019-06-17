""
hydws wsgi file
see also:
  - http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/
"""

# NOTE: In case you would like to place the hydws_conf file on a custom
# location comment out the two lines bellow. Also, adjust the path to the
# configuration file.
#import hydws.settings as settings
#settings.PATH_HYDWS_CONF = '/path/to/your/custom/hydws_config'

from hydws.server.app import main
application = main()
