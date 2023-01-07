class MixException(Exception):
    """A generic mixing exception occured"""

    pass


class AssignmentException(MixException):
    """The mix assigment is invalid"""

    pass


class ChannelException(MixException):
    """The mix channel does not exist"""

    pass


class ValueException(MixException):
    """The value is outside the mix parameters"""

    pass
