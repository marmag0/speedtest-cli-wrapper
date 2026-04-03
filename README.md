# speedtest-cli-wrapper

This project is simple speedtest CLI wrapper to test your Internet access speed and your ISP's credibility. Lightweight, fully containerized and easy to setup!
Personally I run this wrapper on Proxmox home server - that's why main setup includes PostgreSQL setup.

## Setup

1. create .env
   1. come up with db credentails
   2. get your SMTP credentials / `app password` (e.g. [Gmail SMTP Server](https://youtu.be/ZfEK3WP73eY?si=jEGLnbSB6VSbl-pP))

```basic-example
...
```

2. run `docker-compose` (make sure you have [Docker](https://docs.docker.com/engine/install/))

```bash
...
```

## System Design

### Cloud Native Approach - used in this project

**System Desing Schema**
...(here will be a schema)

**Services Hierarchy**
...(here will be a schema)

### Python Loop Oriented Approach - not used in this project

**System Desing Schema**
![System Desing Schema](https://marmag0.github.io/endpoints/speedtest-cli-wrapper/speedtest-cli-wrapper.png)
