from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions.kernel_function import KernelFunction
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from services.booking_service import BookingService
from services.customer_service import CustomerService
from services.redis_memory_store import RedisMemoryStore


class BookingPlugin:
    def __init__(self):
        self.customer_service = CustomerService()
        self.db_service = BookingService()
        self.redis = RedisMemoryStore()

    @kernel_function(name="CheckAvailability", description="Check Hotel availability using CustomerName, Date and HotelName")
    async def check_availability(self, arguments: KernelArguments) -> str:
        name = arguments.get("CustomerName")
        print(f"Exracted CustomerName From the Message as Argument {name}")
        customer_id = await self.customer_service.get_customer_id_by_name(name)

        if customer_id == -1:
            return f"Sorry {name} you are not a registered customer. Please register to check availability."

        date = arguments.get("Date")
        HotelName = arguments.get("HotelName")

        hotel_id = self.db_service.get_hotelId(HotelName)
        if hotel_id == -1:
            return f"Sorry {name}, this {HotelName} is not listed in with the booking service."

        print(f"Exracted Date From the Message as Argument {date}")
        print(f"Exracted HotelId From the Message as Argument {hotel_id}")

        available = self.db_service.check_availability(date, hotel_id)

        if not available:
            return f"Sorry {name}, Hotel {HotelName} is Full. Booking Unavailable."

        await self.redis.append_conversation(customer_id, f"Checked availability for CustomerName {name} with CustomerId {customer_id} on {date} at Hotel {hotel_id}")

        lines = [f"Hi {name}, these are all the available options:"]
        for row in available:
            lines.append(f"• For Date {date} , Hotel {row.HotelId}, Room {row.RoomId} Room Type {row.RoomType}")
        return "\n".join(lines)
    
    @kernel_function(name="MakeReservation", description="Make a hotel reservation using CustomerName, HotelName, Date, and RoomId")
    async def make_reservation(self, arguments: KernelArguments) -> str:
        name = arguments.get("CustomerName")
        customer_id = await self.customer_service.get_customer_id_by_name(name)

        if customer_id == -1:
            return f"Sorry {name} you are not a registered customer. Please register to make a booking."        

        date = arguments.get("Date")
        HotelName = arguments.get("HotelName")
        hotel_id = self.db_service.get_hotelId(HotelName)
        if hotel_id == -1:
            return f"Sorry {name}, this {HotelName} is not listed in with the booking service."
        
        data = {
            "date": arguments.get("Date"),
            "hotel_id": hotel_id,
            "room_id": arguments.get("RoomId"),
            "customer_id": customer_id
        }
        available = self.db_service.check_availability(date, hotel_id)
    
        if not available:
            return f"Sorry {name}, Hotel {HotelName} is Full. Booking Unavailable."

        result = self.db_service.make_reservation(data)
        await self.redis.append_conversation(customer_id, f"Booked reservation for Customer {name} on {date} at Hotel {HotelName} for Room {hotel_id}")
        return (
            f"Booked reservation for Customer {name} on {date} at Hotel {HotelName} for Room {arguments.get('RoomId')}"
            if result
            else f"Failed to Book reservation for Customer {name} on {date} at Hotel {HotelName} for Room {arguments.get('RoomId')}")
    
    @kernel_function(name="CancelReservation", description="Cancel an existing hotel reservation for a CutomerName using BookingId")
    async def cancel_reservation(self, arguments: KernelArguments) -> str:
        name = arguments.get("CustomerName")
        customer_id = await self.customer_service.get_customer_id_by_name(name)

        if customer_id == -1:
            return f"Sorry {name} you are not a registered customer."        

        booking_id = arguments.get("BookingId")
        result = self.db_service.cancel_reservation(booking_id)
        await self.redis.append_conversation(customer_id, f"Canceled reservation For Customer {name} BookingId {booking_id}")
        return (
            f"Canceled reservation For Customer {name} BookingId {booking_id}"
            if result
            else f"Failed to cancel reservation For Customer {name} BookingId {booking_id}")
    
    @kernel_function(name="GetReservation", description="Get all active bookings for a CutomerName")
    async def get_reservation(self, arguments: KernelArguments) -> str:
        name = arguments.get("CustomerName")
        customer_id = await self.customer_service.get_customer_id_by_name(name)

        if customer_id == -1:
            return f"Sorry {name} you are not a registered customer."        
        result = self.db_service.get_my_bookings(customer_id)

        if not result:
            return f"Hi {name}, you have no active upcoming bookings."

        lines = [f"Hi {name}, here are your upcoming bookings:"]
        for row in result:
            date_str = row.Date.strftime("%Y-%m-%d")
            lines.append(
                f"• BookingId {row.BookingId} for Hotel {row.HotelId}, Room {row.RoomId} on {date_str} — ${row.BasePrice:.2f}"
            )
        return "\n".join(lines)


    @kernel_function(name="GetConversationHistory", description="Retrieve a customer's conversation history using CustomerName")
    async def get_history(self, arguments: KernelArguments) -> str:
        name = arguments.get("CustomerName")
        customer_id = await self.customer_service.get_customer_id_by_name(name)

        if customer_id == -1:
            return f"Sorry {name} you are not a registered customer."        
        
        history = await self.redis.get_conversation_history(customer_id)
        return "\n".join(history) if history else "No history available."

# Factory function to register plugin functions in kernel
def create_booking_plugin():
    return BookingPlugin()