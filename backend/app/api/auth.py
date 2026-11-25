from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.utils.telegram_auth import validate_init_data, extract_telegram_user
from app.services.user_service import get_or_create_user
from app.utils.jwt import create_access_token
from app.schemas.schemas import AuthRequest, AuthResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram", response_model=AuthResponse)
async def auth_telegram(payload: AuthRequest, db: AsyncSession = Depends(get_db)):
    tg_user = extract_telegram_user(payload.init_data)
    if not tg_user:
        # dev fallback: try parse init_data as json user
        import json
        try:
            data = dict(__import__("urllib.parse", fromlist=["parse_qsl"]).parse_qsl(payload.init_data, keep_blank_values=True))
            if "user" in data:
                tg_user = json.loads(data["user"])
        except Exception:
            tg_user = None
    if not tg_user:
        raise HTTPException(status_code=401, detail="Invalid initData")
    user = await get_or_create_user(db, tg_user)
    await db.commit()
    token = create_access_token(str(user.telegram_id))
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))
