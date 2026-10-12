from fastapi import FastAPI

from router.admins import router as admin_router
from router.students import router as student_router

app = FastAPI(title="Student Management System")

app.include_router(admin_router)
app.include_router(student_router)

@app.get("/")
async def home():
    return {"message": "Management System"}
