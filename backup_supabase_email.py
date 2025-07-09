import csv
import smtplib
from io import StringIO
from email.message import EmailMessage
from supabase import create_client

SUPABASE_URL = "https://gapfbzmccgkoatleopgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdhcGZiem1jY2drb2F0bGVvcGd2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIwNzY2NzgsImV4cCI6MjA2NzY1MjY3OH0.fu-r_oHiGadA3f4WCO0UtOF3M59Kc1ZagtWB9SaJ7Bc"

EMAIL_ADDRESS = "basedatosvehiculos@gmail.com"
EMAIL_PASSWORD = "oxnt unyc embu fove"
EMAIL_DESTINO = "basedatosvehiculos@gmail.com"

def generar_csv():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    result = supabase.table('vehiculos').select('*').execute()
    vehiculos = result.data

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Matrícula', 'Nombre', 'Modelo'])
    for v in vehiculos:
        cw.writerow([v['id'], v['matricula'], v['nombre'], v['modelo']])
    contenido = si.getvalue()
    si.close()
    return contenido

def enviar_email(contenido_csv):
    msg = EmailMessage()
    msg['Subject'] = 'Backup Base de Datos Vehículos'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_DESTINO
    msg.set_content('Adjunto tienes el backup CSV de la base de datos.')

    msg.add_attachment(contenido_csv, maintype='text', subtype='csv', filename='vehiculos_backup.csv')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
    print("Backup enviado por email correctamente.")

if __name__ == "__main__":
    csv_data = generar_csv()
    enviar_email(csv_data)
