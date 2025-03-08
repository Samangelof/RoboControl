from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.ext.declarative import declarative_base
import datetime


Base = declarative_base()


#! Модель для робота КНП
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_number = Column(String, unique=True, nullable=False, index=True)
    processed_at = Column(DateTime, default=func.now(), nullable=False)


class Robot(Base):
    """Роботы в системе"""
    __tablename__ = 'robots'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    status = Column(String, default="active")  # active / disabled / error
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)


class SystemInfo(Base):
    """ПК, на которых работают роботы"""
    __tablename__ = 'system_info'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Базовая системная информация
    system = Column(String(50))  # uname.system
    node_name = Column(String(100))  # uname.node
    release = Column(String(100))  # uname.release
    version = Column(String(100))  # uname.version
    machine = Column(String(50))  # uname.machine
    processor = Column(String(100))  # uname.processor или cpuinfo.get_cpu_info()['brand_raw']
    ip_address = Column(String(50))  # socket.gethostbyname(socket.gethostname())
    mac_address = Column(String(50))  # ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    
    # Информация о CPU
    physical_cores = Column(Integer)  # psutil.cpu_count(logical=False)
    total_cores = Column(Integer)  # psutil.cpu_count(logical=True)
    cpu_max_freq = Column(Float)  # cpufreq.max
    cpu_min_freq = Column(Float)  # cpufreq.min
    cpu_current_freq = Column(Float)  # cpufreq.current
    cpu_total_usage = Column(Float)  # psutil.cpu_percent()
    
    # Информация о памяти
    total_memory = Column(Integer)  # svmem.total
    available_memory = Column(Integer)  # svmem.available
    used_memory = Column(Integer)  # svmem.used
    memory_percent = Column(Float)  # svmem.percent

class Config(Base):
    """Конфиги (замена JSON)"""
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("robots.id"))
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)


class Log(Base):
    """Логи работы роботов"""
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("robots.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    level = Column(String, nullable=False)  # INFO / ERROR / WARNING
    message = Column(String, nullable=False)