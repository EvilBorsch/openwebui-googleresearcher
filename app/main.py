from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .routers import research
from .config import settings

app = FastAPI(title="AI Researcher Tool Server", version="0.1.0")

security = HTTPBearer(auto_error=False)


def verify_bearer_token(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    if settings.api_token:
        if not credentials or not credentials.scheme.lower() == "bearer" or credentials.credentials != settings.api_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    return True

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply auth dependency to all routes in the research router
app.dependency_overrides = {}

app.include_router(research.router, tags=["research"], dependencies=[Depends(verify_bearer_token)])
