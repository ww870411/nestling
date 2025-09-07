import logging
from sqlalchemy.orm import Session
from . import models, schemas, auth
from .database import SessionLocal, engine
from .template_data import projects_data, report_definitions_data, all_template_metrics, all_template_fields, initial_users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_db():
    db = SessionLocal()
    try:
        # 1. Seed Projects
        for proj_data in projects_data:
            project = db.query(models.Project).filter(models.Project.id == proj_data["id"]).first()
            if not project:
                logger.info(f"Creating project: {proj_data['name']}")
                db_project = models.Project(**proj_data)
                db.add(db_project)
            else:
                logger.info(f"Project {proj_data['name']} already exists.")
        db.commit()

        # 2. Seed Report Definitions
        for definition_data in report_definitions_data:
            definition = db.query(models.ReportDefinition).filter(models.ReportDefinition.id == definition_data["id"]).first()
            if not definition:
                logger.info(f"Creating report definition: {definition_data['name']}")
                db_definition = models.ReportDefinition(**definition_data)
                db.add(db_definition)
            else:
                logger.info(f"Report definition {definition_data['name']} already exists.")
        db.commit()

        # 3. Seed Template Fields
        for field_data in all_template_fields:
            field = db.query(models.TemplateField).filter(
                models.TemplateField.field_id == field_data["field_id"],
                models.TemplateField.template_name == field_data["template_name"],
                models.TemplateField.project_id == field_data["project_id"]
            ).first()
            if not field:
                # Log sparingly here as there are many fields
                db_field = models.TemplateField(**field_data)
                db.add(db_field)
        logger.info("Seeding template fields...")
        db.commit()
        logger.info("Template fields seeded.")

        # 4. Seed Template Metrics
        for metric_data in all_template_metrics:
            metric = db.query(models.TemplateMetric).filter(
                models.TemplateMetric.metric_id == metric_data["metric_id"],
                models.TemplateMetric.template_name == metric_data["template_name"],
                models.TemplateMetric.project_id == metric_data["project_id"]
            ).first()
            if not metric:
                # Log sparingly here as there are many metrics
                db_metric = models.TemplateMetric(**metric_data)
                db.add(db_metric)
        logger.info("Seeding template metrics...")
        db.commit()
        logger.info("Template metrics seeded.")

        # 5. Seed Users
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
    # This is handled by Alembic now, but keeping it doesn't hurt for standalone runs.
    models.Base.metadata.create_all(bind=engine)
    seed_db()
    logger.info("Database seeding finished.")