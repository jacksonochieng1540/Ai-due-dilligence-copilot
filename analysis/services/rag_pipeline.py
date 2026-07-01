from django.utils import timezone

from ..models import AnalysisReport, Question


def ask_question(session, question_text: str) -> Question:
    """
    Ask a question about the documents in a session using RAG.

    This is a stub implementation. The actual implementation would:
    1. Retrieve relevant document chunks using vector similarity search
    2. Construct a prompt with the retrieved context
    3. Send to an LLM to generate an answer
    4. Store the question, answer, and retrieved chunks
    """
    question = Question.objects.create(
        session=session,
        question_text=question_text,
        answer_text="This is a stub answer. Implement RAG pipeline.",
    )
    return question


def generate_report(session) -> AnalysisReport:
    """
    Generate a comprehensive due diligence report for a session.

    This is a stub implementation. The actual implementation would:
    1. Retrieve all relevant document chunks for the company
    2. Generate structured analysis sections (financials, risks, etc.)
    3. Compile into a comprehensive report
    """
    if not session.documents.exists():
        raise ValueError("No documents in session to generate report from")

    report = AnalysisReport.objects.create(
        session=session,
        executive_summary="This is a stub executive summary. Implement RAG pipeline for full report generation.",
        risk_assessment=[],
        growth_opportunities=[],
        raw_llm_response={},
    )
    return report
