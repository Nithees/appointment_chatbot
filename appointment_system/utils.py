import re

def validate_user_data(user_data):
    errors = {}
    if 'name' in user_data:
        name = user_data['name']
        if not name.replace(" ", "").isalpha():
            errors['name'] = 'Name must contain only alphabets and spaces.'
    
    if 'email' in user_data:
        email = user_data['email']
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            errors['email'] = 'Invalid email address.'
    
    if 'phone_number' in user_data:
        phone_number = user_data['phone_number']
        if not re.match(r'^[0-9]{10}$', phone_number):
            errors['phone_number'] = 'Phone number must be exactly 10 digits.'
    
    if 'age' in user_data:
        try:
            age = int(user_data['age'])
        except ValueError:
            errors['age'] = 'Age must be a valid number.'
        else:
            if not (0 < age < 100):
                errors['age'] = 'Age must be between 1 and 99.'
    
    return errors
