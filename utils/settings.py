import ruamel_yaml


def import_settings_file(filename='config.yaml'):

    with open(filename, 'r') as stream:
        try:
            settings_dict = ruamel_yaml.load(stream)
            stream.close()
            return settings_dict
        except ruamel_yaml.YAMLError as exc:
            print(exc)
            return 1

def export_settings(filename='config.yaml'):
    pass

def get_settings(settings_type='', filename='config.yaml'):
    config = import_settings_file(filename)
    system_config = config['system']
    model_config = config['model']
    filter_config = config['filter']
    solver_config = config['solver']
    calibration_config = config['calibration']

    if settings_type == 'system':
        return system_config
    elif settings_type == 'model':
        return model_config
    elif settings_type == 'filter':
        return filter_config
    elif settings_type == 'solver':
        return solver_config
    elif settings_type == 'calibration':
        return calibration_config
    else:
        return config



def get_calibration(filename='calibration.yaml'):

    cals = import_settings_file(filename)

    return cals

def write_calibration(cals, filename='calibration.yaml'):

    with open(filename, 'w') as stream:
        try:
            ruamel_yaml.dump(cals, stream)
            return 0
        except ruamel_yaml.YAMLError as exc:
            print(exc)
            return 1