# speedtest-cli-wrapper

This project is simple speedtest CLI wrapper to test your Internet access speed and your ISP's credibility. Lightweight, fully containerized and easy to setup!
Personally I run this wrapper on Proxmox home server - that's why main setup includes PostgreSQL setup.

## Setup

1. Create `.env`
   1. come up with db credentials
   2. get your SMTP credentials - **app password** (e.g. [Gmail SMTP Server](https://youtu.be/ZfEK3WP73eY?si=jEGLnbSB6VSbl-pP))

```env
# Database credentials
POSTGRES_USER=postgres
POSTGRES_PASSWORD=SuperStrongPassword
POSTGRES_DB=speedtest-db

# SMTP credentials
SMTP_APP_PASSWD=SthStrongForSure
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=sender@addr.pl
REPORT_RECIPIENT=target1@addr.pl, target2@addr.pl, ...

# Thresholds for bad tests
MIN_DOWN=100
MIN_UP=20
MAX_PING=100
```

2. Run `docker-compose` (make sure you have [Docker](https://docs.docker.com/engine/install/))

```bash
docker compose up --build
```

3. That's it, everything works perfectly fine from this moment!

4. If you're not sure if it really does, perform quick test:
   1. Stop Docker with `docker compose down -v`
   2. Change report logic in `monthly_report.py`:

   ```python
   # original logic (previous month)
   if now.month == 1:
      report_month = 12
      report_year = now.year - 1
   else:
      report_month = now.month - 1
      report_year = now.year
   ```

   ```python
   # test logic (current month)
   report_month = now.month
   report_year = now.year
   ```

   3. Run once again `docker compose up --build`
   4. After full init, you can execute commands directly on the running container.
   5. Run: `for i in {1..5}; do docker compose exec speedtest-py python speedtest_app.py; done`
   6. Run: `docker compose exec speedtest-py python monthly_report.py`
   7. Check logs for errors and verify your email for the report!

## Report Generation

The application automatically generates a comprehensive PDF report every month using the **Ofelia** scheduler. The report includes:

- **Performance Overview**: Total tests, average download/upload speeds, and average ping.
- **Visual Data**: Pie charts representing client IP distribution and the speedtest servers used.
- **Contract Compliance**: A detailed table listing all tests that failed to meet your minimum speed and maximum ping requirements (defined in `.env`).
- **Automated Delivery**: The final PDF is sent directly to your specified email recipients via SMTP.

![Mock Email Example](https://marmag0.github.io/endpoints/speedtest-cli-wrapper/mock_mail.png)

![Mock Report Example](https://marmag0.github.io/endpoints/speedtest-cli-wrapper/mock_pdf.png)

## System Design

### Cloud Native Approach - used in this project

**System Design Schema**
![Current System Design Schema](https://marmag0.github.io/endpoints/speedtest-cli-wrapper/speedtest-cli-wrapper-ofelia.png)

**Services Hierarchy**
![Services Hierarchy Schema](https://marmag0.github.io/endpoints/speedtest-cli-wrapper/speedtest-cli-wrapper-hierarchy.png)

### Python Loop Oriented Approach - not used in this project

**System Design Schema**
![System Design Schema](https://marmag0.github.io/endpoints/speedtest-cli-wrapper/speedtest-cli-wrapper.png)
