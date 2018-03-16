import yaml


def import_settings(filename='config.yaml'):

    with open(filename, 'r') as stream:
        try:
            settings_dict = yaml.load(stream)
            stream.close()
            system_config = settings_dict['system']
            model_config = settings_dict['model']
            filter_config = settings_dict['filter']
            calibration_config = settings_dict['calibration']

            return system_config, model_config, filter_config, calibration_config
        except yaml.YAMLError as exc:
            print(exc)
            return 1



def export_settings(filename='config.yaml'):
    pass