from sqlalchemy.orm import Session
from models import User, Role
from utils import hash_password

from utils import verify_password

# =========================
# CREATE USERsss
# =========================


def authenticate_user(db: Session, username: str, password: str):
    try:
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return None

        # compare plain password with hashed password
        if not verify_password(password, user.password):
            return None

        return user

    except Exception:
        return None
def create_user(db: Session, user):
    try:
        # check username
        if db.query(User).filter(User.username == user.username).first():
            return None, None, "Username already exists"

        # check email
        if db.query(User).filter(User.email == user.email).first():
            return None, None, "Email already exists"

        # get role
        role = db.query(Role).filter(Role.name == "user").first()
        if not role:
            return None, None, "Default role not found"

        user_data = user.model_dump()

        # hash password
        user_data["password"] = hash_password(user_data.pop("password"))

        # assign role
        user_data["role_id"] = role.id
        user_data["role_name"] = role.name
        # create object
        new_user = User(**user_data)

        db.add(new_user)

        # 🔥 IMPORTANT: flush so ID is generated
        db.flush()

        # safe response
        response = {
            "id": str(new_user.id),
            "username": new_user.username,
            "email": new_user.email,
            "role": role.name
        }

        return new_user, response, None

    except Exception as e:
        db.rollback()
        return None, None, str(e)


# =========================
# UPDATE USER
# =========================
def update_user(db: Session, user):
    try:
        db_user = db.query(User).filter(User.username == user.username).first()

        if not db_user:
            return None, None, "User not found"
        # print(user)
        data = user.model_dump(exclude_unset=True)
        data.pop("username", None)
        # print(data)

        # 🔐 password update
        if "password" in data:
            data["password"] = hash_password(data.pop("password"))

        # 🔥 FIXED ROLE UPDATE
        if "role_name" in data:
            role = db.query(Role).filter(Role.name == data["role_name"]).first()

            if not role:
                return None, None, "Invalid role"

            # ✅ set role_id in user table
            db_user.role_id = role.id

            # optional: keep role_name column if exists
            db_user.role_name = role.name
            # print(db_user)
            print("---------------------")
            # remove from dict so it doesn't conflict
            # data.pop("role_name")

        # 🔁 update remaining fields
        for k, v in data.items():
            setattr(db_user, k, v)

        # db.add(db_user)

        response = {
            "id": str(db_user.id),
            "username": db_user.username,
            "email": db_user.email,
            "role_name": db_user.role.name if db_user.role else None
        }

        return db_user, response, None

    except Exception as e:
        return None, None, str(e)


# =========================
# DELETE USER
# =========================
def delete_user(db: Session, username: str):
    try:
        db_user = db.query(User).filter(User.username == username).first()

        if not db_user:
            return False, "User not found"

        db.delete(db_user)

        return True, None

    except Exception as e:
        return False, str(e)