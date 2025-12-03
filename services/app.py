import logging
import os
from flask import Flask, render_template, request, jsonify 
from datetime import datetime, timedelta
from .config import Config
from .models import Database, Member, AttendanceLog, PaymentLog
from .logger_setup import LoggerSetup

# Inisialisasi Aplikasi Flask
app = Flask(__name__,
            template_folder=os.path.join(Config.TEMPLATE_DIR),
            static_folder=os.path.join(Config.STATIC_DIR))

 # Inisialisasi database
Database.init_db()

# Set up logger
app_logger = LoggerSetup.setup_logger('app', 'app.log')


@app.template_filter('format_number')
def format_number(value):
    return f"{value:,}"

@app.route('/')
def home():
    app_logger.info("Home route accessed.")
    return render_template('index.html', fees=Config.FEES)

@app.route('/api/register', methods=['POST'])
def register_member() -> str:
    try:
        name = request.form.get('name')
        transport = request.form.get('transport')

        if not name or not transport:
            app_logger.warning("Register failed: Missing name or transport type.")
            return jsonify({'error': 'Missing Name or transport type'}), 400
        
        # Membuat anggota baru
        member = Member.create(name, transport)
        app_logger.info(f"New member registered: {member.member_code}")
        return jsonify({'memberCode': member.member_code}), 201
    
    except Exception as e:
        app_logger.error(f"Error during member registration: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/attendance', methods=['POST'])
def record_attendance() -> str:
    
    try:
        code = request.form.get('code')
        now = datetime.now()

        # Periksa apakah anggota terdaftar
        member = Member.get_by_code(code)
        if not member:
            app_logger.warning("Attendance failed: Invalid member code.")
            return jsonify({'message': 'Invalid member code'}), 400
        
        # Periksa apakah ada pembayaran yang tertunda
        payment_due = PaymentLog.get_unpaid(code)
        if payment_due:
            app_logger.warning("Attendance failed: Payment required.")
            return jsonify({'message': 'Payment required before recording additional attendance'}), 400
        
        
        # Periksa waktu kehadiran yang terakhir
        last_attendance = AttendanceLog.get_last_attendance(code)
            
        # if last_attendance:
        #     time_since_last = now - last_attendance.timestamp
        #     if time_since_last < timedelta(minutes=Config.ATTENDANCE_LIMIT_MINUTES):
        #         time_left = timedelta(minutes=Config.ATTENDANCE_LIMIT_MINUTES) - time_since_last
        #         formatted_time_left = str(time_left).split('.')[0]
        #         return jsonify({
        #             'message': f'Cannot record attendance. Try again in: {formatted_time_left}'
        #         }), 400
        
        # Perbaharui attendance log, setiap kali anggota melakukan kehadiran
        new_count = (last_attendance.visit_number + 1) if last_attendance else 1
        AttendanceLog.create(code, new_count)

        # Periksa apakah anggota sudah hadir selama 5 kali
        need_payment = False
        payment_amount = 0

        if new_count % 5 == 0:
            payment_amount = member.fee * 5
            PaymentLog.create(code, payment_amount)
            need_payment = True
        
        response = {
            'message': 'Attendance Recorded', 
            'needPayment': need_payment
        }
        
        if need_payment:
            response['paymentAmount'] = payment_amount

        app_logger.info(f"Attendance recorded for member: {code}")
        return jsonify(response), 200

    except Exception as e:
        app_logger.error(f"Error during attendance recording: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance-list', methods=['GET'])
def get_attendance_list() -> str:
    try:
        data = AttendanceLog.get_all()
        app_logger.info("Attendance list retrieved.")
        return render_template('table_attendance.html', attendance_list=data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/payment-list', methods=['GET'])
def get_payment_list() -> str:
    try:
        data = PaymentLog.get_all()
        app_logger.info("Payment list retrieved.")
        return render_template('table_payment.html', payment_list=data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pay', methods=['POST'])
def pay_fee() -> str:
    try:
        code = request.form.get('code')

        payment = PaymentLog.get_unpaid(code)

        # Tandai payment as paid, ketika anggota membayar tagihannya
        payment.mark_as_paid()

        # Reset visit_number
        last_attendance = AttendanceLog.get_last_attendance(code)
        if last_attendance:
            last_attendance.reset_visit_number(0)
        
        app_logger.info(f"Payment proccessed for member: {code}")
        return jsonify({'message':  'Payment proceed successfully'})
    
    except Exception as e:
        app_logger.error(f"Error processing payment: {e}")
        return jsonify({'error': str(e)}), 500