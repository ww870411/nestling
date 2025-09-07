from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Detailed user information
    unit = Column(String, nullable=False)
    global_role = Column(String, nullable=True) # e.g., 'super_admin', 'regional_admin'
    roles_by_project = Column(JSON, nullable=True) # e.g., {"heating_plan_2025-2026": "filler"}

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    report_definitions = relationship("ReportDefinition", back_populates="project")

class ReportDefinition(Base):
    __tablename__ = "report_definitions"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    template_name = Column(String, nullable=False)
    
    project = relationship("Project", back_populates="report_definitions")

class TemplateMetric(Base):
    __tablename__ = "template_metrics"
    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, nullable=False)
    template_name = Column(String, nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    category = Column(String)
    name = Column(String, nullable=False)
    unit = Column(String)
    type = Column(String) # 'basic' or 'calculated'
    formula = Column(Text, nullable=True)
    style = Column(JSON, nullable=True)
    same_period_editable = Column(JSON, nullable=True) # Mapped from samePeriodEditable
    required_properties = Column(JSON, nullable=True)

class TemplateField(Base):
    __tablename__ = "template_fields"
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, nullable=False)
    template_name = Column(String, nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    label = Column(String, nullable=False)
    type = Column(String) # 'basic' or 'calculated'
    component = Column(String)
    width = Column(Integer, nullable=True)
    fixed = Column(JSON, nullable=True) # Mapped from fixed
    formula = Column(Text, nullable=True)
