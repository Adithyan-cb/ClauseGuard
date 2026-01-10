from django.db import models
from django.contrib.auth.models import User


class Contract(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contracts")
    contract_file = models.FileField(upload_to='contracts/')
    llm_model = models.CharField(max_length=50)
    contract_type = models.CharField(max_length=50)
    jurisdiction = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} ({self.user.username})"


class ContractAnalysis(models.Model):
    id = models.AutoField(primary_key=True)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="analysis",
    )
    # JSON/text blobs stored as text (Pydantic-validated before save)
    summary = models.TextField(blank=True, null=True)
    clauses = models.TextField(blank=True, null=True)
    risks = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)
    comparison_result = models.TextField(blank=True, null=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    extraction_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    processing_time = models.FloatField(null=True, blank=True)
    analysed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Contract {self.contract.id} (status={self.extraction_status})"


class Clause(models.Model):

    class RiskLevel(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    id = models.AutoField(primary_key=True)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="clauses",
    )
    clause_type = models.CharField(max_length=100, blank=True)
    clause_text = models.TextField()  # longtext equivalent
    risk_level = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
    )
    missing_parts = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)
    similarity_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Clause {self.id} (Contract {self.contract.id})"




class Complaint(models.Model):
    class PriorityLevel(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="complaints"
    )
    subject = models.CharField(max_length=200,null=True,blank=True )
    category = models.CharField(max_length=50,null=True,blank=True )
    priority = models.CharField(
        max_length=10,
        choices=PriorityLevel.choices,
        default=PriorityLevel.MEDIUM,
    )
    message = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Complaint {self.id} by {self.user.username}"


class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedbacks"
    )
    date = models.CharField(max_length=100)
    category = models.CharField(max_length=50, null=True, blank=True)
    rating = models.IntegerField()
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.id} - Rating {self.rating}"
