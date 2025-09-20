from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = "sqlite:///./whatsapp_bot.db"

    # OpenAI
    OPENAI_API_KEY: str

    # Flow
    FLOW_API_KEY: str
    FLOW_SECRET_KEY: str
    FLOW_BASE_URL: str = "https://sandbox.flow.cl/api"
    
    # URLs de producción
    BASE_URL: str = "http://127.0.0.1:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Evita errores si hay variables no definidas

settings = Settings()
