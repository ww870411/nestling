import logging
from sqlalchemy.orm import Session

from . import models, schemas, auth
from .database import SessionLocal, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data from auth.js
initial_users = [
  {
    "username": 'group_admin',
    "password": 'password',
    "unit": '集团公司',
    "global_role": 'super_admin',
  },
  {
    "username": 'downtown_admin',
    "password": 'password',
    "unit": '主城区',
    "global_role": 'regional_admin',
  },
  {
    "username": 'beihai_filler',
    "password": 'password',
    "unit": '北海热电厂',
    "roles_by_project": {
      'heating_plan_2025-2026': 'filler',
    },
  },
  {
    "username": 'xianghai_filler',
    "password": 'password',
    "unit": '香海热电厂',
    "roles_by_project": {
      'heating_plan_2025-2026': 'filler',
    },
  },
  {
    "username": 'gongre_filler',
    "password": 'password',
    "unit": '供热公司',
    "roles_by_project": {
      'heating_plan_2025-2026': 'filler',
    },
  },
  {
    "username": 'jinzhou_filler',
    "password": 'password',
    "unit": '金州热电',
    "roles_by_project": {
      'heating_plan_2025-2026': 'filler',
    },
  },
  {
    "username": 'beifang_filler',
    "password": 'password',
    "unit": '北方热电',
    "roles_by_project": {
      'heating_plan_2025-2026': 'filler',
    },
  },
  {
    "username": 'jinpu_filler',
    "password": 'password',
    "unit": '金普热电',
    "roles_by_project": {
      'heating_plan_2025-2026': 'filler',
    },
  },
  {
    "username": 'zhuanghe_filler',
    "password": 'password',
    "unit": '庄河热电',
    "roles_by_project": {
      'heating_plan_2025-2026': 'filler',
    },
  },
  {
    "username": 'yanjiuyuan_filler',
    "password": 'password',
    "unit": '研究院',
    "roles_by_project": {
      'heating_plan_2025-2026': 'filler',
    },
  },
]

def seed_db():
    db = SessionLocal()
    try:
        for user_data in initial_users:
            user = db.query(models.User).filter(models.User.username == user_data["username"]).first()
            if not user:
                logger.info(f"Creating user: {user_data['username']}")
                user_in = schemas.UserCreate(
                    username=user_data["username"],
                    password=user_data["password"],
                    unit=user_data["unit"],
                    global_role=user_data.get("global_role"),
                    roles_by_project=user_data.get("roles_by_project")
                )
                hashed_password = auth.pwd_context.hash(user_in.password)
                db_user = models.User(
                    username=user_in.username,
                    hashed_password=hashed_password,
                    unit=user_in.unit,
                    global_role=user_in.global_role,
                    roles_by_project=user_in.roles_by_project
                )
                db.add(db_user)
            else:
                logger.info(f"User {user_data['username']} already exists.")
        
        db.commit()
        logger.info("User seeding complete.")

    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Initializing database seed...")
    # Make sure all tables are created before seeding
    models.Base.metadata.create_all(bind=engine)
    seed_db()
    logger.info("Database seeding finished.")
