import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://sahil@localhost:5432/ipick_dev"
)
