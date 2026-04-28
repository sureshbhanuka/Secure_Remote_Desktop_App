import ssl

def create_tls_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(
        certfile="certs/host_cert.pem",
        keyfile="certs/host_key.pem"
    )
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations("certs/ca_cert.pem")
    return context