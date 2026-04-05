import io
import os
import sys
import smtplib
from email.message import EmailMessage
import matplotlib.pyplot as plt
from fpdf import FPDF

from sqlalchemy import create_engine, text
from datetime import datetime, timezone



def get_timestampz():
    now_utc = datetime.now(timezone.utc)
    postgres_format = now_utc.isoformat(sep=' ')
    return postgres_format



class SpeedtestReport(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_report(month_year: str, isps: list, stats: dict, bad_tests: list, ips: dict, servers: dict) -> str:
    pdf = SpeedtestReport()
    pdf.add_page()

    pdf.set_font("helvetica", "", 12)

    # --------------------- #
    # 1. title and subtitle #
    # --------------------- #
    pdf.set_font("helvetica", "B", 18)
    pdf.cell(0, 10, f"Internet Performance Report - {month_year}", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.set_font("helvetica", "I", 14)
    for isp_name in isps:
        pdf.cell(0, 10, f"ISP: {isp_name}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)

    # ----------- #
    # 2. overview #
    # ----------- #
    pdf.set_font("helvetica", "B", 14)
    
    col_w = 190 / 3
    
    pdf.cell(col_w, 10, "Speedtests", align="C")
    pdf.cell(col_w, 10, "Average Speed", align="C")
    pdf.cell(col_w, 10, "Average Ping", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(col_w, 10, f"Total: {stats['total']}", align="C")
    pdf.cell(col_w, 10, f"Download: {stats['avg_down']:.2f} Mbps", align="C")
    pdf.cell(col_w, 10, f"{stats['avg_ping']:.3f} ms", new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("helvetica", "", 12)
    pdf.cell(col_w, 10, f"Successful: {stats['successful']}", align="C")
    pdf.cell(col_w, 10, f"Upload: {stats['avg_up']:.1f} Mbps", align="C")
    pdf.cell(col_w, 10, f"", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)

    # ------------ #
    # 3. pie chart #
    # ------------ #
    
    fixed_fig_size = (4, 5)

    fig1, ax1 = plt.subplots(figsize=fixed_fig_size)
    ax1.pie(ips.values(), labels=None, autopct=None, startangle=90, radius=1)
    ax1.set_title("Client's IP Addresses")
    ax1.legend(ips.keys(), title="Adresy IP", loc="upper center", bbox_to_anchor=(0.5, -0.05))
    
    fig1.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.35)
    
    buf1 = io.BytesIO()
    fig1.savefig(buf1, format="png")
    buf1.seek(0)
    plt.close(fig1)
    
    fig2, ax2 = plt.subplots(figsize=fixed_fig_size)
    ax2.pie(servers.values(), labels=None, autopct=None, startangle=90, radius=1)
    ax2.set_title("Speedtest Servers")
    ax2.legend(servers.keys(), title="Serwery", loc="upper center", bbox_to_anchor=(0.5, -0.05))
    
    fig2.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.35)
    
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format="png")
    buf2.seek(0)
    plt.close(fig2)
    
    current_y = pdf.get_y()
    
    pdf.image(buf1, x=10, y=current_y, w=90)
    pdf.image(buf2, x=105, y=current_y, w=90)
    
    pdf.set_y(current_y + 125)

    # -------------------------------------- #
    # 4. Table of contract violation records #
    # -------------------------------------- #
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Speedtest results not fulfiling contract requirements", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    
    with pdf.table(text_align="CENTER") as table:
        header = table.row()
        for col_name in ["Date", "Download (Mbps)", "Upload (Mbps)", "Ping (ms)"]:
            header.cell(col_name)
        
        for test in bad_tests:
            row = table.row()
            row.cell(test['date'])
            row.cell(str(test['down']))
            row.cell(str(test['up']))
            row.cell(str(test['ping']))

    # ------------------------ #
    # 5. saving raport to file #
    # ------------------------ #
    reports_dir = "reports"
    
    os.makedirs(reports_dir, exist_ok=True)
    
    output_filename = f"report_{month_year.replace(' ', '_')}.pdf"
    file_path = os.path.join(reports_dir, output_filename)
    pdf.output(file_path)

    return file_path



def get_speedtest_values(db_url: str, cur_year: int, cur_month: int) -> dict:
    engine = create_engine(db_url)

    with engine.begin() as conn:
        # select: getting speedtest count
        query_stats = text("""
            SELECT 
                count(*) AS total,
                count(*) FILTER (WHERE is_successful = TRUE) AS successful,
                COALESCE(AVG(download_speed), 0) AS avg_down,
                COALESCE(AVG(upload_speed), 0) AS avg_up,
                COALESCE(AVG(ping), 0) AS avg_ping
            FROM speedtests
            WHERE EXTRACT(YEAR FROM start_time) = :year 
              AND EXTRACT(MONTH FROM start_time) = :month; 
        """)
        row_stats = conn.execute(query_stats, {"year": cur_year, "month": cur_month}).fetchone()
        stats_dict = {
            "total": row_stats.total if row_stats else 0,
            "successful": row_stats.successful if row_stats else 0,
            "avg_down": float(row_stats.avg_down) if row_stats else 0.0,
            "avg_up": float(row_stats.avg_up) if row_stats else 0.0,
            "avg_ping": float(row_stats.avg_ping) if row_stats else 0.0
        }
        
        # select: getting all client's IP addresses
        query_ips = text("""
            SELECT client_ip, count(client_ip) as ip_count
            FROM speedtests
            WHERE EXTRACT(YEAR FROM start_time) = :year 
              AND EXTRACT(MONTH FROM start_time) = :month
            GROUP BY client_ip
        """)
        result_ips = conn.execute(query_ips, {"year": cur_year, "month": cur_month}).fetchall()
        ips_dict = {str(row.client_ip): row.ip_count for row in result_ips}

        # select: getting all speedtest server names
        query_servers = text("""
            SELECT ss.server_name, count(ss.id) AS server_count
            FROM speedtests AS s
            JOIN speedtest_servers AS ss
                ON s.server_id = ss.id
            WHERE EXTRACT(YEAR FROM s.start_time) = :year 
              AND EXTRACT(MONTH FROM s.start_time) = :month
            GROUP BY ss.server_name;            
        """)
        result_servers = conn.execute(query_servers, {"year": cur_year, "month": cur_month}).fetchall()
        servers_dict = {row.server_name: row.server_count for row in result_servers}

        # select: speedtests not fulfiling contract requirements
        query_bad_tests = text("""
            SELECT start_time, download_speed, upload_speed, ping
            FROM speedtests
            WHERE EXTRACT(YEAR FROM start_time) = :year 
              AND EXTRACT(MONTH FROM start_time) = :month
              AND (download_speed <= 80 OR upload_speed <= 8 OR ping >= 100)
            ORDER BY start_time DESC;
        """)
        result_bad = conn.execute(query_bad_tests, {"year": cur_year, "month": cur_month}).fetchall()
        bad_tests_list = [
            {
                "date": row.start_time.strftime("%Y-%m-%d %H:%M"), 
                "down": float(row.download_speed),
                "up": float(row.upload_speed),
                "ping": float(row.ping)
            }
            for row in result_bad
        ]

        # select: getting distinct ISPs for the given month
        query_isps = text("""
            SELECT DISTINCT i.isp_name
            FROM speedtests s
            JOIN isps i ON s.isp_id = i.id
            WHERE EXTRACT(YEAR FROM s.start_time) = :year 
              AND EXTRACT(MONTH FROM s.start_time) = :month;
        """)
        result_isps = conn.execute(query_isps, {"year": cur_year, "month": cur_month}).fetchall()
        isps_list = [row.isp_name for row in result_isps]

        return {
            "stats": stats_dict,
            "ips": ips_dict,
            "servers": servers_dict,
            "bad_tests": bad_tests_list,
            "isps": isps_list
        }



def send_report_email(pdf_path: str, recipient_emails: list):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_APP_PASSWD")

    if not all([smtp_host, smtp_user, smtp_pass]):
        raise ValueError("Missing SMTP environmental variables!")

    msg = EmailMessage()
    msg['Subject'] = f"Speedtest Report - {os.path.basename(pdf_path)}"
    msg['From'] = smtp_user
    msg['To'] = ", ".join(recipient_emails)

    msg.set_content(
        "Hey!\n\n"
        "Here's your monthly Internet performance report - find it in attachement!\n\n"
        "Best regards, your server <3"
    )

    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
        pdf_name = os.path.basename(pdf_path)

    msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=pdf_name)
    
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)



if __name__ == "__main__":
    print(f"[*] {get_timestampz()}: Starting reporting using Ofelia...")

    now = datetime.now()
    if now.month == 1:
        report_month = 12
        report_year = now.year - 1
    else:
        report_month = now.month - 1
        report_year = now.year


    # module 1: getting database connection string from environmental variables
    try:
        print(f"[*] {get_timestampz()}: Getting environmental variables...")
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
        else:
            user = os.getenv("POSTGRES_USER")
            password = os.getenv("POSTGRES_PASSWORD")
            db_name = os.getenv("POSTGRES_DB")

            if not all([user, password, db_name]):
                raise ValueError("Not all environmental variables set!")

            db_url = f"postgresql://{user}:{password}@speedtest-db:5432/{db_name}?sslmode=disable"
    
    except Exception as e:
        print(f"[!] {get_timestampz()}: Environmental variables error: {e}")
        sys.exit(1)

    
    # module 2: getting values from database
    try:
        print(f"[*] {get_timestampz()}: Getting speedtest values from database...")
        
        values_dict = get_speedtest_values(db_url, report_year, report_month)

    except Exception as e:
        print(f"[!] {get_timestampz()}: Database error: {e}")
        sys.exit(1)


    # module 3: generating PDF report
    try:
        print(f"[*] {get_timestampz()}: Generating PDF report...")

        months = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

        report_path = generate_report(
            month_year=f"{months[report_month]} {report_year}",
            isps=values_dict["isps"],
            stats=values_dict["stats"],
            bad_tests=values_dict["bad_tests"],
            ips=values_dict["ips"],
            servers=values_dict["servers"]
        )
        
    except Exception as e:
        print(f"[!] {get_timestampz()}: Error during PDF generation: {e}")
        sys.exit(1)


    print(f"[+] {get_timestampz()}: PDF generated successfuly!")


    # module 4: sending report via SMTP
    try:
        print(f"[*] {get_timestampz()}: Sending PDF via SMTP...")
        
        recipient_str = os.getenv("REPORT_RECIPIENT")
        recipient_list = [email.strip() for email in recipient_str.split(',') if email.strip()]

        send_report_email(report_path, recipient_list)
        
        print(f"[+] {get_timestampz()}: Report successfully sent to {len(recipient_list)} recipients!")
        
    except Exception as e:
        print(f"[!] {get_timestampz()}: Error during sending report via SMTP: {e}")
        sys.exit(1)
        

