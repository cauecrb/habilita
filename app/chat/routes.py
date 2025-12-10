from flask import render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from . import chat_bp
from ..extensions import db
from ..models import User, Conversation, Message

def can_access(conv: Conversation) -> bool:
    return current_user.is_authenticated and (current_user.is_admin or current_user.id in (conv.tutor_id, conv.student_id))

@chat_bp.route("/")
@login_required
def list_conversations():
    if current_user.is_admin:
        convs = Conversation.query.order_by(Conversation.created_at.desc()).all()
    else:
        convs = Conversation.query.filter((Conversation.tutor_id == current_user.id) | (Conversation.student_id == current_user.id)).order_by(Conversation.created_at.desc()).all()
    items = []
    for c in convs:
        other_id = c.student_id if current_user.id == c.tutor_id else c.tutor_id
        other = User.query.get(other_id)
        last = Message.query.filter_by(conversation_id=c.id).order_by(Message.created_at.desc()).first()
        items.append({"conv": c, "other": other, "last": last})
    return render_template("chat_list.html", items=items)

@chat_bp.route("/start/<int:tutor_id>")
@login_required
def start(tutor_id: int):
    tutor = User.query.get_or_404(tutor_id)
    if not tutor.is_professor:
        abort(400)
    if not current_user.is_aluno and not current_user.is_admin:
        abort(403)
    student_id = current_user.id if current_user.is_aluno else None
    if student_id is None:
        abort(403)
    conv = Conversation.query.filter_by(tutor_id=tutor.id, student_id=student_id).first()
    if not conv:
        conv = Conversation(tutor_id=tutor.id, student_id=student_id)
        db.session.add(conv)
        db.session.commit()
    return redirect(url_for("chat.thread", conversation_id=conv.id))

@chat_bp.route("/<int:conversation_id>", methods=["GET", "POST"])
@login_required
def thread(conversation_id: int):
    conv = Conversation.query.get_or_404(conversation_id)
    if not can_access(conv):
        abort(403)
    if request.method == "POST":
        body = request.form.get("body", "").strip()
        if body:
            msg = Message(conversation_id=conv.id, sender_id=current_user.id, body=body)
            db.session.add(msg)
            db.session.commit()
        return redirect(url_for("chat.thread", conversation_id=conv.id))
    msgs = Message.query.filter_by(conversation_id=conv.id).order_by(Message.created_at.asc()).all()
    tutor = User.query.get(conv.tutor_id)
    student = User.query.get(conv.student_id)
    return render_template("chat_thread.html", conv=conv, msgs=msgs, tutor=tutor, student=student)
