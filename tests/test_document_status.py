from app.models.document import Document


def test_document_qna_readiness_status():
    ready = Document(status="completed", total_chunks=5)
    processing = Document(status="processing", total_chunks=5)
    uploaded = Document(status="uploaded", total_chunks=5)
    failed = Document(status="failed", total_chunks=5)

    assert ready.is_ready_for_qna is True
    assert processing.is_ready_for_qna is False
    assert uploaded.is_ready_for_qna is False
    assert failed.is_ready_for_qna is False
