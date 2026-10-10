"""Thread-safe in-memory user store."""

import threading


class UserStore:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self._users = {}
            self._next_id = 1

    def create(self, username: str, password_hash: str, role: str) -> dict | None:
        with self._lock:
            if any(u["username"] == username for u in self._users.values()):
                return None
            user = {
                "id": self._next_id,
                "username": username,
                "password_hash": password_hash,
                "role": role,
            }
            self._next_id += 1
            self._users[user["id"]] = user
            return user

    def get_by_username(self, username: str) -> dict | None:
        with self._lock:
            for user in self._users.values():
                if user["username"] == username:
                    return user
            return None

    def all(self) -> list[dict]:
        with self._lock:
            return list(self._users.values())


user_store = UserStore()
