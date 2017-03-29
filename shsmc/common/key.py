def save_key(key, filename):
    """ Save key to file.
    """

    key_file = open(filename, 'w')
    key_file.write(key.decode('utf-8'))
    key_file.close()

def load_key(filename):
    """ Load key from file.
    """

    key_file = open(filename, 'r')
    key = key_file.read().encode()
    key_file.close()
    return key
