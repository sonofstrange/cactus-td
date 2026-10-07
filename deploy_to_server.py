# -*- coding: utf-8 -*-
"""
deploy_to_server.py
Скрипт загрузки бэкенда на сервер 185.176.94.10, настройки systemd и проверки.
"""
import os
import paramiko

HOST = "185.176.94.10"
USER = "root"
PASS = "3sZEhYzgSBYWcw7"
REMOTE_DIR = "/opt/cactus_leaderboard"

SYSTEMD_UNIT = """[Unit]
Description=Cactus TD Leaderboard API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/cactus_leaderboard
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8095
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

def deploy():
    print("1. Connecting to server via SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=15)

    print("2. Ensuring directory /opt/cactus_leaderboard exists...")
    ssh.exec_command(f"mkdir -p {REMOTE_DIR}")

    print("3. Uploading app.py via SFTP...")
    sftp = ssh.open_sftp()
    local_app = os.path.join(os.path.dirname(__file__), "server_app.py")
    sftp.put(local_app, f"{REMOTE_DIR}/app.py")

    print("4. Writing systemd service /etc/systemd/system/cactus-leaderboard.service...")
    with sftp.open("/etc/systemd/system/cactus-leaderboard.service", "w") as f:
        f.write(SYSTEMD_UNIT)
    sftp.close()

    print("5. Reloading systemd and restarting cactus-leaderboard service...")
    cmds = [
        "systemctl daemon-reload",
        "systemctl enable cactus-leaderboard",
        "systemctl restart cactus-leaderboard",
        "sleep 2",
        "systemctl status cactus-leaderboard --no-pager",
        "curl -s http://127.0.0.1:8095/api/health"
    ]
    for c in cmds:
        stdin, stdout, stderr = ssh.exec_command(c)
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        print(f"--- [ {c} ] ---")
        if out: print("OUT:\n", out.encode('ascii', errors='replace').decode('ascii'))
        if err: print("ERR:\n", err.encode('ascii', errors='replace').decode('ascii'))

    ssh.close()
    print("Deployment completed successfully!")

if __name__ == "__main__":
    deploy()
