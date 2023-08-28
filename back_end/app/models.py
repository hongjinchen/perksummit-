from flask_login import UserMixin
from app import db
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120),nullable=True) 
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)
    @property
    def is_active(self):
        return True
    def get_id(self):
        return str(self.id)
    
class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    lecturer_name = db.Column(db.String(255), nullable=False)
    enrollment_limit = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1024)) 
    course_type = db.Column(db.String(50), nullable=False) 
    schedules = db.relationship('CourseSchedule', backref='course', lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class CourseSchedule(db.Model):
    __tablename__ = 'course_schedule'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(255), nullable=False)
    registered = db.Column(db.Integer, nullable=False)
    max = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)


class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'), nullable=False)
    course_time = db.Column(db.String(255), nullable=False)