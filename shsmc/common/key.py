def save_key(key, filename):
    key_file = open(filename, 'w')
    key_file.write(key)
    key_file.close()

def load_key(filename):
    key_file = open(filename, 'r')
    key = key_file.read()
    key_file.close()
    return key
