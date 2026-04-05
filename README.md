# speedtest-cli-wrapper

This project is simple speedtest CLI wrapper to test your Internet access speed and your ISP's credibility. Lightweight, fully containerized and easy to setup!
Personally I run this wrapper on Proxmox home server - that's why main setup includes PostgreSQL setup.

## Setup

1. Create `.env`
   1. come up with db credentials
   2. get your SMTP credentials - **app password** (e.g. [Gmail SMTP Server](https://youtu.be/ZfEK3WP73eY?si=jEGLnbSB6VSbl-pP))

```basic-example
POSTGRES_USER=postgres
POSTGRES_PASSWORD=SuperStrongPassword
POSTGRES_DB=speedtest-db

SMTP_APP_PASSWD=SthStrongForSure
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=sender@addr.pl
REPORT_RECIPIENT=target1@addr.pl, target2@addr.pl, ...
```

2. Run `docker-compose` (make sure you have [Docker](https://docs.docker.com/engine/install/))

```bash
docker compose up --build
```

3. That's it, everything works perfectly fine from this moment!

4. If you're not sure if it really does, perform quick test:

```bash
...
```

## System Design

### Cloud Native Approach - used in this project

**System Design Schema**
![Current System Design Schema](https://marmag0.github.io/endpoints/speedtest-cli-wrapper/speedtest-cli-wrapper-ofelia.png)

**Services Hierarchy**
![Services Hierarchy Schema](https://marmag0.github.io/endpoints/speedtest-cli-wrapper/speedtest-cli-wrapper-hierarchy.png)

### Python Loop Oriented Approach - not used in this project

**System Design Schema**
![System Design Schema](https://marmag0.github.io/endpoints/speedtest-cli-wrapper/speedtest-cli-wrapper.png)
