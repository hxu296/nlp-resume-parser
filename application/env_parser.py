ENV_FILE_PATH = '.env'

def parse_env_file():
    env_variables = {}
    try:
        with open(ENV_FILE_PATH, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_variables[key] = value
    except FileNotFoundError:
        return env_variables
    return env_variables
