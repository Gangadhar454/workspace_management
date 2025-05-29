from django.urls import path
from bookings.views import (
    BookingCreateView,
    BookingCancelView,
    BookingListView,
    RoomAvailabilityView
)

urlpatterns = [
    path('bookings/', BookingListView.as_view(), name='booking-list'),
    path('bookings/create/', BookingCreateView.as_view(), name='booking-create'),
    path('cancel/<uuid:booking_id>/', BookingCancelView.as_view(), name='booking-cancel'),
    path('rooms/available/', RoomAvailabilityView.as_view(), name='room-availability'),
]