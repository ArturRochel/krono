from datetime import date, time, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models import ShiftEnum, AppointmentStatusEnum


# --- LABELS ---
class LabelBase(BaseModel):
    name: str
    icon: str = "tag"
    color: str = "#64748b"


class LabelCreate(LabelBase):
    pass


class LabelResponse(LabelBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- LINKS / ANEXOS ---
class AttachmentItem(BaseModel):
    title: str
    url: str
    type: str = "link"  # ex: 'link', 'pdf', 'drive', 'github'


# --- TAREFAS (TASKS) ---
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_date: date = date.today()
    shift: ShiftEnum = ShiftEnum.MANHA
    deadline_at: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    is_recurring: bool = False
    attachments: List[Dict[str, Any]] = []
    label_id: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    scheduled_date: date
    shift: ShiftEnum
    deadline_at: Optional[datetime]
    reminder_at: Optional[datetime]
    is_recurring: bool
    attachments: List[Dict[str, Any]]
    completed_at: Optional[datetime]
    label: Optional[LabelResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- COMPROMISSOS (APPOINTMENTS) ---
class AppointmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    date: date = date.today()
    start_time: time
    end_time: Optional[time] = None
    location: Optional[str] = None
    links: List[Dict[str, Any]] = []
    label_id: Optional[int] = None


class AppointmentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    date: date
    start_time: time
    end_time: Optional[time]
    location: Optional[str]
    links: List[Dict[str, Any]]
    status: AppointmentStatusEnum
    completed_at: Optional[datetime]
    shift: ShiftEnum  # Vem da @property automática do model!
    label: Optional[LabelResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- RESUMO DO DIA (BRIEFING + OFENSIVA) ---
class ShiftBlock(BaseModel):
    total_count: int
    appointments: List[AppointmentResponse]
    tasks: List[TaskResponse]


class StatsResponse(BaseModel):
    streak_days: int
    completed_today: int
    completed_total: int


class TodayBriefingResponse(BaseModel):
    date: date
    stats: StatsResponse
    manha: ShiftBlock
    tarde: ShiftBlock
    noite: ShiftBlock