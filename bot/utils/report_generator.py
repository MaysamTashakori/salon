import pandas as pd
from fpdf import FPDF
from ..database.models import Appointment, User, Service
from .date_helper import get_persian_date
import jdatetime

class ReportGenerator:
    @staticmethod
    def generate_excel(start_date=None, end_date=None, report_type='appointments'):
        if report_type == 'appointments':
            data = Appointment.get_report_data(start_date, end_date)
            df = pd.DataFrame(data, columns=[
                'تاریخ', 'ساعت', 'نام مشتری', 'شماره تماس', 
                'خدمت', 'قیمت', 'وضعیت پرداخت'
            ])
            filename = f'reports/appointments_{jdatetime.datetime.now().strftime("%Y%m%d")}.xlsx'
            df.to_excel(filename, index=False)
            return filename

    @staticmethod
    def generate_pdf(start_date=None, end_date=None, report_type='appointments'):
        pdf = FPDF()
        pdf.add_font('Iran', '', 'static/fonts/IRANSans.ttf', uni=True)
        pdf.set_font('Iran', '', 12)
        
        if report_type == 'appointments':
            data = Appointment.get_report_data(start_date, end_date)
            pdf.add_page()
            pdf.cell(200, 10, 'گزارش نوبت‌ها', ln=True, align='C')
            
            for item in data:
                pdf.cell(200, 10, f'تاریخ: {item[0]}', ln=True)
                pdf.cell(200, 10, f'مشتری: {item[2]}', ln=True)
                pdf.cell(200, 10, f'خدمت: {item[4]}', ln=True)
                pdf.cell(200, 10, '─' * 50, ln=True)
            
            filename = f'reports/appointments_{jdatetime.datetime.now().strftime("%Y%m%d")}.pdf'
            pdf.output(filename)
            return filename
