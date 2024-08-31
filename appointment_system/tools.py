import json
from .database import Database
from .models import Booking

class AppointmentTools:
    def __init__(self, db: Database):
        self.db = db
        self.available_slots = {
            "2024-08-30": {"09:00": True, "10:00": True, "11:00": True, "14:00": True, "15:00": True},
            "2024-08-31": {"09:30": True, "10:30": True, "11:30": True, "14:30": True, "15:30": True},
            "2024-09-01": {"10:00": True, "11:00": True, "13:00": True, "14:00": True, "16:00": True},
        }

    def get_available_time_slots(self, date):
        if date in self.available_slots:
            return [slot for slot, available in self.available_slots[date].items() if available]
        return []

    def create_booking(self, date, time, user_id):
        if date in self.available_slots and time in self.available_slots[date] and self.available_slots[date][time]:
            self.available_slots[date][time] = False
            booking = Booking(user_id, date, time)
            self.db.execute('''INSERT INTO bookings (user_id, date, time, status)
                               VALUES (?, ?, ?, ?)''', 
                            (booking.user_id, booking.date, booking.time, booking.status))
            self.db.commit()
            booking_id = self.db.cursor.lastrowid
            return json.dumps({"status": "success", "message": f"Booking created for {date} at {time}", "booking_id": booking_id})
        else:
            return json.dumps({"status": "error", "message": "Slot not available"})

    def cancel_booking(self, booking_id):
        self.db.execute('''SELECT date, time, status FROM bookings WHERE booking_id=?''', (booking_id,))
        result = self.db.fetchone()
        
        if result and result[2] == 'confirmed':
            date, time = result[0], result[1]
            self.db.execute('''DELETE FROM bookings WHERE booking_id=?''', (booking_id,))
            self.db.commit()
            if date in self.available_slots and time in self.available_slots[date]:
                self.available_slots[date][time] = True
            return json.dumps({"status": "success", "message": "Booking cancelled"})
        else:
            return json.dumps({"status": "error", "message": "Cannot cancel unconfirmed or non-existent booking"})

    def confirm_booking(self, booking_id, date, time):
        self.db.execute('''SELECT status FROM bookings WHERE booking_id=?''', (booking_id,))
        result = self.db.fetchone()
        
        if result and result[0] == 'pending':
            self.db.execute('''UPDATE bookings SET status=? WHERE booking_id=?''', ('confirmed', booking_id))
            self.db.commit()
            self.available_slots[date][time] = False
            return json.dumps({"status": "success", "message": f"Booking confirmed for {date} at {time}"})
        else:
            return json.dumps({"status": "error", "message": "Booking cannot be confirmed or does not exist"})
        
    def lookup_user(self, name, email, phone_number):
        self.db.execute('''SELECT user_id FROM users WHERE name=? AND email=? AND phone_number=?''',
                        (name, email, phone_number))
        result = self.db.fetchone()
        if result:
            return json.dumps({"status": "success", "user_id": result[0]})
        else:
            return json.dumps({"status": "error", "message": "User not found"})

    def select_appointment_date(self):
        available_dates = [date for date, slots in self.available_slots.items() if any(slots.values())]
        return json.dumps({"available_dates": available_dates})

    def select_time_slot(self, date):
        available_time_slots = self.get_available_time_slots(date)
        if available_time_slots:
            return json.dumps({"available_time_slots": available_time_slots})
        else:
            return json.dumps({"status": "error", "message": "No available slots for the selected date."})

    def change_booking_date(self, booking_id, new_date):
        self.db.execute('''SELECT date, time FROM bookings WHERE booking_id=?''', (booking_id,))
        result = self.db.fetchone()
        if result:
            old_date, old_time = result
            available_time_slots = self.get_available_time_slots(new_date)
            if available_time_slots:
                self.db.execute('''UPDATE bookings SET date=? WHERE booking_id=?''', (new_date, booking_id))
                self.db.commit()
                if old_date in self.available_slots and old_time in self.available_slots[old_date]:
                    self.available_slots[old_date][old_time] = True
                return json.dumps({
                    "status": "success", 
                    "message": f"Booking date changed to {new_date}",
                    "available_time_slots": available_time_slots
                })
            else:
                return json.dumps({"status": "error", "message": "No available time slots for the selected date"})
        else:
            return json.dumps({"status": "error", "message": "Booking not found"})

    def change_booking_time(self, booking_id, new_time):
        self.db.execute('''SELECT date, time FROM bookings WHERE booking_id=?''', (booking_id,))
        result = self.db.fetchone()
        if result:
            date, old_time = result
            if date in self.available_slots and new_time in self.available_slots[date] and self.available_slots[date][new_time]:
                self.db.execute('''UPDATE bookings SET time=? WHERE booking_id=?''', (new_time, booking_id))
                self.db.commit()
                self.available_slots[date][old_time] = True
                self.available_slots[date][new_time] = False
                return json.dumps({"status": "success", "message": f"Booking time changed to {new_time}"})
            else:
                return json.dumps({"status": "error", "message": "Selected time slot is not available"})
        else:
            return json.dumps({"status": "error", "message": "Booking not found"})