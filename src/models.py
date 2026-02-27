from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    base_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    files = relationship("File", back_populates="project")

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)
    filename = Column(String, nullable=False)
    extension = Column(String, nullable=True)
    size = Column(BigInteger, nullable=False)
    hash = Column(String, index=True, nullable=True)  # SHA256
    drive = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True)
    modified_at = Column(DateTime(timezone=True), nullable=True)
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    
    project = relationship("Project", back_populates="files")

class Duplicate(Base):
    __tablename__ = 'duplicates'
    id = Column(Integer, primary_key=True)
    original_file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    duplicate_file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    status = Column(String, default='pending')  # pending, resolved, ignored
    created_at = Column(DateTime(timezone=True), server_default=func.now())
