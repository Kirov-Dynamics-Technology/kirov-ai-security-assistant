from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


load_dotenv()


class Settings(BaseSettings):
    app_name: str = "Kirov AI Security Assistant"
    app_version: str = "0.1.0"
    debug: bool = False
    jwt_secret: str = Field(
        default="",
        description="JWT signing secret. Set via env var KIROV_SECURITY_JWT_SECRET.",
    )
    database_url: str = Field(
        default="postgresql+asyncpg://kirov:kirov@localhost:5432/kirov_security",
    )
    redis_url: str = Field(default="redis://localhost:6379/0")
    openai_api_key: str | None = None
    log_level: str = "INFO"

    model_config = {"env_prefix": "KIROV_SECURITY_", "env_file": ".env"}

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        stripped = v.strip() if v else ""
        if (
            not stripped
            or "placeholder" in stripped.lower()
            or "change" in stripped.lower()
        ):
            raise ValueError(
                "JWT_SECRET must be set and must not be a placeholder. "
                "Set the KIROV_SECURITY_JWT_SECRET env var or add it to .env."
            )
        return stripped


settings = Settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-powered code security scanning API",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "kirov-ai-security-assistant",
        "version": settings.app_version,
    }
