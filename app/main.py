import os
import sys
from datetime import datetime
import random
import traceback
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import jwt

from app.db import CONN, CURS, DB
from app.schemas import UserBaseSchema


app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="sign_in")


def generate_token(user_email: str) -> dict:
    """Generate access token for user"""
    return jwt.encode(
        {"user_email": user_email},
        os.environ["JWT_SECRET"],
        algorithm="HS256",
    )


def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            os.environ["JWT_SECRET"],
            algorithms="HS256",
        )
        user_email: str = payload.get("user_email")
        if user_email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    DB(f"SELECT count(*) FROM public.\"user\" WHERE email='{user_email}';")
    if CURS.fetchone()[0] == 0:
        raise credentials_exception
    return user_email


@app.get("/sign_up", response_class=HTMLResponse)
def sign_up(request: Request):
    """Display sign up form"""
    return templates.TemplateResponse("sign_up.html", {"request": request})


@app.post("/sign_up")
def sign_up(
    request: Request, user_email: str = Form(), password: str = Form(min_length=3)
):
    """Check if user exists and is already valid
    If not, create user, auth, write digit code in console and redirect to code_verification
    """

    # Check if email validated does not already exists in db
    DB(
        f"SELECT COUNT(*) FROM public.\"user\" WHERE email='{user_email}' and is_valid=true;"
    )

    # New user
    if CURS.fetchone()[0] == 0:
        try:
            # Update or create user
            DB(
                f"""INSERT INTO public.\"user\" (email, password, created_at)
                VALUES('{user_email}', '{password}', '{datetime.now()}')
                ON CONFLICT (email) DO UPDATE SET password = EXCLUDED.password RETURNING id;"""
            )
            user_id = CURS.fetchone()[0]

            # Create digit and print it in console
            number = random.randint(1000, 9999)
            DB(
                f"INSERT INTO public.\"2fa_code\" (code, user_id, created_at) VALUES({number}, '{user_id}', '{datetime.now()}')"
            )
            print(f"Here is your digit : {number}")

            CONN.commit()
            token = generate_token(user_email)
            response = RedirectResponse("/code_verification", status_code=302)
            response.set_cookie(key="access-token", value=token, httponly=True)
            return response

        except Exception as e:
            tb = traceback.format_exc()
            return templates.TemplateResponse(
                "sign_up.html",
                {"request": request, "user_email_error": e.with_traceback(tb)},
            )

    #  User already created and valid
    else:
        return templates.TemplateResponse(
            "sign_up.html",
            {"request": request, "user_email_error": "user already created"},
        )


@app.get("/code_verification", response_class=HTMLResponse)
def code_verification(request: Request):
    """Display code digit form"""
    jwt_token = request.cookies.get("access-token")

    if get_current_user(jwt_token):
        return templates.TemplateResponse(
            "code_verification.html", {"request": request}
        )
    raise HTTPException(status_code=400, detail="Inactive user")


@app.post("/code_verification")
def code_verification(request: Request, code_digit: int = Form()):
    """Check if digit code is correct and valid
    Update is_valid for current user
    """
    jwt_token = request.cookies.get("access-token")

    user_email = get_current_user(jwt_token)

    if user_email:
        # Check if code is active
        DB(
            f"""SELECT code_table.created_at, user_id FROM public.\"2fa_code\" AS code_table 
            JOIN public.\"user\" AS user_table ON user_table.id = code_table.user_id
            WHERE user_table.email = '{user_email}' ORDER BY code_table.created_at DESC"""
        )
        db_result = CURS.fetchall()[0]
        last_code_date = db_result[0]
        user_id = db_result[1]
        minutes_diff = (datetime.now() - last_code_date).total_seconds() / 60.0

        if minutes_diff > 1:
            # Generate another code
            number = random.randint(1000, 9999)
            DB(
                f"INSERT INTO public.\"2fa_code\" (code, user_id, created_at) VALUES({number}, '{user_id}', '{datetime.now()}')"
            )
            print(f"Here is your digit : {number}")
            return templates.TemplateResponse(
                "code_verification.html",
                {
                    "request": request,
                    "error": "Expired code, check the new code in console",
                },
            )

        # Check if code is correct
        DB(
            f"""SELECT count(*) FROM public.\"2fa_code\" AS code_table 
            JOIN public.\"user\" AS user_table ON user_table.id = code_table.user_id
            WHERE user_table.email = '{user_email}' AND code_table.code={code_digit}"""
        )
        if CURS.fetchone()[0] == 0:
            return templates.TemplateResponse(
                "code_verification.html", {"request": request, "error": "Invalid code"}
            )

        # Update user.is_valid = true
        DB(f"UPDATE public.\"user\" SET is_valid = true WHERE id = '{user_id}';")
        CONN.commit()
        return templates.TemplateResponse(
            "code_verification.html", {"request": request, "message": "Email validated"}
        )

    raise HTTPException(status_code=400, detail="Inactive user")
