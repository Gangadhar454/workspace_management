from django.db import models
from django.core.exceptions import ValidationError
import uuid
from users.models import User, Team
from datetime import time
from bookings.utils import is_valid_time_slot

class RoomType(models.TextChoices):
    PRIVATE = 'private', 'Private'
    CONFERENCE = 'conference', 'Conference'
    SHARED = 'shared', 'Shared'

class Room(models.Model):
    room_type = models.CharField(max_length=20, choices=RoomType.choices)
    capacity = models.IntegerField()
    
    def __str__(self):
        return f"{self.room_type} Room {self.id}"

class Booking(models.Model):
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if not (self.user or self.team):
            raise ValidationError("Booking must have either a user or a team.")
        if self.user and self.team:
            raise ValidationError("Booking cannot have both a user and a team.")
        if not is_valid_time_slot(self.start_time, self.end_time):
            raise ValidationError("Invalid time slot. Must be hourly between 9 AM and 6 PM.")
    
    def __str__(self):
        return f"Booking {self.booking_id}"

