class TicketNotFoundException(Exception):
    """Ticket Not Found Error"""

class IdempotencyKeyReusedException(Exception):
    """Idempotency key was already used with a different request body"""
