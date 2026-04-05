import speedtest
from datetime import datetime, timezone

def get_timestampz():
    now_utc = datetime.now(timezone.utc)
    postgres_format = now_utc.isoformat(sep=' ')
    return postgres_format


print(f"[*] {get_timestampz()}: Starting speedtest using Ofelia...")


# speedtest module
try:
    start_time = get_timestampz()
    st = speedtest.Speedtest(secure=True)
    st.get_best_server()
    st.download()
    st.upload()

    finish_time = get_timestampz()
    st_dict: dict = st.results.dict()


    results = st.results

    download_speed: float = results.download / 1_000_000  # Mbps
    upload_speed: float = results.upload / 1_000_000  # Mbps
    ping: float = results.ping  # ms
except Exception as e:
    print(f"[!] {get_timestampz()}: Speedtest error: {e}")


# saving to db module
try:
    pass

except:
    pass


# debug log module
try:
    print(f"[*] Download: {download_speed:.2f} Mbps; Upload: {upload_speed:.2f} Mbps; Ping: {ping} ms")
    print(f"[*] Speedtest server: {st_dict['server']}")
    print(f"[*] Speedtest client: {st_dict['client']}")
    print(f"[+] {get_timestampz()}: Speedtest successful")

except Exception as e:
    print(f"[!] {get_timestampz()}: Logging error: {e}")