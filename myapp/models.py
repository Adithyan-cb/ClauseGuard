from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Contract(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contracts")
    original_filename = models.CharField(max_length=500)
    file_path = models.CharField(max_length=400)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_filename} ({self.user.username})"


class ContractAnalysis(models.Model):
    id = models.AutoField(primary_key=True)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="analysis",
    )
    summary = models.TextField()
    risks = models.TextField()
    suggestions = models.TextField()
    comparison_result = models.TextField()
    analysed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Contract {self.contract.id}"


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

    def __str__(self):
        return f"Clause {self.id} (Contract {self.contract.id})"




class Complaint(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="complaints"
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
<<<<<<< HEAD
    date = models.CharField(max_length=100)


=======
    rating = models.IntegerField()
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.id} - Rating {self.rating}"
>>>>>>> abcfc4a072dfe10b5771c1baf266886ae3398f95
