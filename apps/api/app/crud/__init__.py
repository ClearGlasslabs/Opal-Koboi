"""Database persistence boundaries for the control plane.

CRUD functions never commit transactions. The request-scoped database dependency
owns commit and rollback so business services remain atomic.
"""
