#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
main.py

Backend para MailXpress: invocado como proceso hijo desde Electron/Vue
Recibe JSON por stdin, envía correos SMTP con plantillas y adjuntos,
y emite logs/resultados por stdout.

Uso en Electron:
  const pyProc = spawn(path_to_executable, []);
  pyProc.stdin.write(JSON.stringify(payload) + '\n');
  pyProc.stdout.on('data', d => console.log(d.toString()));
"""

import sys
import json
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders



def process_payload(payload: dict) -> None:
    """Valida payload, envía correos uno a uno y reporta por stdout/stderr."""
    required = [
        "smtp_server",
        "smtp_port",
        "username",
        "password",
        "subject",
        "template",
        "contacts",
    ]
    for field in required:
        if field not in payload:
            logging.error("Missing required field: %s", field)
            return

    server_conf = {
        "host": payload["smtp_server"],
        "port": payload["smtp_port"],
        "user": payload["username"],
        "pass": payload["password"],
    }
    subject = payload["subject"]
    template = payload["template"]
    contacts = payload.get("contacts", [])
    attachments = payload.get("attachments", [])

    # Conexión SMTP
    try:
        server = smtplib.SMTP(server_conf["host"], server_conf["port"])
        server.starttls()
        server.login(server_conf["user"], server_conf["pass"])
    except Exception as e:
        logging.error("SMTP connection failed: %s", e)
        return

    # Envío a cada contacto
    for contact in contacts:
        to_email = contact.get("email")
        if not to_email:
            logging.error("Contact missing email: %s", contact)
            continue

        msg = MIMEMultipart()
        msg["From"] = server_conf["user"]
        msg["To"] = to_email
        msg["Subject"] = subject

        # Generar cuerpo
        try:
            body = template.format(**contact)
        except Exception as e:
            logging.error("Formatting error for %s: %s", to_email, e)
            body = template
        msg.attach(MIMEText(body, "plain"))

        # Adjuntos
        for rel_path in attachments:
            abs_path = os.path.abspath(rel_path)
            if not os.path.isfile(abs_path):
                logging.error("Attachment not found: %s", abs_path)
                continue
            try:
                with open(abs_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(abs_path)}"'
                )
                msg.attach(part)
            except Exception as e:
                logging.error("Error attaching %s: %s", abs_path, e)

        # Enviar mensaje
        try:
            server.send_message(msg)
            print(f"OK: enviado a {to_email}", flush=True)
        except Exception as e:
            logging.error("ERROR: %s - %s", to_email, e)

    server.quit()
    print("DONE", flush=True)


def read_stdin() -> None:
    """Lee payloads JSON línea a línea desde stdin y los procesa."""
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as e:
            logging.error("Invalid JSON: %s", e)
            continue
        process_payload(payload)


def main() -> None:
    """Punto de entrada: configura logging y arranca lector de stdin."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
    )
    try:
        read_stdin()
    except EOFError:
        pass  # stdin cerrado, terminamos limpiamente


if __name__ == "__main__":
    main()
