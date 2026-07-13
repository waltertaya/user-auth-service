from werkzeug.security import generate_password_hash, check_password_hash

revoked_tokens = set()

def hashing_password(password):
    return generate_password_hash(password)


def compare_password_hash(password_hash, password):
    return check_password_hash(password_hash, password)

def add_revoked_tokens(jti):
    revoked_tokens.add(jti)

def is_token_revoked(jti):
    return jti in revoked_tokens
