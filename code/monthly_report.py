import io
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
        self.cell(0, 10, f"Strona {self.page_no()}", align="C")

def generate_report(month_year: str, isp_name: str, stats: dict, bad_tests: list, ips: dict, servers: dict):
    pdf = SpeedtestReport()
    pdf.add_page()

    pdf.set_font("helvetica", "", 12)

    # --------------------- #
    # 1. title and subtitle #
    # --------------------- #
    pdf.set_font("helvetica", "B", 18)
    pdf.cell(0, 10, f"Internet Performance Report - {month_year}", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.set_font("helvetica", "I", 14)
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
    pdf.cell(col_w, 10, f"Download: {stats['avg_down']:.2f} Mb/s", align="C")
    pdf.cell(col_w, 10, f"{stats['avg_ping']:.3f} ms", new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("helvetica", "", 12)
    pdf.cell(col_w, 10, f"Successful: {stats['successful']}", align="C")
    pdf.cell(col_w, 10, f"Upload: {stats['avg_up']:.1f} Mb/s", align="C")
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
    pdf.cell(0, 10, "Speedtests violating contract guaranteed speed", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    
    with pdf.table(text_align="CENTER") as table:
        header = table.row()
        for col_name in ["Date", "Download", "Upload", "Ping"]:
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
    # TODO path management, logging to dedicated dir, returning file path
    output_filename = f"raport_{month_year.replace(' ', '_')}.pdf"
    pdf.output(output_filename)
    print(f"[+] Raport generated: {output_filename}")



pass



if __name__ == "__main__":
    # Dane testowe (jak poprzednio)
    mock_stats = {
        "total": 720,
        "successful": 715,
        "avg_down": 285.5,
        "avg_up": 45.2,
        "avg_ping": 14.2
    }
    
    # Bardzo długie nazwy serwerów dla testu
    mock_ips = {"91.123.181.242": 600, "91.123.181.200": 120}
    mock_servers = {
        "Exatel Warsaw (HQ Main)": 500, 
        "Orange Warsaw (Secondary Backup)": 220
    }
    
    mock_bad_tests = [
        {"date": "2026-04-01 10:00", "down": 45.0, "up": 10.0, "ping": 120.5},
        {"date": "2026-04-03 21:15", "down": 12.5, "up": 2.1, "ping": 300.0},
    ]

    generate_report(
        month_year="Kwiecien 2026",
        isp_name="Firma Handlowa Giga Arkadiusz Kocma",
        stats=mock_stats,
        bad_tests=mock_bad_tests,
        ips=mock_ips,
        servers=mock_servers
    )