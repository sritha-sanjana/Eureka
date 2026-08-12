import os

class Settings:
    PROJECT_NAME: str = "EUREKA! Pitching Platform"
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./eureka.db")
    
    # JWT Security Settings
    # In production, this should be a random secure string
    SECRET_KEY: str = os.getenv("SECRET_KEY", "7b049d5c317db698be906ba07c08a9f6d7eb593361df4fe7a68a52ee24a1b021")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day session
    
    # Admin Credentials
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    # For simplicity of deployment, we set the default plain password here, and we'll hash it
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "EurekaAdmin2026")
    
    # Storage settings
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "uploads")

settings = Settings()
