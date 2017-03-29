import configparser

class Configuration:
    """ Configuration class for shsmd.

        Attributes:
            database  (str): Path to sqlite database.
            debug (boolean): Toggle to enable debug.
    """

    def __init__(self, path):
        """ Configuration class initialisation.

        """

        config = configparser.RawConfigParser()
        config.read(path)

        self.debug = config.getboolean('general', 'debug')
        self.api_url = config.get('general', 'api_url')
        self.key_dir = config.get('general', 'key_dir')
        self.username = config.get('general', 'username')
