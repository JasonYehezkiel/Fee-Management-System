import inspect
import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import uuid
from .config import Config
from .logger_setup import LoggerSetup

models_logger = LoggerSetup.setup_logger('models', 'models.log')

class Database:

    first_connection = True

    @staticmethod
    def get_connection():
        # Membuat koneksi dengan database SQLite
        try:
            conn = sqlite3.connect(Config.DB_PATH)
            conn.row_factory = sqlite3.Row

            if Database.first_connection:
                models_logger.debug('Database connection established.')
                Database.first_connection = False
                
            return conn
        except sqlite3.Error as e:
            models_logger.error(f"Database connection error: {e}")
            raise

    @staticmethod
    def init_db():
        # Menginisialisasikan database dengan membuat tabel yang diperlukan
        if os.path.exists(Config.DB_PATH):
            return
        
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.executescript('''
                CREATE TABLE IF NOT EXISTS members (
                    member_code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    transport TEXT NOT NULL,
                    fee INTEGER NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS attendance_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_code TEXT NOT NULL,
                    visit_number INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (member_code) REFERENCES members (member_code)
                );
                
                CREATE TABLE IF NOT EXISTS payment_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_code TEXT NOT NULL,
                    payment_due INTEGER NOT NULL,
                    paid BOOLEAN DEFAULT FALSE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_code) REFERENCES members (member_code)
                );
            ''')
            conn.commit()
            models_logger.debug("Database initialized succesfully.")
        except sqlite3.Error as e:
            models_logger.error(f"Error initializing database: {e}")
        finally:
            conn.close()


class Member:
    def __init__(self, member_code: str, name: str, transport: str, fee: int):
        # Insisalisasi objek Member
        self.member_code = member_code
        self.name = name
        self.transport = transport
        self.fee = fee

    @staticmethod
    def create(name: str, transport: str) -> 'Member':
        # Membuat anggota baru dan menyimpannya ke database
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            member_code = f"MEM-{uuid.uuid4().hex[:6].upper()}" # Digunakan untuk menghasilkan kode anggota unik
            fee = Config.FEES[transport]
            c.execute('''
                INSERT INTO members (member_code, name, transport, fee)
                VALUES (?, ?, ?, ?)
            ''', (member_code, name, transport, fee))
            conn.commit()
            models_logger.info(f"New member created: {name} with member code: {member_code}")
            return Member(member_code, name, transport, fee)
        except sqlite3.Error as e:
            models_logger.error(f"Error creating member: {e}")
            raise
        finally:
            conn.close()
    

    @staticmethod
    def get_by_code(member_code: str) -> Optional['Member']:
        # Mendapatkan informasi anggota menggunakan kode anggota.
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.execute('SELECT * FROM members WHERE member_code = ?', (member_code,))
            row = c.fetchone()
            if row:
                models_logger.info(f"Member found: {row['name']} with member code: {member_code}")
                return Member(
                    row['member_code'],
                    row['name'],
                    row['transport'],
                    row['fee']
                )
            else:
                models_logger.warning(f"Member not found for code: {member_code}")
                return None
        except sqlite3.Error as e:
            models_logger.error(f"Error retrieving member by code {member_code}: {e}")
            raise
        finally:
            conn.close()
            


class AttendanceLog:
    # Inisialisasi objek Catatan Kehadiran
    def __init__(self, member_code: str, timestamp: datetime, visit_number: int, id: Optional[int] = None):
        self.id = id
        self.member_code = member_code
        self.timestamp = timestamp
        self.visit_number = visit_number

    @staticmethod
    def get_last_attendance(member_code: str, supress_logs: bool = False) -> Optional['AttendanceLog']:
        # Digunakan untuk mendapatkan catatan kehadiran terakhir anggota tertentu
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.execute('''
                SELECT * FROM attendance_log 
                WHERE member_code = ? 
                ORDER BY timestamp DESC LIMIT 1
            ''', (member_code,))
            row = c.fetchone()
            if row:
                if not supress_logs:
                    models_logger.info(f"Attendance found for member code: {member_code}")
                return AttendanceLog(
                    row['member_code'],
                    datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S'),
                    row['visit_number'],
                    row['id']
                )
            return None
        
        except sqlite3.Error as e:
            models_logger.error(f"Error retrieving attendance for code {member_code}: {e}")
            raise
        finally:
            conn.close()
    

    @staticmethod
    # Membuat catatan kehadiran baru
    def create(member_code: str, visit_number: int) -> 'AttendanceLog':
        try:
            now = datetime.now()
            conn = Database.get_connection()
            c = conn.cursor()
            
            last_attendance = AttendanceLog.get_last_attendance(member_code, supress_logs=True)
            
            if last_attendance:
                c.execute('''
                    UPDATE attendance_log 
                    SET timestamp = ?, visit_number = ?
                    WHERE id = ?
                ''', (now.strftime('%Y-%m-%d %H:%M:%S'), visit_number, last_attendance.id))
                models_logger.info(f"Attendance updated for member code: {member_code} with visit number: {visit_number}")
            else:
                c.execute('''
                    INSERT INTO attendance_log (member_code, timestamp, visit_number)
                    VALUES (?, ?, ?)
                ''', (member_code, now.strftime('%Y-%m-%d %H:%M:%S'), visit_number))
                models_logger.info(f"New attendance created for member code: {member_code}")
            
            conn.commit()
            return AttendanceLog(member_code, now, visit_number)
        except sqlite3.Error as e:
            models_logger.error(f"Error creating attendance for {member_code}: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_all() -> List[Dict]:
        # Mendapatkan semua catatan kehadiran untuk ditampilkan
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.execute('''
                SELECT 
                    attendance_log.member_code,
                    members.name,
                    attendance_log.visit_number
                FROM attendance_log
                JOIN members ON attendance_log.member_code = members.member_code
                ORDER BY attendance_log.timestamp DESC
            ''')
            result = [{
                'memberCode': row[0],
                'member': row[1],
                'visitNumber': row[2]
            } for row in c.fetchall()]
            models_logger.info(f"Retrieved all attendance records. Total records: {len(result)}")
            return result
        except sqlite3.Error as e:
            models_logger.error(f"Error retrieving attendance records: {e}")
            raise
        finally:
            conn.close()


    def reset_visit_number(self, new_count: int) -> None:
        # Mengatur ulang visit_number anggota tertentu
        try:
            conn= Database.get_connection()
            c = conn.cursor()
            c.execute('''
                UPDATE attendance_log 
                SET visit_number = ? 
                WHERE member_code = ?
            ''', (new_count, self.member_code))
            conn.commit()
            self.visit_number = new_count
            models_logger.info(f"Visit number reset for member code: {self.member_code} to {new_count}")
        except sqlite3.Error as e:
            models_logger.error(f"Error resetting visit number for {self.member_code}: {e}")
            raise
        finally:
            conn.close()


class PaymentLog:
    # Inisialisasi objek Catatan Pembayaran
    def __init__(self, member_code: str, payment_due: int, timestamp: datetime, paid: bool = False, id: Optional[int] = None):
        self.id = id
        self.member_code = member_code
        self.payment_due = payment_due
        self.paid = paid
        self.timestamp = timestamp

    @staticmethod
    def create(member_code: str, payment_due: int) -> 'PaymentLog':
        # Membuat catatan pembayaran baru
        try:
            conn = Database.get_connection()
            now = datetime.now()
            c = conn.cursor()
            c.execute('''
                INSERT INTO payment_log (member_code, payment_due, paid, timestamp)
                VALUES (?, ?, FALSE, ?)
            ''', (member_code, payment_due, now.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            models_logger.info(f"Payment record created for member code: {member_code} with payment of {payment_due}")
            return PaymentLog(member_code, payment_due, now)
        except sqlite3.Error as e:
            models_logger.error(f"Error creating payment record for {member_code}: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_unpaid(member_code: str) -> Optional['PaymentLog']:
        # Mendapatkan iuran yang belum dibayar anggota
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.execute('''
                SELECT * FROM payment_log 
                WHERE member_code = ? AND paid = FALSE
            ''', (member_code,))
            row = c.fetchone()
            if row:
                models_logger.info(f"Unpaid payment found for member {member_code} with payment of {row['payment_due']}")
                return PaymentLog(
                    row['member_code'],
                    row['payment_due'],
                    row['timestamp'],
                    row['paid'],
                    row['id']
                )
    
            return None
        
        except sqlite3.Error as e:
            models_logger.error(f"Error fetching unpaid payment for member {member_code}: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_all() -> List[Dict]:
        # Digunakan untuk menampilkan iuran yang belum dibayar
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.execute('''
                SELECT 
                    payment_log.member_code,
                    members.name,
                    payment_log.payment_due,
                    payment_log.paid
                FROM payment_log
                JOIN members ON payment_log.member_code = members.member_code
                ORDER BY payment_log.timestamp DESC
            ''')
            result = [{
                'memberCode': row[0],
                'member': row[1],
                'amount': row[2],
                'paid': row[3]
            } for row in c.fetchall()]
            models_logger.info(f"Fetched all payment records. Total records: {len(result)}")
            return result
        except sqlite3.Error as e:
            models_logger.error(f"Error retrieving payment records: {e}")
            raise
        finally:
            conn.close()


    def mark_as_paid(self) -> None:
        # Digunakan untuk menandakan iuran telah terbayar
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.execute('''
                UPDATE payment_log 
                SET paid = TRUE 
                WHERE member_code = ? AND paid = FALSE
            ''', (self.member_code,))
            conn.commit()
            self.paid = True
            models_logger.info(f"Payment marked as paid for member {self.member_code}")
        except sqlite3.Error as e:
            models_logger.error(f"Error marking payment as paid for member {self.member_code}: {e}")
            raise
        finally:
            conn.close()