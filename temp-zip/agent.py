# agent.py
import asyncio
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentServer, JobContext
from livekit.agents.voice import AgentSession, Agent
# IMPORTANT: import RoomOptions from here
from livekit.agents.voice import room_io
from livekit.plugins import openai, noise_cancellation

load_dotenv()

class SimpleAssistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are a friendly, helpful AI assistant.
Keep responses concise, natural, and engaging.
Use casual language like you're talking to a friend."""
        )

server = AgentServer()

@server.rtc_session()
async def entrypoint(ctx: JobContext):
    # Connect to room
    await ctx.connect()

    # Create realtime session with OpenAI
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="coral",           # alternatives: "nova", "alloy", "shimmer", "echo", "fable"
            temperature=0.8,
        )
    )

    # Start the session with proper room configuration
    await session.start(
        room=ctx.room,
        agent=SimpleAssistant(),
        room_options=room_io.RoomOptions(                   # ← correct location
            audio_input=room_io.AudioInputOptions(          # ← correct location
                noise_cancellation=lambda p: (
                    noise_cancellation.BVCTelephony()
                    if p.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                )
            )
        )
    )

    print(f"Voice agent started in room {ctx.room.name} ({ctx.room.sid})")

    # Auto-greet
    await session.generate_reply(
        instructions="Greet the user warmly in English and ask how you can help today."
    )

    print("Voice agent ready! Start speaking...")

if __name__ == "__main__":
    agents.cli.run_app(server)