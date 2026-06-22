from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SessionForm
from .models import DueDiligenceSession
from .services.rag_pipeline import ask_question, generate_report


@login_required
def session_list(request):
    sessions = DueDiligenceSession.objects.filter(owner=request.user)
    return render(request, "analysis/session_list.html", {"sessions": sessions})


@login_required
def session_create(request):
    if request.method == "POST":
        form = SessionForm(request.POST, owner=request.user)
        if form.is_valid():
            session = form.save(commit=False)
            session.owner = request.user
            session.save()
            form.save_m2m()
            return redirect("analysis:session_detail", pk=session.pk)
    else:
        form = SessionForm(owner=request.user)
    return render(request, "analysis/session_create.html", {"form": form})


@login_required
def session_detail(request, pk):
    session = get_object_or_404(DueDiligenceSession, pk=pk, owner=request.user)

    if request.method == "POST":
        if "generate_report" in request.POST:
            try:
                generate_report(session)
            except ValueError as exc:
                messages.error(request, str(exc))
        elif "question" in request.POST:
            question_text = request.POST.get("question", "").strip()
            if question_text:
                try:
                    ask_question(session, question_text)
                except ValueError as exc:
                    messages.error(request, str(exc))
        return redirect("analysis:session_detail", pk=session.pk)

    latest_report = session.reports.first()
    questions = session.questions.all()
    return render(
        request,
        "analysis/session_detail.html",
        {"session": session, "report": latest_report, "questions": questions},
    )
