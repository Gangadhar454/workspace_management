from rest_framework import serializers
from .models import Room, Booking, RoomType
from datetime import datetime
from bookings.utils import is_valid_time_slot

class RoomSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = ['id', 'room_type', 'capacity', 'is_available']
    
    def get_is_available(self, obj):
        request = self.context.get('request')
        start_time = request.query_params.get('start_time')
        if not start_time:
            return True
        start_time = datetime.fromisoformat(start_time)
        end_time = start_time.replace(hour=start_time.hour + 1)
        return not obj.bookings.filter(
            start_time__lte=end_time,
            end_time__gte=start_time
        ).exists()

class BookingSerializer(serializers.ModelSerializer):
    room_type = serializers.ChoiceField(choices=RoomType.choices, write_only=True)
    user_id = serializers.IntegerField(required=False, allow_null=True)
    team_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Booking
        fields = [
            'booking_id',
            'room',
            'room_type',
            'user_id',
            'team_id', 
            'start_time',
            'end_time',
            'created_at'
        ]
        read_only_fields = ['booking_id', 'created_at']
    
    def validate(self, data):
        start_time = data['start_time']
        end_time = data['end_time']
        room_type = data['room_type']
        
        if not is_valid_time_slot(start_time, end_time):
            raise serializers.ValidationError("Invalid time slot.")
        
        if not (data.get('user_id') or data.get('team_id')):
            raise serializers.ValidationError("Either user_id or team_id is required.")
        
        if data.get('user_id') and data.get('team_id'):
            raise serializers.ValidationError("Cannot provide both user_id and team_id.")
        
        if room_type == RoomType.CONFERENCE and data.get('user_id'):
            raise serializers.ValidationError("Conference rooms are for teams only.")
        
        if room_type == RoomType.PRIVATE and data.get('team_id'):
            raise serializers.ValidationError("Private rooms are for individual users only.")
        
        return data