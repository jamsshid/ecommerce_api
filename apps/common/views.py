from django.http import Http404, HttpResponse

from .models import DBFile


def serve_file(request, name):
    """Serve a binary file stored in the database."""
    try:
        db_file = DBFile.objects.get(name=name)
    except DBFile.DoesNotExist:
        raise Http404("File not found")

    response = HttpResponse(
        bytes(db_file.content),
        content_type=db_file.content_type or "application/octet-stream",
    )
    response["Content-Length"] = db_file.size
    response["Cache-Control"] = "public, max-age=86400"
    return response
