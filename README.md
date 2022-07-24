[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# Vpn4.One | VPN server setup automation app

This is the source code repo of https://vpn4.one/ service. 

# Run in docker

The preferred way to use the app is via docker container.

```bash
docker pull vpn41/vpn41
docker run --rm -p 8080:8080 vpn41/vpn41
```

Or build from source

```bash
git clone https://github.com/vpn41/vpn41.git
cd vpn41
./build
docker run --rm -p 8080:8080 vpn41/vpn41
```

Or with docker compose

```bash
git clone https://github.com/vpn41/vpn41.git
cd vpn41
docker-compose build vpn41
docker-compose up vpn41
```

Now open browser and enter the `http://localhost:8080/` to the address bar. Here you can setup both remote cloud
server and a server in your local network. Just enter the address of your server e.g. `192.168.0.7` in case of local network.

---
**NOTE**

The server being setup must provide root ssh access on 22 port. The only Ubuntu 20.04 LTS is now supported.

---

The easiest way to have Docker on Linux is described [here](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script).
For `docker-compose` [look here](https://docs.docker.com/compose/install/).

# Run directly on your host

Python 3.6+, ansible and sshpass are required. 

```bash
apt update && apt install -y sshpass ansible
git clone https://github.com/vpn41/vpn41.git
cd vpn41
app/app
```

# Run tests

Run `vpn41/app/app test` or `pytest` in the project root or app folder but be aware about dependencies in latter case.

# API
## POST https://vpn4.one/setup/ - Start setup 

The parameters are self descriptive 

`ip-address` - Target host ip address  
`ssh-user` - For now only `root` is allowed  
`ssh-password` - Target host ssh password for `root` account  
`first-setup` - Whether setup server and client or just client  
`download-keys` - Whether download keys or not from the target host

Response sets cookie `session`. This should be maintained in subsequent calls to have consistent results.

## GET https://vpn4.one/status/ - Get setup status

The result can be one of the following.

```json
{"status": "pending"}
{"status": "completed", "ok": "true"}
{"status": "completed", "ok": "false"}
{"status": "completed", "ok": "true", "keys_file_url": "/keys/"}
```

1. The first one indicates the setup is in progress.
2. Completed successfully 
3. Failure
4. Completed successfully with keys available via `keys_file_url`

## DELETE https://vpn4.one/status/ - Dismiss the setup status and keys if present 

## GET https://vpn4.one/keys/ - Download keys

Returns 5 client keys in `.ovpn` format archived with `.zip`.   

# Ansible scripts

The folder `vpn-setup` under the `app` folder contains ansible scripts and bash simple wrappers for them. These are divided into
local and remote scripts. Use scripts from `local` folder. 

For bunch setup using ansible scripts directly makes things easy like using ssh key pair authentication. 

`scratch-setup.sh HOSTNAME PASSWORD` - Installs prerequisites like docker and related stuff.  
`server-setup.sh HOSTNAME PASSWORD SERVER_PORT` - Setup the OpenVPN server.  
`client-setup.sh HOSTNAME PASSWORD FETCH_KEYS PLATFORM` - Setup 5 OpenVPN client keys.

`FETCH_KEYS` - is ansible compatible boolean type like strings `true`, `false`, `yes`, `no`. Keys are fetched to `/tmp/fetched`.  
`PLATFORM` - `linux` or whatever.

# Build an executable 

The binary is only available for Linux.

```bash
cd vpn41
build --binary
dist/vpn41
```

# Build web service with reverse proxy
 
Correct virtual host `server_name` in `vpn41/web/www.conf`.
Inside `vpn41` folder run `docker-compose build && docker compose up -d`.
Delivering containers to the target system is on you.
SSL Let's Encrypt certificate obtained and renewed automatically when run on target host.
