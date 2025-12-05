from flask import Blueprint, request
from controllers.area_controller import AreaController

area_bp = Blueprint("area_bp", __name__)

@area_bp.get("/")
def get_areas():
    return AreaController.get_all()

@area_bp.post("/")
def create_area():
    data = request.get_json()
    return AreaController.create(data)

@area_bp.put("/<int:id>")
def update_area(id):
    data = request.get_json()
    return AreaController.update(id, data)

@area_bp.delete("/<int:id>")
def delete_area(id):
    return AreaController.delete(id)
