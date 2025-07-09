import smtplib
from email.message import EmailMessage
from datetime import datetime
import shutil
import os

EMAIL_EMISOR = os.environ.get('EMAIL_EMISOR')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECEPTOR = os.environ.get('EMAIL_RECEPTOR')

def hacer_backup():
    fecha = datetime.now().strftime('%Y-%m-%d')
    nombre_backup = f'database_backup_{fecha}.db'
    shutil.copyfile('database.db', nombre_backup)
    return nombre_backup

def enviar_correo(nombre_backup):
    msg = EmailMessage()
    msg['Subject'] = f'Backup base de datos {nombre_backup}'
    msg['From'] = EMAIL_EMISOR
    msg['To'] = EMAIL_RECEPTOR
    msg.set_content('Aquí tienes el backup diario de la base de datos.')

    with open(nombre_backup, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='octet-stream', filename=nombre_backup)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_EMISOR, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == '__main__':
    backup_file = hacer_backup()
    enviar_correo(backup_file)
