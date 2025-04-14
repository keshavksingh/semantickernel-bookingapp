import pyodbc
import os
from datetime import datetime

class BookingService:
    def __init__(self):
        self.conn = pyodbc.connect(os.getenv("AZURE_SQL_CONNECTION_STRING"))


        
    def get_hotelId(self, hotelName):
        cursor = self.conn.cursor()
        query = "SELECT TOP 1 HotelId FROM HotelTable WHERE HotelName = ?"
        print(f"Executing query to get hotel ID for name '{hotelName}'")

        cursor.execute(query, (hotelName,))
        row = cursor.fetchone()

        if row:
            return row.HotelId
        else:
            return -1

    def check_availability(self, date, hotel_id):
        cursor = self.conn.cursor()
        query = f"""
        SELECT HT.* FROM   HotelTable HT  LEFT JOIN (SELECT * FROM GuestAllocation WHERE [Date] = '{date}') GA
        ON HT.HotelId = GA.HotelId AND HT.RoomId = GA.RoomId
        WHERE GA.HotelId IS NULL AND GA.RoomId IS NULL AND HT.HotelId = '{hotel_id}'
        """

        #SELECT COUNT(*) as booked
        #FROM GuestAllocation
        #WHERE Date = '{date}' AND HotelId = '{hotel_id}' AND Status = 'booked'

        print(query)
        cursor.execute(query)
        rows = cursor.fetchall()
        #booked_count = cursor.fetchone()[0]
        return rows

    def make_reservation(self, data):
        cursor = self.conn.cursor()

        insert = f"""
        INSERT INTO GuestAllocation (BookingId, Date, HotelId, RoomId, CustomerId, BasePrice, Status)
        VALUES (NEWID(),'{data["date"].strip()}', '{data["hotel_id"]}', '{data["room_id"]}', '{data["customer_id"]}', 100, 'booked')
        """
        print(insert)
        
        cursor.execute(insert)
        self.conn.commit()
        return True

    def cancel_reservation(self, booking_id):
        cursor = self.conn.cursor()
        update = f"""
        UPDATE GuestAllocation
        SET Status = 'cancelled'
        WHERE BookingId = '{booking_id}'
        """
        print(update)
        cursor.execute(update)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_my_bookings(self, customerId: int) -> str:
        cursor = self.conn.cursor()
        # Get active future bookings
        query = """
        SELECT BookingId, HotelId, RoomId, Date, BasePrice, Status
        FROM GuestAllocation
        WHERE CustomerId = ? AND Status = 'booked' AND [Date] > GETDATE()
        """
        cursor.execute(query, (customerId,))
        rows = cursor.fetchall()
        return rows