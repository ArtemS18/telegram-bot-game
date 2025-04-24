from fastapi import FastAPI
from app.admin.view import AdminView



def setup_admin_routes(app: FastAPI):
    admin_view = AdminView(app)
    app.include_router(admin_view.get_router())