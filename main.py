from fastapi import FastAPI
from app.database import Base, engine
from app.auth import router as auth_router
from app.routes import router as main_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(main_router)


#--------------------------- instructions to run this project ---------------------------------------

# in project root directory, run:  not in app directory
# python -m venv myenv
# .\myenv\Scripts\Activate
# pip install python-multipart
# pip install fastapi uvicorn 'passlib[bcrypt]' python-jose pydantic
# uvicorn main:app --reload
