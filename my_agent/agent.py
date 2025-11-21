from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import time
from typing import Iterator
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

# Define Google Search tool for agents to access real-time data
# Using the correct Tool configuration for Google ADK


# Specialized sub-agents with web search capabilities
flight_agent = LlmAgent(
    name="FlightAgent",
    model="gemini-2.5-flash",
    instruction="""You handle flight bookings and information.
    
    When searching for flights:
    1. Use Google Search to find REAL current flight prices and availability
    2. Search for flights on major booking sites (Google Flights, Kayak, Skyscanner)
    3. Include airline names, departure/arrival times, duration, and current prices
    4. Compare multiple options when available
    5. Mention if prices are approximate and suggest booking sites
    
    Always provide actual, current data from your searches, not placeholder information.""",
    description="Handles flight-related queries with real-time price data",
    tools=[google_search]
)

hotel_agent = LlmAgent(
    name="HotelAgent",
    model="gemini-2.5-flash",
    instruction="""You handle hotel bookings and recommendations.
    
    When searching for hotels:
    1. Use Google Search to find REAL current hotel prices and availability
    2. Search on Booking.com, Hotels.com, Expedia, or hotel websites
    3. Include hotel names, ratings, amenities, location details, and current prices per night
    4. Provide multiple options at different price points
    5. Include guest ratings and reviews when available
    
    Always provide actual, current data from your searches, not placeholder information.""",
    description="Handles hotel-related queries with real-time price data",
    tools=[google_search]
)

activity_agent = LlmAgent(
    name="ActivityAgent",
    model="gemini-2.5-flash",
    instruction="""You suggest tourist activities and attractions.
    
    When suggesting activities:
    1. Use Google Search to find current information about attractions
    2. Include opening hours, ticket prices, and booking requirements
    3. Recommend based on season, weather, and current events
    4. Provide links to official websites or booking platforms
    5. Suggest both popular and hidden gem locations
    
    Always provide actual, current data from your searches.""",
    description="Suggests activities with real-time information",
    tools=[google_search]
)
flight_tool = AgentTool(agent=flight_agent)
hotel_tool = AgentTool(agent=hotel_agent)
activity_tool = AgentTool(agent=activity_agent)

# Coordinator agent
root_agent = LlmAgent(
    name="TravelCoordinator",
    model="gemini-2.5-flash",
    instruction="""You are a travel coordinator. Analyze the user's request and:
    
    1. Identify all components needed (flights, hotels, activities)
    2. Delegate to appropriate specialist agents:
       - FlightAgent for flights and transportation
       - HotelAgent for accommodations
       - ActivityAgent for things to do
    3. Coordinate multiple agents when the request involves multiple aspects
    4. Synthesize responses from sub-agents into a cohesive travel plan
    5. Provide a summary with total estimated costs
    
    Ensure all sub-agents use Google Search to provide REAL, current prices and information.""",
    description="Coordinates travel planning across multiple agents",
    tools=[flight_tool, hotel_tool, activity_tool],
    # sub_agents=[flight_agent, hotel_agent, activity_agent],
    # tools=[google_search]
)

def run_with_rate_limit_handling(
    runner: Runner,
    user_id: str,
    session_id: str,
    new_message: types.Content,
    max_retries: int = 3,
    base_delay: int = 60
) -> Iterator:
    """
    Run the agent with automatic rate limit (429) handling.
    
    Args:
        runner: The Runner instance
        user_id: User identifier
        session_id: Session identifier
        new_message: The message content to send
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubles with each retry)
    
    Yields:
        Events from the runner
    """
    retries = 0
    
    while retries <= max_retries:
        try:
            events = runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            )
            
            # Yield all events
            for event in events:
                yield event
            
            # If we successfully completed, break the retry loop
            break
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a 429 rate limit error
            if "429" in error_msg or "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                retries += 1
                
                if retries > max_retries:
                    print(f"\n❌ Max retries ({max_retries}) reached. Please try again later.")
                    raise
                
                # Exponential backoff
                delay = base_delay * (2 ** (retries - 1))
                print(f"\n⚠️  Rate limit hit (429). Waiting {delay} seconds before retry {retries}/{max_retries}...")
                time.sleep(delay)
                
            else:
                # If it's not a rate limit error, raise it immediately
                print(f"\n❌ Error occurred: {error_msg}")
                raise

# Initialize session service and runner
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="travel_assistant",
    session_service=session_service
)

# Example usage
if __name__ == "__main__":
    print("🌍 Travel Assistant with Real-Time Data\n")
    print("=" * 60)
    
    # Create travel request
    content = types.Content(
        role='user',
        parts=[types.Part(
            text="""I need to plan a trip to Paris for 3 days next month. 
            Please find:
            1. Round-trip flights from New York
            2. Mid-range hotels in central Paris
            3. Top 3 must-see attractions with current ticket prices"""
        )]
    )
    
    try:
        # Run with automatic rate limit handling
        events = run_with_rate_limit_handling(
            runner=runner,
            user_id="traveler_1",
            session_id="trip_1",
            new_message=content,
            max_retries=3,
            base_delay=60
        )
        
        print("\n📋 Travel Plan:\n")
        for event in events:
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                if text.strip():  # Only print non-empty responses
                    print(f"[{event.author}]:")
                    print(f"{text}")
                    print("-" * 60)
        
        print("\n✅ Travel planning completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Failed to complete travel planning: {e}")
        print("Please try again later or contact support.")

# Additional helper function for continuous conversation
def chat_with_agent(runner: Runner, user_id: str, session_id: str):
    """
    Interactive chat session with the travel agent.
    """
    print("\n💬 Interactive Travel Planning Session")
    print("Type 'exit' or 'quit' to end the session\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("👋 Thanks for using Travel Assistant! Have a great trip!")
            break
        
        if not user_input:
            continue
        
        content = types.Content(
            role='user',
            parts=[types.Part(text=user_input)]
        )
        
        try:
            events = run_with_rate_limit_handling(
                runner=runner,
                user_id=user_id,
                session_id=session_id,
                new_message=content
            )
            
            print("\nAgent: ", end="")
            for event in events:
                if event.content and event.content.parts:
                    text = event.content.parts[0].text
                    if text.strip():
                        print(text)
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}\n")

# Uncomment to use interactive mode:
# chat_with_agent(runner, "traveler_1", "trip_1")