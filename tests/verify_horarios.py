import requests
import datetime
import random
import string

BASE_URL = "http://localhost:5000/api"

def get_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_random_dni():
    return ''.join(random.choices(string.digits, k=8))

def test_horarios():
    print("--- Starting Verification ---")
    
    # 1. Create Doctor
    doctor_dni = get_random_dni()
    doctor_password = "password123"
    doctor_data = {
        "dni": doctor_dni,
        "password": doctor_password,
        "rol_id": 2, # Assuming 2 is medico, as DB expects integer
        "username": f"Dr.{get_random_string(5)}"
    }
    print(f"Creating Doctor: {doctor_data['username']} ({doctor_dni})")
    res = requests.post(f"{BASE_URL}/auth/create", json=doctor_data)
    if res.status_code != 201:
        print(f"Error creating doctor: {res.text}")
        return
    doctor_id = res.json().get("id") # Assuming create returns ID, if not we need to login to get it or assume it worked.
    # Wait, UsuarioController.crear_usuario might not return ID. Let's check.
    # If not, we login.

    # 2. Login to get token
    print("Logging in...")
    login_data = {"dni": doctor_dni, "password": doctor_password}
    res = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if res.status_code != 200:
        print(f"Error logging in: {res.text}")
        return
    
    token = res.json().get("access_token")
    user_data = res.json().get("usuario")
    doctor_id = user_data.get("id")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Logged in. Doctor ID: {doctor_id}")

    # 3. Create Area
    timestamp = int(datetime.datetime.now().timestamp())
    area_name = f"Area {get_random_string(5)} {timestamp}"
    print(f"Creating Area: {area_name}")
    area_data = {"nombre": area_name, "descripcion": "Test Area"}
    # Area creation might not require token if not protected, but let's see. 
    # area_routes.py doesn't seem to have @token_required on create_area? 
    # Wait, let me check area_routes.py again. 
    # It imports token_required but doesn't seem to use it on create_area in the snippet I saw?
    # Actually, I should check if it's protected. If not, I can just call it.
    # Flask usually handles it if strict_slashes is not set or set to False.
    # Let's try without trailing slash.
    res = requests.post(f"{BASE_URL}/areas/", json=area_data)
    print(f"First attempt status: {res.status_code}")
    if res.status_code != 201:
        print(f"First attempt failed: {res.text}")
        # Maybe it requires token?
        res = requests.post(f"{BASE_URL}/areas/", json=area_data, headers=headers)
        print(f"Second attempt status: {res.status_code}")
        if res.status_code != 201:
            print(f"Error creating area: {res.text}")
            return
    
    area_id = res.json().get("data").get("id")
    print(f"Area created. ID: {area_id}")

    # 4. Create Schedule for TODAY
    today = datetime.datetime.now()
    dia_semana = today.weekday()
    print(f"Creating Schedule for Day {dia_semana} (Today)")
    
    horario_data = {
        "medico_id": doctor_id,
        "area_id": area_id,
        "dia_semana": dia_semana,
        "hora_inicio": "00:00", # All day for simplicity
        "hora_fin": "23:59",
        "cupos": 1 # Only 1 slot to test limit
    }
    res = requests.post(f"{BASE_URL}/horarios/", json=horario_data, headers=headers)
    if res.status_code not in [200, 201]:
        print(f"Error creating schedule: {res.text}")
        return
    print("Schedule created.")

    # 5. Register Patient and Appointment (Success)
    print("Registering Patient 1 (Should Success)")
    patient_dni = get_random_dni()
    patient_data = {
        "dni": patient_dni,
        "nombres": "Test",
        "apellido_paterno": "Patient",
        "apellido_materno": "One",
        "fecha_nacimiento": "1990-01-01",
        "sexo": "M",
        "estado_civil": "S",
        "direccion": "Test Address",
        "sintomas": "Headache",
        "doctor_asignado_id": doctor_id,
        "area_atencion": area_name # The controller expects 'area' string, not ID? 
        # In Cita model: area = db.Column(db.String(100), nullable=False)
        # In PacienteController: area=data.get("area_atencion")
        # So yes, it expects the name.
    }
    
    res = requests.post(f"{BASE_URL}/pacientes/", json=patient_data)
    if res.status_code != 201:
        print(f"Error registering patient 1: {res.text}")
        return
    print("Patient 1 registered successfully.")

    # 6. Register Patient 2 (Should Fail due to cupos)
    print("Registering Patient 2 (Should Fail due to cupos)")
    patient2_dni = get_random_dni()
    patient2_data = patient_data.copy()
    patient2_data["dni"] = patient2_dni
    
    res = requests.post(f"{BASE_URL}/pacientes/", json=patient2_data)
    if res.status_code == 400 and "cupos" in res.text:
        print("Success: Registration failed as expected due to cupos limit.")
    else:
        print(f"Failure: Expected 400 error, got {res.status_code} - {res.text}")

if __name__ == "__main__":
    test_horarios()
