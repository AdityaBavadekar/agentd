import asyncio

from .agent import AgentD

agentd = AgentD()
USER_ID = AgentD.generate_user_id()


def simple_callback(event, eventType: AgentD.EventType):
    print("@@@@@@ [CALLBACK] EVENT @@@@@@")
    if eventType == AgentD.EventType.USER_INPUT_REQUEST:
        user_input_specs: dict = event
        print(
            f"Agent '{user_input_specs.get('agent_name', 'Unknown')}' is requesting your input:\n"
            f"{user_input_specs.get('description', '')}\n"
        )


async def main():
    new_session = await agentd.new_sesion(USER_ID)

    while True:
        try:
            new_message = input("[>>] Enter a message (or type 'exit'): ")
            if new_message.lower() == "exit":
                print("Exiting AgentD...")
                break
            await agentd.continue_session(
                message=new_message,
                session=new_session,
                callback=simple_callback,
            )
        except KeyboardInterrupt:
            print("Exiting AgentD...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


asyncio.run(main())
