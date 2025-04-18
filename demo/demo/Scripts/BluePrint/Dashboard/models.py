from django.db import models
from Users.models import CustomUser
from cryptography.fernet import Fernet
from django.conf import settings
import base64

# Generate encryption key from the SECRET_KEY
ENCRYPTION_KEY = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode())

class Email(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="emails")
    sender = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="emails_sent")
    recipients = models.ManyToManyField(CustomUser, related_name="emails_received")
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)  # Will store encrypted content
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    starred = models.BooleanField(default=False, blank=True)
    deleted = models.BooleanField(default=False, blank=True)

    def encrypt_body(self, plaintext_body):
        """Encrypts the plaintext email body."""
        fernet = Fernet(ENCRYPTION_KEY)
        return fernet.encrypt(plaintext_body.encode()).decode()

    def decrypt_body(self):
        """Decrypts the encrypted email body."""
        try:
            fernet = Fernet(ENCRYPTION_KEY)
            return fernet.decrypt(self.body.encode()).decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return "Error decrypting the email body."

    def save(self, *args, **kwargs):
        """Override save method to ensure body is encrypted before saving."""
        if not self.pk:  # Encrypt only when the email is created
            self.body = self.encrypt_body(self.body)
        super().save(*args, **kwargs)

    def serialize(self):
        """Returns the email object data in a serialized form, including decrypted body and profile image."""
        return {
            "id": self.id,
            "username": f"{self.sender.first_name} {self.sender.last_name}".strip() or self.sender.username,
            "sender": self.sender.username,  # Changed from email to username
            "recipients": [f"{user.first_name} {user.last_name}".strip() or user.username for user in self.recipients.all()],
            "subject": self.subject,
            "body": self.decrypt_body(),
            "timestamp": self.timestamp.isoformat(),
            "read": self.read,
            "archived": self.archived,
            "starred": self.starred,
            "deleted": self.deleted,
            "attachments": [attachment.file.url for attachment in self.attachments.all()],
            "sender_profile_image": (
                self.sender.userprofile.profile_image.url
                if hasattr(self.sender, 'userprofile') and self.sender.userprofile.profile_image
                else '/static/images/default_profile.png'
            ),
        }
    

class Reply(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name="replies")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    body = models.TextField(blank=True)  # Encrypted content
    timestamp = models.DateTimeField(auto_now_add=True)

    def encrypt_body(self, plaintext_body):
        """Encrypts the plaintext reply body."""
        fernet = Fernet(ENCRYPTION_KEY)
        return fernet.encrypt(plaintext_body.encode()).decode()

    def decrypt_body(self):
        """Decrypts the encrypted reply body."""
        try:
            fernet = Fernet(ENCRYPTION_KEY)
            return fernet.decrypt(self.body.encode()).decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return "Error decrypting the reply body."

    def save(self, *args, **kwargs):
        """Override save method to ensure body is encrypted before saving."""
        if not self.pk:  # Encrypt only when the reply is created
            self.body = self.encrypt_body(self.body)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reply by {self.sender.username} to {self.email.subject}"

    def serialize(self):
        """Returns the reply object data in a serialized form."""
        username = f"{self.sender.first_name} {self.sender.last_name}".strip() or self.sender.username
        return {
            "sender": self.sender.username,  # Changed from email to username
            "username": username,
            "sender_profile_image": (
                self.sender.userprofile.profile_image.url
                if hasattr(self.sender, 'userprofile') and self.sender.userprofile.profile_image
                else '/static/images/default_profile.png'
            ),
            "body": self.decrypt_body(),
            "timestamp": self.timestamp.isoformat(),
            "attachments": [attachment.file.url for attachment in self.attachments.all()],
        }

class Attachment(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name="attachments", null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name="attachments", null=True, blank=True)
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')

    def __str__(self):
        return f"Attachment for {self.email or self.reply}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(email__isnull=False) | models.Q(reply__isnull=False),
                name='attachment_must_belong_to_email_or_reply'
            )
        ]


