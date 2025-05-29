from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from bookings.serializers import BookingSerializer, RoomSerializer
from bookings.models import Room, RoomType, Booking
from users.models import Team
from django.db.models import Count, Q
from datetime import datetime

class BookingCreateView(APIView):
    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            room_type = serializer.validated_data['room_type']
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['end_time']
            user_id = serializer.validated_data.get('user_id')
            team_id = serializer.validated_data.get('team_id')
            
            with transaction.atomic():
                # Lock rooms of the requested type
                available_rooms = Room.objects.select_for_update().filter(
                    room_type=room_type
                ).annotate(
                    booking_count=Count('bookings', filter=Q(
                        bookings__start_time__lte=end_time,
                        bookings__end_time__gte=start_time
                    ))
                )
                
                if room_type == RoomType.SHARED:
                    available_rooms = available_rooms.filter(booking_count__lt=4)
                else:
                    available_rooms = available_rooms.filter(booking_count=0)
                
                if not available_rooms.exists():
                    return Response(
                        {"error": "No available room for the selected slot and type."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                room = available_rooms.first()
                
                # Additional validation for conference rooms
                if room_type == RoomType.CONFERENCE and team_id:
                    team = Team.objects.get(id=team_id)
                    member_count = team.members.count()
                    if member_count < 3:
                        return Response(
                            {"error": "Conference rooms require 3+ members."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # Check for existing bookings
                if user_id and Booking.objects.filter(
                    user_id=user_id,
                    start_time__lte=end_time,
                    end_time__gte=start_time
                ).exists():
                    return Response(
                        {"error": "User already has a booking in this time slot."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if team_id and Booking.objects.filter(
                    team_id=team_id,
                    start_time__lte=end_time,
                    end_time__gte=start_time
                ).exists():
                    return Response(
                        {"error": "Team already has a booking in this time slot."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create booking
                booking = Booking.objects.create(
                    room=room,
                    user_id=user_id,
                    team_id=team_id,
                    start_time=start_time,
                    end_time=end_time
                )
                return Response(
                    BookingSerializer(booking).data,
                    status=status.HTTP_201_CREATED
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookingCancelView(APIView):
    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(booking_id=booking_id)
            booking.delete()
            return Response(
                {"message": "Booking cancelled successfully."},
                status=status.HTTP_200_OK
            )
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )

class BookingListView(APIView):
    def get(self, request):
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

class RoomAvailabilityView(APIView):
    def get(self, request):
        start_time_str = request.query_params.get('start_time')
        if not start_time_str:
            return Response(
                {"error": "start_time query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = start_time.replace(hour=start_time.hour + 1)
        except ValueError:
            return Response(
                {"error": "Invalid start_time format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rooms = Room.objects.annotate(
            booking_count=Count('bookings', filter=Q(
                bookings__start_time__lte=end_time,
                bookings__end_time__gte=start_time
            ))
        )
        serializer = RoomSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data)