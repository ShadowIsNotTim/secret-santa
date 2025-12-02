import json
import os
from main import logger
from datetime import datetime

DATA_FILE = "users.json"


def load_users():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Ошибка загрузки: {e}")
        return {}


def save_user(user_id, user):
    try:
        users = load_users()
        users[str(user_id)] = {
            "tag": user,
            "registration_date": datetime.now().isoformat(),
            "user_id": user_id,
            "target": 0,
            "wishlist": ""
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        logger.info(f"Пользователь {user_id} сохранен")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")
        return False


def set_wishlist(user_id, new_wishlist):
    try:
        if new_wishlist:
            users = load_users()
            users[str(user_id)]["wishlist"] = new_wishlist
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=4)
            logger.info(f"Пользователь {user_id} сохранен")
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"Ошибка редактирования: {e}")
        return False


def set_target(user_id, target):
    try:
        users = load_users()
        users[str(user_id)]["target"] = target
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        logger.info(f"Пользователь {user_id} дарит {target}")
        return True
    except Exception as e:
        logger.error(f"Ошибка редактирования: {e}")
        return False


def check_wishlist(user_id):
    try:
        users = load_users()
        target = users[str(user_id)]["target"]
        if target == 0:
            return "Ивент еще не начался или период регистрации закончился"
        wishlist = users[str(target)]["wishlist"]
        logger.info(f"Пользователь {user_id} проверил вишлист цели")
        if wishlist == "":
            return "Вишлиста еще нет"
        return wishlist
    except Exception as e:
        logger.error(f"Ошибка проверки: {e}")
        return "Вишлиста еще нет"


def delete_user(user_id):
    try:
        users = load_users()
        users.pop(str(user_id))
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        logger.info(f"Пользователь {user_id} удален")
        return True
    except Exception as e:
        logger.error(f"Ошибка удаления")
        return False


def get_user(user_id):
    users = load_users()
    return users.get(str(user_id))
