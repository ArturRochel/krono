import enum
from datetime import date, time, datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Boolean, Date, Time, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ShiftEnum(str, enum.Enum):
    MANHA = "MANHA"
    TARDE = "TARDE"
    NOITE = "NOITE"


class AppointmentStatusEnum(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class Label(Base):
    __tablename__ = "labels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    icon: Mapped[str] = mapped_column(String(50), default="tag")  # Nome do ícone no lucide-react
    color: Mapped[str] = mapped_column(String(20), default="#64748b")

    tasks: Mapped[List["Task"]] = relationship(back_populates="label")
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="label")


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    links: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    status: Mapped[AppointmentStatusEnum] = mapped_column(
        Enum(AppointmentStatusEnum), default=AppointmentStatusEnum.SCHEDULED
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Preparação futura para Google Calendar / Jira sem custo extra hoje
    external_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    label_id: Mapped[Optional[int]] = mapped_column(ForeignKey("labels.id", ondelete="SET NULL"), nullable=True)
    label: Mapped[Optional["Label"]] = relationship(back_populates="appointments")

    @property
    def shift(self) -> ShiftEnum:
        """Deduz automaticamente o bloco do dia pelo horário de início."""
        if self.start_time.hour < 12:
            return ShiftEnum.MANHA
        elif self.start_time.hour < 18:
            return ShiftEnum.TARDE
        return ShiftEnum.NOITE


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Data planejada para execução + Bloco do dia (Manhã, Tarde, Noite)
    scheduled_date: Mapped[date] = mapped_column(Date, index=True, default=date.today)
    shift: Mapped[ShiftEnum] = mapped_column(Enum(ShiftEnum), default=ShiftEnum.MANHA)
    
    # Prazos e lembretes
    deadline_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reminder_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    attachments: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    
    # Controle de conclusão e ofensiva (Streak)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    external_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    label_id: Mapped[Optional[int]] = mapped_column(ForeignKey("labels.id", ondelete="SET NULL"), nullable=True)
    label: Mapped[Optional["Label"]] = relationship(back_populates="tasks")