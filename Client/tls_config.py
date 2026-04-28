import ssl

def create_tls_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations("certs/ca_cert.pem")
    context.load_cert_chain(
        certfile="certs/client_cert.pem",
        keyfile="certs/client_key.pem"
    )
    return context