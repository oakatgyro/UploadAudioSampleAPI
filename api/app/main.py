"""API main worker"""

from io import BytesIO
import subprocess
import tempfile

from fastapi import FastAPI, Depends, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from mysql.connector.connection import MySQLConnection
from routes import healthcheck
from pydub import AudioSegment
from db import get_db_connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


app.include_router(healthcheck.router, prefix="/healthcheck")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """exception handler

    Args:
        request (Request): request information
        exc (HTTPException): exception
    """
    if exc.status_code == 500:
        return JSONResponse(
            content={"description": f"Internal Server Error: {str(exc.detail)}"},
            status_code=500,
        )
    else:
        return JSONResponse(
            content={"description": exc.detail},
            status_code=exc.status_code,
        )


@app.get("/audio/user/{user_id}/phrase/{phrase_id}/{audio_format}")
async def get_audio_by_user_phrase(
    user_id: int,
    phrase_id: int,
    audio_format: str,
    db_conn: MySQLConnection = Depends(get_db_connection),
):
    """get audio by user id and phrase id with audio format.

    Args:
        user_id (int): user id
        phrase_id (int): phrase id
        audio_format (str): audio format (only m4a available)
        db_conn (MySQLConnection, optional): database connection. Defaults to Depends(get_db_connection).
    """
    if audio_format != "m4a":
        raise HTTPException(status_code=400, detail="Invalid Audio Format")

    query = "SELECT audio FROM user_phrase_audio WHERE user_id=%s AND phrase_id=%s"
    if db_conn.is_connected():
        with db_conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id, phrase_id))
            res = cursor.fetchone()
    else:
        raise HTTPException(status_code=500, detail="Database Not Connected")

    if not res:
        raise HTTPException(status_code=404, detail="Record Not Found")

    audio_data = res["audio"]

    with tempfile.NamedTemporaryFile(delete=True, dir=".", suffix=".m4a") as temp_file:
        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-i",
            "pipe:0",
            temp_file.name,
        ]
        proc = subprocess.Popen(
            ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        proc.communicate(audio_data)

        if proc.returncode != 0:
            raise HTTPException(status_code=500, detail="Convert Audio Failed")

        with open(temp_file.name, "rb") as f:
            audio_data = f.read()

        return StreamingResponse(BytesIO(audio_data), media_type="audio/x-m4a")


@app.post("/audio/user/{user_id}/phrase/{phrase_id}")
async def post_audio_by_user_and_phrase(
    user_id: int,
    phrase_id: int,
    audio_file: UploadFile,
    db_conn: MySQLConnection = Depends(get_db_connection),
):
    """post audio by user id and phrase id

    Args:
        user_id (int): user id
        phrase_id (int): phrase id
        audio_file (UploadFile): audio file (m4a format)
        db_conn (MySQLConnection, optional): database connection. Defaults to Depends(get_db_connection).
    """
    if audio_file.content_type != "audio/x-m4a":
        raise HTTPException(status_code=400, detail="Invalid audio format")

    audio_data = BytesIO(await audio_file.read())
    audio = AudioSegment.from_file(audio_data, format="m4a")

    wav_data = audio.export(format="wav").read()

    query = "INSERT INTO user_phrase_audio (user_id, phrase_id, audio) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE audio = VALUES(audio), updated_at = NOW()"
    if db_conn.is_connected():
        with db_conn.cursor() as cursor:
            cursor.execute(query, (user_id, phrase_id, wav_data))
        db_conn.commit()
    else:
        raise HTTPException(status_code=500, detail="Database Not Connected")

    return {"description": "Succeeded"}
