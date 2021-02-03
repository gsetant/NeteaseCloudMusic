from app.plugins.plugin_demo.lang.lang import I18n

icon = 'data:image/png;base64,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'

def get_info(lang):
    """

    :param lang: i18n support
    :return: plugin info
        {
            'name': 'has to be same as package name',
            'tittle': 'is the tittle shows by website',
            'version': '1.0',
            'github': 'githubUrl',
            'icon': 'should be a accessible url',
        }
    """
    i18n = I18n(lang)
    return {
        'name': i18n.str('name'),
        'tittle': i18n.str('tittle'),
        'version': '0.1.0',
        'github': 'https://github.com/gsetant/NeteaseCloudMusic',
        'icon': icon,
        'content': i18n.str('content')

    }


def get_settings(lang):
    i18n = I18n(lang)
    form = [
        {
            'type': 'text',
            'label': 'text',
            'model': 'text_model',
            'place_holder': 'place_holder',
        },
        {
            'type': 'select',
            'label': 'select',
            'model': 'select_model',
            'option': [
                {
                    'label': 'label-1',
                    'value': 'value-1'
                },
                {
                    'label': 'label-2',
                    'value': 'value-2'
                },
            ]
        },
        {
            'type': 'switch',
            'label': 'switch',
            'model': 'switch_model',
        },
        {
            'type': 'radio',
            'label': 'radio',
            'model': 'radio_model',
            'place_holder': 'place_holder',
            'option': [
                {
                    'label': 'label-1'
                },
                {
                    'label': 'label-2'
                },
            ]
        },
    ]
    return form


