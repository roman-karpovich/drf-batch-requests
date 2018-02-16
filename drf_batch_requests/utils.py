import random
import string


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


def generate_random_id(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_node_callback(node, status):
    def callback():
        if status == 'start':
            node.start()
        elif status == 'success':
            node.complete()
        elif status == 'fail':
            node.fail()
        else:
            raise NotImplementedError

    return callback