import hashlib

import bcrypt


class Encryptor:

    @staticmethod
    def hash_password(password: str) -> str:
        sha256_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(sha256_hash.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        sha256_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
        return bcrypt.checkpw(
            password=sha256_hash.encode("utf-8"),
            hashed_password=hashed_password.encode("utf-8")
        )
