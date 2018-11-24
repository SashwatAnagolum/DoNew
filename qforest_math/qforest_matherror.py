# -*- coding: utf-8 -*-

"""
exceptions.py: Holds all the custom errors defined as part of 
QForestMath.
"""

class QForestMathError(Exception):
    """
    Base class for errors raised by the QForestMath library.

    """
    def __init__(self, *message):
        """Set the error message."""
        super().__init__(' '.join(message))
        self.message = ' '.join(message)

    def __str__(self):
        """Return the message."""
        return repr(self.message)

class RegisterError(QForestMathError):
    """
    Error class for register index and length related errors. 
    Derived from the QForestMathError class.

    """
    def __init__(self, *message):
        """Set the error message."""
        super().__init__(' '.join(message))
        self.message = ' '.join(message)

    def __str__(self):
        """Return the message."""
        return repr(self.message)

class ZeroError(QForestMathError):
    """
    Error class for division by zero errors. 
    Derived from the QForestMathError class.

    """
    def __init__(self, *message):
        """Set the error message."""
        super().__init__(' '.join(message))
        self.message = ' '.join(message)

    def __str__(self):
        """Return the message."""
        return repr(self.message)


 