def kebab_to_snake_case(json):
    if isinstance(json, dict):
        return kebab_to_snake_case_dict(json)
    if isinstance(json, list):
        new_json = []
        for d in json:
            if isinstance(d, dict):
                new_json.append(kebab_to_snake_case_dict)
    return json


def kebab_to_snake_case_dict(d: dict):
    return {key.replace('-', '_'): kebab_to_snake_case(value) for key, value in d.items()}
