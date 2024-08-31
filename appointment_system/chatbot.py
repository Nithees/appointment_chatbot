import json
import anthropic

class Chatbot:
    def __init__(self, api_key, model_name, tools, db, appointment_tools):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name
        self.tools = tools
        self.db = db
        self.appointment_tools = appointment_tools

    def process_tool_call(self, tool_name, tool_input, user_id=None):
        if tool_name == "create_booking":
            return self.appointment_tools.create_booking(tool_input['date'], tool_input['time'], user_id)
        elif tool_name == "cancel_booking":
            return self.appointment_tools.cancel_booking(tool_input['booking_id'])
        elif tool_name == "confirm_booking":
            return self.appointment_tools.confirm_booking(tool_input['booking_id'], tool_input['date'], tool_input['time'])
        elif tool_name == "lookup_user":
            return self.appointment_tools.lookup_user(tool_input['name'], tool_input['email'], tool_input['phone_number'])
        elif tool_name == "select_appointment_date":
            return self.appointment_tools.select_appointment_date()
        elif tool_name == "select_time_slot":
            return self.appointment_tools.select_time_slot(tool_input['date'])
        elif tool_name == "change_booking_date":
            return self.appointment_tools.change_booking_date(tool_input['booking_id'], tool_input['new_date'])
        elif tool_name == "change_booking_time":
            return self.appointment_tools.change_booking_time(tool_input['booking_id'], tool_input['new_time'])

    def chat(self, user_message, user_id, messages):
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=1000,
            tools=self.tools,
            system="""You are an appointment booking chatbot. You can only assist users with tasks related to appointment bookings, such as selecting appointment dates, time slots, creating or canceling bookings, and confirming or changing appointments. 
            Start with a greeting, then ask for the user's preferred appointment date and then slots in respective selected dates. 
            For changing bookings, always ask for the new date first, then provide available time slots for that date. 
            If no slots are available for a date, inform the user and suggest they choose another date. 
            Always confirm the final booking details with the user before making any changes.
            If a user asks a question unrelated to appointment bookings, politely inform them that you can only assist with appointment-related queries and guide them to booking-related tasks.""",
            messages=messages
        )

        if response.stop_reason == "tool_use":

            messages.append({"role": "assistant", "content": response.content})

            tool_calls = response.content[1]
            tool_name = tool_calls.name
            tool_input = json.loads(json.dumps(tool_calls.input))
            tool_error = False

            try:
                tool_result = self.process_tool_call(tool_name, tool_input, user_id)
            except Exception as e:
                tool_result = json.dumps({"status": "error", "message": str(e)})
                tool_error = True

            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_calls.id,
                        "content": tool_result,
                        "is_error": tool_error
                    }
                ]
            })

            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1000,
                tools=self.tools,
                messages=messages
            )

        messages.append({"role": "assistant", "content": response.content[0].text})
        return response.content[0].text
