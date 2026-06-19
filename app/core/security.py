import os
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader


#************************
#* Chargement config    *
#************************

load_dotenv()

API_KEY_HEADER_NAME = os.getenv("API_KEY_HEADER_NAME", "X-API-Key")
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


#************************
#* Lecture configuration *
#************************

@lru_cache
def get_expected_api_key() -> str | None:
    return os.getenv("API_KEY")


#************************
#* Dependance FastAPI   *
#************************

def require_api_key(api_key: str | None = Security(api_key_header)) -> str:
    expected_api_key = get_expected_api_key()

    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key configuration missing",
        )

    if api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="L'API key manque ou est invalide",
        )

    return api_key
