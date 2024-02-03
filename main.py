from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from utils import authenticate as auth
from models import user_model as UM
import constants as CNST

app = FastAPI()


@app.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> UM.Token:
    user = auth.authenticate_user(auth.fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=CNST.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return UM.Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=UM.User)
async def read_users_me(
        current_user: Annotated[UM.User, Depends(auth.get_current_active_user)]
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
        current_user: Annotated[UM.User, Depends(auth.get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]
