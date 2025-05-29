from django.test import TestCase
from rest_framework.test import APIClient
from bookings.models import Room, Booking, RoomType
from users.models import User, Team, TeamMember
from datetime import datetime
from django.utils import timezone

class BookingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test data
        self.user = User.objects.create(name="John Doe", age=30, gender="M")
        self.team = Team.objects.create(name="Test Team")
        TeamMember.objects.create(team=self.team, user=self.user, is_child=False)
        
        self.private_room = Room.objects.create(room_type=RoomType.PRIVATE, capacity=1)
        self.conference_room = Room.objects.create(room_type=RoomType.CONFERENCE, capacity=10)
        self.shared_room = Room.objects.create(room_type=RoomType.SHARED, capacity=4)
        
        self.start_time = timezone.make_aware(datetime(2025, 5, 28, 10, 0))
        self.end_time = timezone.make_aware(datetime(2025, 5, 28, 11, 0))
    
    def test_create_booking_private_room(self):
        data = {
            'room_type': 'private',
            'user_id': self.user.id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }
        response = self.client.post('/api/v1/bookings/create/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('booking_id', response.data)
    
    def test_create_booking_conference_room_invalid_team(self):
        data = {
            'room_type': 'conference',
            'team_id': self.team.id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }
        response = self.client.post('/api/v1/bookings/create/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
    
    def test_cancel_booking(self):
        booking = Booking.objects.create(
            room=self.private_room,
            user=self.user,
            start_time=self.start_time,
            end_time=self.end_time
        )
        response = self.client.post(f'/api/v1/cancel/{booking.booking_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Booking.objects.filter(booking_id=booking.booking_id).exists())
    
    def test_room_availability(self):
        response = self.client.get(
            f'/api/v1/rooms/available/?start_time={self.start_time.isoformat()}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)