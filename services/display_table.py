from typing import Any, List, Dict
from tabulate import tabulate
from services.models import Database

# Fungsi ini digunakan untuk mendapatkan semua data dari tabel.
def get_all_from_table(table_name: str) -> List[Dict[str, Any]]:
    conn = Database.get_connection()
    c = conn.cursor()
    c.execute(f'SELECT * FROM {table_name}')
    rows = c.fetchall()

    columns = [description[0] for description in c.description]
    return [{columns[i]: row[i] for i in range(len(row))} for row in rows]

# Fungsi ini digunakan untuk menampilkan data yang diambil secara tabular.
def display_table(table_name: str):
    data = get_all_from_table(table_name)
    if data:
        print(f"\nData from {table_name}")
        print(tabulate(data, headers="keys", tablefmt="grid"))
    else:
        print(f"\nNo data found in {table_name}")

if __name__ == "__main__":
    tables = ["members", "attendance_log", "payment_log"]
    for table in tables:
        display_table(table)
