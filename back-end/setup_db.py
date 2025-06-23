import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.sqlite import BLOB


Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, nullable=False)
    email = Column(String, nullable=True)

    conversations = relationship("Conversation", back_populates="user")
    file_uploads = relationship("FileUpload", back_populates="user")

class FileUpload(Base):
    __tablename__ = 'file_uploads'
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'))
    file_name = Column(String, nullable=False)
    file_token = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    user = relationship("User", back_populates="file_uploads")

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'))
    title = Column(String, nullable=False)

    user = relationship("User", back_populates="conversations")
    chats = relationship("Chat", back_populates="conversation")

class Chat(Base):
    __tablename__ = 'chats'
    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey('conversations.id'))
    content = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="chats")

# Create SQLite database
engine = create_engine("sqlite:///database.db", echo=True)
Base.metadata.create_all(engine)

print("Tables with UUID primary keys created successfully!")
