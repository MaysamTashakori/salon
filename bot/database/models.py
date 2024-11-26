from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base, SessionLocal
import enum
from datetime import datetime, timedelta 

class UserRole(enum.Enum):
    CLIENT = "client"
    ADMIN = "admin"
    STAFF = "staff"

class AppointmentStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    created_at = Column(DateTime, default=func.now())
    last_visit = Column(DateTime)
    total_visits = Column(Integer, default=0)
    is_blocked = Column(Boolean, default=False)
    notes = Column(Text)
    
    appointments = relationship("Appointment", foreign_keys='Appointment.user_id', back_populates="user")
    reviews = relationship("Review", back_populates="user")
    
    @classmethod
    def get_by_telegram_id(cls, telegram_id: int):
        with SessionLocal() as session:
            return session.query(cls).filter(cls.telegram_id == telegram_id).first()
            
    @classmethod
    def create_user(cls, telegram_id: int, phone: str, full_name: str, role: UserRole = UserRole.CLIENT):
        with SessionLocal() as session:
            user = cls(
                telegram_id=telegram_id,
                phone=phone,
                full_name=full_name,
                role=role
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def update_visit(self):
        with SessionLocal() as session:
            session.add(self)
            self.last_visit = func.now()
            self.total_visits += 1
            session.commit()
            return True

    def update_full_name(self, new_name: str):
        with SessionLocal() as session:
            session.add(self)
            self.full_name = new_name
            session.commit()
            return True

    def update_phone_number(self, new_phone: str):
        with SessionLocal() as session:
            session.add(self)
            self.phone = new_phone
            session.commit()
            return True

class Service(Base):
    __tablename__ = 'services'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)
    category = Column(String(50))
    image_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    max_daily_appointments = Column(Integer, default=10)
    discount_percentage = Column(Float, default=0)
    
    appointments = relationship("Appointment", back_populates="service")
    reviews = relationship("Review", back_populates="service")
    
    @classmethod
    def get_all_active(cls):
        with SessionLocal() as session:
            return session.query(cls).filter(cls.is_active == True).all()
            
    @classmethod
    def get_by_id(cls, service_id: int):
        with SessionLocal() as session:
            return session.query(cls).filter(cls.id == service_id).first()
            
    @classmethod
    def create_service(cls, name: str, description: str, price: float, duration: int, **kwargs):
        with SessionLocal() as session:
            service = cls(
                name=name,
                description=description,
                price=price,
                duration=duration,
                **kwargs
            )
            session.add(service)
            session.commit()
            session.refresh(service)
            return service

    def get_final_price(self):
        if self.discount_percentage:
            return self.price * (1 - self.discount_percentage / 100)
        return self.price

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', name='fk_appointment_user'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('users.id', name='fk_appointment_staff'))
    appointment_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    cancellation_reason = Column(Text)
    special_requests = Column(Text)
    final_price = Column(Float)
    
    user = relationship("User", foreign_keys=[user_id], back_populates="appointments")
    staff = relationship("User", foreign_keys=[staff_id], backref="staff_appointments")
    service = relationship("Service", back_populates="appointments")
    review = relationship("Review", back_populates="appointment", uselist=False)

    @classmethod
    def create_appointment(cls, user_id: int, service_id: int, appointment_time: DateTime, **kwargs):
        with SessionLocal() as session:
            service = session.query(Service).get(service_id)
            appointment = cls(
                user_id=user_id,
                service_id=service_id,
                appointment_time=appointment_time,
                end_time=appointment_time + timedelta(minutes=service.duration),
                final_price=service.get_final_price(),
                **kwargs
            )
            session.add(appointment)
            session.commit()
            session.refresh(appointment)
            return appointment

    @classmethod
    def get_user_appointments(cls, user_id: int, status=None):
        with SessionLocal() as session:
            query = session.query(cls).filter(cls.user_id == user_id)
            if status:
                query = query.filter(cls.status == status)
            return query.order_by(cls.appointment_time.desc()).all()

    @classmethod
    def check_time_availability(cls, service_id: int, date, time_str):
        with SessionLocal() as session:
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d')
            time = datetime.strptime(time_str, '%H:%M').time()
            appointment_time = datetime.combine(date, time)
            
            service = session.query(Service).get(service_id)
            end_time = appointment_time + timedelta(minutes=service.duration)
            
            conflicts = session.query(cls).filter(
                cls.service_id == service_id,
                cls.status != AppointmentStatus.CANCELLED,
                cls.appointment_time < end_time,
                cls.end_time > appointment_time
            ).count()
            
            return conflicts == 0

    @classmethod
    def check_date_availability(cls, service_id: int, date):
        with SessionLocal() as session:
            start_of_day = datetime.combine(date.togregorian(), datetime.min.time())
            end_of_day = datetime.combine(date.togregorian(), datetime.max.time())
            
            count = session.query(cls).filter(
                cls.service_id == service_id,
                cls.appointment_time >= start_of_day,
                cls.appointment_time <= end_of_day,
                cls.status != AppointmentStatus.CANCELLED
            ).count()
            
            service = session.query(Service).get(service_id)
            return count < service.max_daily_appointments

    def cancel(self, reason: str = None):
        with SessionLocal() as session:
            session.add(self)
            self.status = AppointmentStatus.CANCELLED
            self.cancellation_reason = reason
            session.commit()
            return True

    def confirm(self, staff_id: int = None):
        with SessionLocal() as session:
            session.add(self)
            self.status = AppointmentStatus.CONFIRMED
            if staff_id:
                self.staff_id = staff_id
            session.commit()
            return True

    def complete(self):
        with SessionLocal() as session:
            session.add(self)
            self.status = AppointmentStatus.COMPLETED
            self.user.update_visit()
            session.commit()
            return True

    @classmethod
    def get_staff_appointments(cls, staff_id: int, date=None):
        with SessionLocal() as session:
            query = session.query(cls).filter(cls.staff_id == staff_id)
            if date:
                start_of_day = datetime.combine(date, datetime.min.time())
                end_of_day = datetime.combine(date, datetime.max.time())
                query = query.filter(
                    cls.appointment_time >= start_of_day,
                    cls.appointment_time <= end_of_day
                )
            return query.order_by(cls.appointment_time).all()

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="reviews")
    service = relationship("Service", back_populates="reviews")
    appointment = relationship("Appointment", back_populates="review")

    @classmethod
    def create_review(cls, user_id: int, service_id: int, appointment_id: int, rating: int, comment: str = None):
        with SessionLocal() as session:
            review = cls(
                user_id=user_id,
                service_id=service_id,
                appointment_id=appointment_id,
                rating=rating,
                comment=comment
            )
            session.add(review)
            session.commit()
            session.refresh(review)
            return review

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default='pending')
    payment_method = Column(String(50))
    transaction_id = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    appointment = relationship("Appointment", backref="payment")
    
    @classmethod
    def create_payment(cls, appointment_id: int, amount: float, payment_method: str):
        with SessionLocal() as session:
            payment = cls(
                appointment_id=appointment_id,
                amount=amount,
                payment_method=payment_method
            )
            session.add(payment)
            session.commit()
            session.refresh(payment)
            return payment

    @classmethod
    def get_user_payments(cls, user_id: int):
        with SessionLocal() as session:
            return session.query(cls)\
                .join(Appointment)\
                .filter(Appointment.user_id == user_id)\
                .order_by(cls.created_at.desc())\
                .all()

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    is_from_user = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User", backref="chat_history")
    
    @classmethod
    def add_message(cls, user_id: int, message: str, is_from_user: bool = True):
        with SessionLocal() as session:
            chat_message = cls(
                user_id=user_id,
                message=message,
                is_from_user=is_from_user
            )
            session.add(chat_message)
            session.commit()
            session.refresh(chat_message)
            return chat_message
            
    @classmethod
    def get_user_history(cls, user_id: int, limit: int = 10):
        with SessionLocal() as session:
            return session.query(cls)\
                .filter(cls.user_id == user_id)\
                .order_by(cls.created_at.desc())\
                .limit(limit)\
                .all()
