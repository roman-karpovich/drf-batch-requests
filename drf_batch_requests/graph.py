class RequestGraphNode(object):
    STATUS_FAILED = -1
    STATUS_FAILED_PARENT = -2
    STATUS_NOT_STARTED = 0
    STATUS_IN_PROGRESS = 1
    STATUS_COMPLETED = 2

    def __init__(self, request=None):
        self.request = request
        self.name = self.request.get('name')
        self.parents = set()
        self.children_set = set()
        self.status = self.STATUS_NOT_STARTED

    def start(self):
        self.status = RequestGraphNode.STATUS_IN_PROGRESS

    def complete(self):
        self.status = RequestGraphNode.STATUS_COMPLETED

    def fail(self, own_fail=True):
        self.status = RequestGraphNode.STATUS_FAILED if own_fail else RequestGraphNode.STATUS_FAILED_PARENT
        for child_node in filter(lambda n: n.status == RequestGraphNode.STATUS_NOT_STARTED, self.children_set):
            child_node.fail(own_fail=False)

    @property
    def can_be_performed(self):
        return self.status == RequestGraphNode.STATUS_NOT_STARTED and \
               all(map(lambda parent: parent.status == RequestGraphNode.STATUS_COMPLETED, self.parents))

    def __str__(self):
        return self.name or super(RequestGraphNode, self).__str__()


class RequestGraph(object):
    def __init__(self, requests):
        self.nodes = [RequestGraphNode(request) for request in requests]
        self._named_requests = {
            node.request['name']: node
            for node in filter(lambda n: n.request.get('name'), self.nodes)
        }

        for node in self.nodes:
            parents = node.request.get('depends_on', [])

            for parent_name in parents:
                parent = self._named_requests.get(parent_name)
                if not parent:
                    raise Exception('Wrong parent {} in node.'.format(parent_name))

                node.parents.add(parent)
                parent.children_set.add(node)

    def get_node_order(self, node):
        return self.nodes.index(node)

    def get_not_failed_nodes(self):
        return filter(
            lambda node: node.status not in [
                RequestGraphNode.STATUS_FAILED,
                RequestGraphNode.STATUS_FAILED_PARENT
            ],
            self.nodes
        )

    def get_current_available_nodes(self):
        return filter(lambda node: node.can_be_performed, self.get_not_failed_nodes())

    def is_completed(self):
        return all(map(
            lambda node: node.status in [
                RequestGraphNode.STATUS_FAILED,
                RequestGraphNode.STATUS_FAILED_PARENT,
                RequestGraphNode.STATUS_COMPLETED
            ],
            self.nodes
        ))
