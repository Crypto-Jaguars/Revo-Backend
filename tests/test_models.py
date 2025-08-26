"""
Test models for SQLite compatibility.
"""

# Note: TestUser model removed to avoid conflicts with actual User model
# The actual User model uses UUID which is not supported in SQLite
# Tests should use the actual models with proper database setup 