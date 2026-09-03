from pydantic_settings import BaseSettings, SettingsConfigDict

class GlobalSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")

    # MongoDB Config
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "Mova"

    # Redis Config
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # Temporal Config
    TEMPORAL_HOST: str = "localhost:7233"
    TEMPORAL_NAMESPACE: str = "default"

    # C++ gRPC Engine Config
    CPP_ENGINE_HOST: str = "localhost"
    CPP_ENGINE_PORT: int = 50051

    # Qdrant Config
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""

    # Cloudinary Config
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Stripe Config
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # LLMs Config
    OPENAI_API_KEY: str = ""
    COHERE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # App Config
    ENVIRONMENT: str = "local"
    AUTH_JWT_SECRET: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    AUTH_JWT_ALG: str = "HS256"
    AUTH_JWT_EXP_MINUTES: int = 60

    # New Auth Settings
    JWT_SECRET: str = ""
    JWT_REFRESH_SECRET: str = ""
    GOOGLE_CLIENT_ID: str = ""

    # SMTP Config
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_SENDER: str = ""

settings = GlobalSettings()
