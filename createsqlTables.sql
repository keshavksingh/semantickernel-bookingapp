CREATE TABLE GuestAllocation(
BookingId UNIQUEIDENTIFIER,
HotelId INT,
RoomId INT,
CustomerId INT,
BasePrice MONEY,
Date DATETIME,
Status VARCHAR(500)
)

CREATE TABLE HotelTable (
HotelId INT,
HotelName VARCHAR(100),
RoomId INT,
RoomType VARCHAR(100))

INSERT INTO HotelTable
SELECT 1, 'HotelA',1,'Single Occupancy'
UNION ALL
SELECT 1, 'HotelA',2,'Double Occupancy'
UNION ALL
SELECT 1, 'HotelA',3,'Single Occupancy'