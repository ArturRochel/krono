from datetime import date, datetime, time, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Label, Task, Appointment, ShiftEnum, AppointmentStatusEnum
from app.schemas import (
    LabelCreate, LabelResponse,
    TaskCreate, TaskResponse,
    AppointmentCreate, AppointmentResponse,
    TodayBriefingResponse, ShiftBlock, StatsResponse
)

router = APIRouter(prefix="/api", tags=["Krono"])


# ==========================================
# 1. FUNÇÃO AUXILIAR: CÁLCULO DE OFENSIVA
# ==========================================
def calculate_stats(db: Session, today: date) -> StatsResponse:
    # Total geral de tarefas + compromissos concluídos
    tasks_done_total = db.scalar(
        select(func.count(Task.id)).where(Task.completed_at.is_not(None))
    ) or 0
    appts_done_total = db.scalar(
        select(func.count(Appointment.id)).where(Appointment.completed_at.is_not(None))
    ) or 0

    # Total concluído hoje
    tasks_done_today = db.scalar(
        select(func.count(Task.id)).where(func.date(Task.completed_at) == today)
    ) or 0
    appts_done_today = db.scalar(
        select(func.count(Appointment.id)).where(func.date(Appointment.completed_at) == today)
    ) or 0

    # Busca todas as datas distintas em que algo foi concluído para calcular a ofensiva (streak)
    task_dates = db.scalars(
        select(func.date(Task.completed_at)).where(Task.completed_at.is_not(None)).distinct()
    ).all()
    appt_dates = db.scalars(
        select(func.date(Appointment.completed_at)).where(Appointment.completed_at.is_not(None)).distinct()
    ).all()

    active_dates = set(task_dates) | set(appt_dates)

    # Conta dias consecutivos para trás
    streak = 0
    check_date = today if today in active_dates else (today - timedelta(days=1))

    while check_date in active_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return StatsResponse(
        streak_days=streak,
        completed_today=tasks_done_today + appts_done_today,
        completed_total=tasks_done_total + appts_done_total,
    )


# ==========================================
# 2. ENDPOINT PRINCIPAL: VISÃO DO DIA (HOJE)
# ==========================================
@router.get("/briefing/today", response_model=TodayBriefingResponse)
def get_today_briefing(db: Session = Depends(get_db)):
    today = date.today()

    # Compromissos marcados para hoje (ordenados por horário)
    appointments = db.scalars(
        select(Appointment)
        .options(joinedload(Appointment.label))
        .where(Appointment.date == today)
        .order_by(Appointment.start_time.asc())
    ).all()

    # Tarefas planejadas para hoje OU pendentes de dias anteriores (Rollover)
    tasks = db.scalars(
        select(Task)
        .options(joinedload(Task.label))
        .where(
            or_(
                Task.scheduled_date == today,
                (Task.scheduled_date < today) & (Task.completed_at.is_(None)),
            )
        )
        .order_by(Task.completed_at.asc().nullsfirst(), Task.scheduled_date.asc(), Task.id.asc())
    ).all()

    def build_block(shift: ShiftEnum) -> ShiftBlock:
        block_appts = [a for a in appointments if a.shift == shift]
        block_tasks = [t for t in tasks if t.shift == shift]
        return ShiftBlock(
            total_count=len(block_appts) + len(block_tasks),
            appointments=block_appts,
            tasks=block_tasks,
        )

    return TodayBriefingResponse(
        date=today,
        stats=calculate_stats(db, today),
        manha=build_block(ShiftEnum.MANHA),
        tarde=build_block(ShiftEnum.TARDE),
        noite=build_block(ShiftEnum.NOITE),
    )


# ==========================================
# 3. ROTAS DE LABELS (CATEGORIAS)
# ==========================================
@router.get("/labels", response_model=List[LabelResponse])
def list_labels(db: Session = Depends(get_db)):
    return db.scalars(select(Label).order_by(Label.name.asc())).all()


@router.post("/labels", response_model=LabelResponse, status_code=201)
def create_label(payload: LabelCreate, db: Session = Depends(get_db)):
    label = Label(**payload.model_dump())
    db.add(label)
    db.commit()
    db.refresh(label)
    return label


# ==========================================
# 4. ROTAS DE TAREFAS (TASKS)
# ==========================================
@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/toggle", response_model=TaskResponse)
def toggle_task_completion(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    if task.completed_at is None:
        task.completed_at = datetime.now().astimezone()
    else:
        task.completed_at = None

    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    db.delete(task)
    db.commit()


# ==========================================
# 5. ROTAS DE COMPROMISSOS (APPOINTMENTS)
# ==========================================
@router.post("/appointments", response_model=AppointmentResponse, status_code=201)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    appt = Appointment(**payload.model_dump())
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


@router.patch("/appointments/{appt_id}/toggle", response_model=AppointmentResponse)
def toggle_appointment_completion(appt_id: int, db: Session = Depends(get_db)):
    appt = db.get(Appointment, appt_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Compromisso não encontrado")

    if appt.status != AppointmentStatusEnum.COMPLETED:
        appt.status = AppointmentStatusEnum.COMPLETED
        appt.completed_at = datetime.now().astimezone()
    else:
        appt.status = AppointmentStatusEnum.SCHEDULED
        appt.completed_at = None

    db.commit()
    db.refresh(appt)
    return appt


@router.delete("/appointments/{appt_id}", status_code=204)
def delete_appointment(appt_id: int, db: Session = Depends(get_db)):
    appt = db.get(Appointment, appt_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Compromisso não encontrado")
    db.delete(appt)
    db.commit()


# ==========================================
# 6. SEED DE DADOS INICIAIS (PARA TESTE RÁPIDO)
# ==========================================
@router.post("/seed", status_code=201)
def seed_initial_data(db: Session = Depends(get_db)):
    if db.scalar(select(func.count(Label.id))) > 0:
        return {"message": "O banco já possui dados iniciais."}

    lbl_pessoal = Label(name="Pessoal", icon="user", color="#10b981")
    lbl_faculdade = Label(name="Faculdade", icon="graduation-cap", color="#3b82f6")
    lbl_trabalho = Label(name="Trabalho", icon="briefcase", color="#8b5cf6")
    db.add_all([lbl_pessoal, lbl_faculdade, lbl_trabalho])
    db.flush()

    today = date.today()
    yesterday = today - timedelta(days=1)

    db.add_all([
        Task(
            title="Tomar vitaminas / Remédio",
            scheduled_date=today,
            shift=ShiftEnum.MANHA,
            is_recurring=True,
            label_id=lbl_pessoal.id,
        ),
        Task(
            title="Revisar PR do sistema legado",
            scheduled_date=yesterday,  # Vai aparecer como "Ontem"!
            shift=ShiftEnum.MANHA,
            label_id=lbl_trabalho.id,
        ),
        Appointment(
            title="Daily de alinhamento",
            date=today,
            start_time=time(9, 30),
            end_time=time(10, 0),
            location="Google Meet",
            label_id=lbl_trabalho.id,
        ),
        Task(
            title="Estudar árvores balanceadas e entregar lista",
            scheduled_date=today,
            shift=ShiftEnum.TARDE,
            attachments=[{"title": "PDF da Lista", "url": "https://sigaa.ufrn.br", "type": "pdf"}],
            label_id=lbl_faculdade.id,
        ),
        Task(
            title="Separar roupas e organizar mochila de amanhã",
            scheduled_date=today,
            shift=ShiftEnum.NOITE,
            label_id=lbl_pessoal.id,
        ),
    ])
    db.commit()
    return {"message": "Dados de exemplo criados com sucesso!"}