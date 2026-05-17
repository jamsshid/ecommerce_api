import mimetypes

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.urls import reverse
from django.utils.deconstruct import deconstructible


@deconstructible
class DatabaseStorage(Storage):
    """
    Custom Django storage backend that stores file content
    as binary data in the PostgreSQL database (DBFile model).
    """

    def _open(self, name, mode="rb"):
        from .models import DBFile

        db_file = DBFile.objects.get(name=name)
        return ContentFile(bytes(db_file.content), name=name)

    def _save(self, name, content):
        from .models import DBFile

        content.seek(0)
        data = content.read()
        content_type, _ = mimetypes.guess_type(name)

        DBFile.objects.update_or_create(
            name=name,
            defaults={
                "content": data,
                "content_type": content_type or "application/octet-stream",
                "size": len(data),
            },
        )
        return name

    def exists(self, name):
        from .models import DBFile

        return DBFile.objects.filter(name=name).exists()

    def delete(self, name):
        from .models import DBFile

        DBFile.objects.filter(name=name).delete()

    def size(self, name):
        from .models import DBFile

        try:
            return DBFile.objects.get(name=name).size
        except DBFile.DoesNotExist:
            return 0

    def url(self, name):
        return reverse("common:serve_file", kwargs={"name": name})
