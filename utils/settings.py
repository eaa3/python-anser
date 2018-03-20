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

def get_settings(settings_type, filename='config.yaml'):
    settings_dict = import_settings_file(filename)
    system_config = settings_dict['system']
    model_config = settings_dict['model']
    filter_config = settings_dict['filter']
    solver_config = settings_dict['solver']
    calibration_config = settings_dict['calibration']

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




