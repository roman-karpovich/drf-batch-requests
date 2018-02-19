class BatchRequestException(Exception):
    pass


class RequestAttributeError(BatchRequestException):
    """ Empty request attribute. Unable to perform request.  """
