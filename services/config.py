import os

class Config:
    # Definisikan konfigurasi untuk base direcctory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'memberships.db')
    LOG_PATH = os.path.join(BASE_DIR, '..', 'logs')

    # Konfigurasi untuk template dan static folder
    TEMPLATE_DIR = os.path.join(BASE_DIR, '..', 'templates')
    STATIC_DIR = os.path.join(BASE_DIR, '..', 'static')

    # variabel yang dibutuhkan
    FEES = {
        'BUS': 100000,
        'TRAVEL': 50000
    }
    ATTENDANCE_LIMIT_MINUTES = 2