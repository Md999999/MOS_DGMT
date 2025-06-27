from fastapi import FastAPI
from app import auth, routes

app = FastAPI(
    title="SOS Alert System",
    description="Backend for emergency contacts and alerts",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(routes.router)


#--------------------------- instructions to run this project ---------------------------------------

# in project root directory, run:  not in app directory
# python -m venv myenv
# .\myenv\Scripts\Activate
# pip install python-multipart
# pip install fastapi uvicorn 'passlib[bcrypt]' python-jose pydantic
# uvicorn main:app --reload