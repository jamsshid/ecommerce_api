from django.db import models


class DBFile(models.Model):
    """Stores uploaded files as binary content in PostgreSQL."""

    name = models.CharField(max_length=500, unique=True, db_index=True)
    content = models.BinaryField()
    content_type = models.CharField(max_length=100, blank=True)
    size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "db_files"
        verbose_name = "DB File"
        verbose_name_plural = "DB Files"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
