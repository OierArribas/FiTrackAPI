import random

import firebase_admin
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import false, true
from sqlalchemy.orm import Session
import requests
import models
from database import engine, SessionLocal
from esquemas import *
from typing import List, Annotated
from passlib.context import CryptContext
from apscheduler.schedulers.background import BackgroundScheduler
from firebase_admin import credentials, messaging

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#----------------------------------------------------------------------
#----------------------NOTIICACIONES FIREBASE--------------------------
#----------------------------------------------------------------------
#Firebase

credentials_path = "/code/service-account-file.json"
firebase_credentials = credentials.Certificate(credentials_path)
firebase_admin.initialize_app(firebase_credentials)
mensajes_notificaciones = [
    "Hola.",
    "Hola!",
    "Hola 2",
    "Hola! 2!",
    "Hola que tal!",
    "Hi!"
]
"""
print("suscribir al topico")
response = messaging.subscribe_to_topic(
    "cD7yIW2jQDOS-X6qcrl-ym:APA91bEHt9aqmG81lTnMG7K0LgTdojKUBkH50TVf3nUTx6ejhpR7nY6CIAsxgBTCEZTiQJl8NjJQheX5uicIRUeALHyXa8prjNK0nQvXxy-ubg5Yl0cxGQnokN6pMmKjFleavd4S18t1",
    "actividades"
)
print(response.success_count, 'tokens were subscribed successfully')
"""

# Función para enviar mensaje aleatorio
def enviar_mensaje_aleatorio():
    print("Enviando mensaje")
    mensaje_aleatorio = random.choice(mensajes_notificaciones)
    message = messaging.Message(
        notification=messaging.Notification(
            title="FiTrack",
            body=mensaje_aleatorio,
        ),
        topic="actividades"
    )
    try:
        response = messaging.send(message)
        print(f"Mensaje enviado: {response}")
    except Exception as e:
        print(f"Error enviando mensaje: {str(e)}")


scheduler = AsyncIOScheduler()
scheduler.add_job(
    enviar_mensaje_aleatorio,
    IntervalTrigger(seconds=3000000),  # Ejecutar cada 30 segundos
    timezone="UTC"  # Zona horaria de España
)
print("------------------AUTO NOTIFICATIONS ON-------------------")
scheduler.start()


#----------------------------------------------------------------------
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@app.post("/adduser/")
async def create_user(user: User, db: Session = Depends(get_db)):
    hashed_pwd = get_password_hash(user.hashed_password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/getuser")
async def get_user(username: str, password: str, db: Session = Depends(get_db)):
    print(username, password)
    result = db.query(models.User).filter(models.User.username == username).first()

    #result.email = zlib.decompress(result.foto).decode('utf-8')

    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password, result.hashed_password):
        raise HTTPException(status_code=404, detail="Password does not match")
    return result


@app.put("/uploadPhoto")
async def upload_photo(username: str, photo_bitmap_string: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    #user.foto = zlib.compress(photo_bitmap_string.encode('utf-8'))
    #print(user.foto)
    user.foto = photo_bitmap_string

    db.commit()
    return user


@app.get("/subscribeTopic")
async def subscribe_topic(token: str, db: Session = Depends(get_db)):
    response = messaging.subscribe_to_topic(
        token,
        "actividades"
    )
    print(token)
    print(response.success_count, 'tokens were subscribed successfully')


    if response.success_count == 0:
        db_user = models.User(username= "operation error")
    else:
        db_user = models.User(username= "operation succesfull")

    return db_user
