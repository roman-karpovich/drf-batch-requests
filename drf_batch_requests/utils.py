def get_attribute(instance, attrs):
    for attr in attrs:
        if instance is None:
            return None

        if attr == '*':
            # todo: maybe there should be some kind of filtering?
            continue

        if isinstance(instance, list):
            instance = list(map(lambda i: i[attr], instance))
        else:
            instance = instance[attr]
    return instance
