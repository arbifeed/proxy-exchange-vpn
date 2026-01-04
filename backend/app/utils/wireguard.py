import subprocess


def generate_keypair() -> tuple[str, str]:
    private_key = subprocess.check_output(["wg", "genkey"]).strip()
    public_key = subprocess.check_output(
        ["wg", "pubkey"],
        input=private_key,
    ).strip()

    return private_key.decode(), public_key.decode()
