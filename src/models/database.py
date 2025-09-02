"""
Database models for Phase 2
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    analyses = relationship('Analysis', backref='user', lazy=True)
    
    def set_password(self, password: str):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Check if password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # nullable for anonymous users
    
    # Input data
    resume_text = Column(Text, nullable=False)
    job_description_text = Column(Text, nullable=False)
    resume_filename = Column(String(255), nullable=True)
    jd_filename = Column(String(255), nullable=True)
    
    # Analysis results
    scores = Column(JSON, nullable=False)  # Overall scores
    keyword_analysis = Column(JSON, nullable=False)  # Keyword matching results
    ats_analysis = Column(JSON, nullable=False)  # ATS compliance checks
    semantic_analysis = Column(JSON, nullable=True)  # Semantic similarity results
    named_entities = Column(JSON, nullable=True)  # Extracted entities
    suggestions = Column(JSON, nullable=True)  # AI suggestions
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis_version = Column(String(50), default='2.0')
    processing_time = Column(Float, nullable=True)  # seconds
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume_filename': self.resume_filename,
            'jd_filename': self.jd_filename,
            'scores': self.scores,
            'keyword_analysis': self.keyword_analysis,
            'ats_analysis': self.ats_analysis,
            'semantic_analysis': self.semantic_analysis,
            'named_entities': self.named_entities,
            'suggestions': self.suggestions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'analysis_version': self.analysis_version,
            'processing_time': self.processing_time
        }

class AnalysisHistory(db.Model):
    __tablename__ = 'analysis_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    analysis_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)
    action = Column(String(50), nullable=False)  # 'created', 'viewed', 'downloaded'
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)  # Additional action details
    
    # Relationships
    analysis = relationship('Analysis', backref='history', lazy=True)

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
