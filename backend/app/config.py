import os


class Settings:
    def __init__(self) -> None:
        # Defaults are dev-friendly; override via environment
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
        # Example: postgresql+psycopg://user:pass@localhost:5432/reports_db
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:postgres@localhost:5432/reports_db",
        )
