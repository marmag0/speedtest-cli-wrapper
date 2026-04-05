import os
import speedtest
from datetime import datetime, timezone
from sqlalchemy import create_engine, text

def get_timestampz():
    now_utc = datetime.now(timezone.utc)
    postgres_format = now_utc.isoformat(sep=' ')
    return postgres_format


print(f"[*] {get_timestampz()}: Starting speedtest using Ofelia...")

# init variables
start_time = get_timestampz()
is_successful = False
error_message = None

finish_time = None
download_speed = None
upload_speed = None
ping = None
server_id = None
isp_id = None
client_ip = None
st_dict = None

# speedtest module
try:
    st = speedtest.Speedtest(secure=True)
    st.get_best_server()
    st.download()
    st.upload()

    finish_time = get_timestampz()
    results = st.results
    st_dict: dict = results.dict()
    

    download_speed: float = results.download / 1_000_000  # Mbps
    upload_speed: float = results.upload / 1_000_000  # Mbps
    ping: float = results.ping  # ms
    client_ip = st_dict['client']['ip']

    is_successful = True

except Exception as e:
    error_message = str(e)
    print(f"[!] {get_timestampz()}: Speedtest error: {e}")


# saving to db module
try:
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
    
    engine = create_engine(db_url)

    with engine.begin() as conn:
        
        if is_successful:
            # upsert: insert isp if not exists, return id
            query_isp = text("""
                INSERT INTO isps (isp_name, isp_country)
                VALUES (:isp_name, :isp_country)
                ON CONFLICT (isp_name) 
                DO UPDATE SET isp_name = EXCLUDED.isp_name
                RETURNING id;                 
            """)
            isp_id = conn.execute(query_isp, {
                "isp_name": st_dict['client']['isp'],
                "isp_country": st_dict['client']['country']
            }).scalar()

            # upsert: insert server if not exists, return id
            query_server = text("""
                INSERT INTO speedtest_servers (server_id, server_url, server_name, server_country, server_longitude, server_latitude)
                VALUES (:server_id, :server_url, :server_name, :server_country, :server_lon, :server_lat)
                ON CONFLICT (server_id) 
                DO UPDATE SET server_id = EXCLUDED.server_id
                RETURNING id;
            """)
            server_id = conn.execute(query_server, {
                "server_id": int(st_dict['server']['id']),
                "server_url": st_dict['server']['url'],
                "server_name": st_dict['server']['sponsor'],
                "server_country": st_dict['server']['cc'],
                "server_lon": float(st_dict['server']['lon']),
                "server_lat": float(st_dict['server']['lat'])
            }).scalar()

        # insert: save speedtest stats
        query_test = text("""
            INSERT INTO speedtests (
                start_time, is_successful, error_message, finish_time, 
                download_speed, upload_speed, ping, server_id, isp_id, client_ip
            ) VALUES (
                :start_time, :is_successful, :error_message, :finish_time, 
                :download, :upload, :ping, :server_id, :isp_id, :client_ip
            );
        """)
        conn.execute(query_test, {
            "start_time": start_time,
            "is_successful": is_successful,
            "error_message": error_message,
            "finish_time": finish_time,
            "download": download_speed,
            "upload": upload_speed,
            "ping": ping,
            "server_id": server_id,
            "isp_id": isp_id,
            "client_ip": client_ip
        })

except Exception as e:
    print(f"[!] {get_timestampz()}: Database error: {e}")


# debug log module
try:
    if is_successful:
        print(f"[*] Download: {download_speed:.2f} Mbps; Upload: {upload_speed:.2f} Mbps; Ping: {ping} ms")
        print(f"[*] Speedtest server: {st_dict['server']}")
        print(f"[*] Speedtest client: {st_dict['client']}")
        print(f"[+] {get_timestampz()}: Speedtest successful")
    else:
        print(f"[!] {get_timestampz()}: Speedtest failed - check database for error message")

except Exception as e:
    print(f"[!] {get_timestampz()}: Logging error: {e}")