import speedtest
from datetime import datetime, timezone

def get_timestampz(now: datetime = datetime.now()):
    now_utc = datetime.now(timezone.utc)
    postgres_format = now_utc.isoformat(sep=' ')
    return postgres_format

print(f"[*] {get_timestampz()}: Starting speedtest using Ofelia...")

try:
    st = speedtest.Speedtest()
    st.get_best_server()
    st.download()
    st.upload()

    results = st.results

    download: float = results.download / 1_000_000  # Mbps
    upload: float = results.upload / 1_000_000  # Mbps
    ping: float = results.ping  # ms

    print(f"[*] Download: {download:.2f} Mbps; Upload: {upload:.2f} Mbps; Ping: {ping} ms")
    print(f"[+] {get_timestampz()}: Speedtest successful")

except Exception as e:
    print(f"[!] {get_timestampz()}: Speedtest error: {e}")