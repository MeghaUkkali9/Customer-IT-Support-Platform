class EmailAlreadyRegisteredException(Exception):
    """Email is already registered"""

class InvalidCredentialsException(Exception):
    """Wrong email or password"""
