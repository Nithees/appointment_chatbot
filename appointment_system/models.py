class User:
    def __init__(self, name, email, phone_number, age, appointment_status='available'):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.age = age
        self.appointment_status = appointment_status

class Booking:
    def __init__(self, user_id, date, time, status='pending'):
        self.user_id = user_id
        self.date = date
        self.time = time
        self.status = status