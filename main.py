import streamlit as st
from appointment_system import Database, AppointmentTools, Chatbot, validate_user_data
import json

# Initialize components
db = Database()
appointment_tools = AppointmentTools(db)

tools = [
    {
        "name": "select_appointment_date",
        "description": "Lets the user select a date for the appointment.",
        "input_schema": {
            "type": "object",
            "properties": {

            }
        }
    },
    {
        "name": "select_time_slot",
        "description": "Lets the user select a time slot from available options for the chosen date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The selected appointment date."
                },
                "available_time_slots": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Available time slots for the selected date."
                }
            }
        }
    },    {
        "name": "create_booking",
        "description": "Create a booking for a specific date and time",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The date for the booking (format: YYYY-MM-DD)",
                },
                "time": {
                    "type": "string",
                    "description": "The time for the booking (format: HH:MM)",
                },
            },
            "required": ["date", "time"],
        },
    },
    {
        "name": "cancel_booking",
        "description": "Cancel a booking using the booking ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "integer",
                    "description": "The ID of the booking to be cancelled",
                },
            },
            "required": ["booking_id"],
        },
    },
    {
        "name": "confirm_booking",
        "description": "Confirm a booking after creating it",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "integer",
                    "description": "The ID of the booking to be confirmed",
                },
                "date": {
                    "type": "string",
                    "description": "The date for the booking (format: YYYY-MM-DD)",
                },
                "time": {
                    "type": "string",
                    "description": "The time for the booking (format: HH:MM)",
                },
            },
            "required": ["booking_id", "date", "time"],
        },
    },
    {
        "name": "lookup_user",
        "description": "Lookup a user based on provided details",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the user",
                },
                "email": {
                    "type": "string",
                    "description": "The email of the user",
                },
                "phone_number": {
                    "type": "string",
                    "description": "The phone number of the user",
                },
            },
            "required": ["name", "email", "phone_number"],
        },
    },
    {
        "name": "change_booking_date",
        "description": "Change the date of an existing booking",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "integer",
                    "description": "The ID of the booking to be changed",
                },
                "new_date": {
                    "type": "string",
                    "description": "The new date for the booking (format: YYYY-MM-DD)",
                },
            },
            "required": ["booking_id", "new_date"],
        },
    },
    {
        "name": "change_booking_time",
        "description": "Change the time of an existing booking",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "integer",
                    "description": "The ID of the booking to be changed",
                },
                "new_time": {
                    "type": "string",
                    "description": "The new time for the booking (format: HH:MM)",
                },
            },
            "required": ["booking_id", "new_time"],
        },
    }
]


chatbot = Chatbot(
    api_key="",
    model_name="claude-3-5-sonnet-20240620",
    tools=tools,
    db=db,
    appointment_tools=appointment_tools
)

# Streamlit UI
st.title("Appointment Booking Chatbot")

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "conversation_started" not in st.session_state:
    st.session_state["conversation_started"] = False

if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

if "user_data" not in st.session_state:
    st.session_state["user_data"] = {"name": "", "email": "", "phone_number": "", "age": 18}

# Collect user data
if st.session_state["user_id"] is None and not st.session_state["form_submitted"]:
    with st.form(key='user_form'):
        st.subheader("Please enter your details to start:")
        name = st.text_input("Name", value=st.session_state["user_data"]["name"])
        email = st.text_input("Email", value=st.session_state["user_data"]["email"])
        phone_number = st.text_input("Phone Number", value=st.session_state["user_data"]["phone_number"])
        age = st.number_input("Age", min_value=1, max_value=99, value=st.session_state["user_data"]["age"])
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            user_data = {
                'name': name,
                'email': email,
                'phone_number': phone_number,
                'age': age
            }
            errors = validate_user_data(user_data)
            if errors:
                for field, error in errors.items():
                    st.error(f"{field.capitalize()}: {error}")
                # Update session state with valid inputs
                for field in user_data:
                    if field not in errors:
                        st.session_state["user_data"][field] = user_data[field]
            else:
                user_id_result = json.loads(appointment_tools.lookup_user(name, email, phone_number))
                if user_id_result['status'] == 'success':
                    st.session_state["user_id"] = user_id_result['user_id']
                    st.success(f"User found with user_id {st.session_state['user_id']}.")
                else:
                    db.execute('''INSERT INTO users (name, email, phone_number, age, appointment_status)
                                VALUES (?, ?, ?, ?, ?)''', 
                            (name, email, phone_number, age, 'available'))
                    db.commit()
                    st.session_state["user_id"] = db.cursor.lastrowid
                    st.success(f"User {name} successfully registered with user_id {st.session_state['user_id']}.")
                st.session_state["form_submitted"] = True
                st.rerun()

# Display chat history and chatbot UI
if st.session_state["user_id"] is not None and st.session_state["form_submitted"]:
    # Clear the screen and display chatbot in full screen
    st.empty()
    
    # Display chat history
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not st.session_state["conversation_started"]:
        with st.chat_message("assistant"):
            st.markdown("Hello, welcome to the appointment booking system! How can I assist you today?")
        st.session_state["conversation_started"] = True
    
    if prompt := st.chat_input("You:"):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = chatbot.chat(prompt, st.session_state["user_id"], st.session_state["messages"])
        with st.chat_message("assistant"):
            try:
                st.markdown(response)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.rerun()
else:
    st.info("Please fill out your details to start using the chatbot.")
