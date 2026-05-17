from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email is required"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", CustomUser.Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("is_staff=True for Superuser"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("is_superuser=True for Superuser"))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "admin", _("Admin")
        CUSTOMER = "customer", _("Customer")
        SELLER = "seller", _("Seller")

    email = models.EmailField(_("Email"), unique=True)
    first_name = models.CharField(_("First Name"), max_length=150, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=150, blank=True)
    phone = models.CharField(_("Phone Number"), max_length=20, blank=True)
    role = models.CharField(
        _("Rol"),
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    avatar = models.ImageField(_("Avatar"), upload_to="avatars/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    @property
    def is_customer(self) -> bool:
        return self.role == self.Role.CUSTOMER

    @property
    def is_seller(self) -> bool:
        return self.role == self.Role.SELLER
