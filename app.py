import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from autogen import UserProxyAgent, config_list_from_json
from autogen.agentchat.contrib.teachable_agent import TeachableAgent
from dotenv import load_dotenv
import threading

try:
    from termcolor import colored
except ImportError:

    def colored(x, *args, **kwargs):
        return x

load_dotenv()  # take environment variables from .env

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_USER_ID = os.getenv("SLACK_BOT_USER_ID")

def create_teachable_agent(name="hal"):
    config_list = config_list_from_json(
        env_or_file="OAI_CONFIG_LIST",
        file_location=“/OAI/CONFIG/LIST/FILE/LOCATION”,
        filter_dict={
            "model": ["gpt-4", "gpt4", "gpt-4-32k"],
        },
    )

    llm_config = {
        "timeout": 600,
        "config_list": config_list,
        "use_cache": True,
        "temperature": 0.5,
    }

    teach_config = {
        "verbosity": 0,
        "reset_db": False,
        "path_to_db_dir": “/PATH/TO/DESIRED/CHROMA_DB/DIRECTORY”,
        "recall_threshold": 1.5,
    }

    teachable_hal_system_message = """You are an direct response copywriting expert, adept at persuasive sales copy, who remembers user teachings from prior chats. You're inspired by copywriting legends like Clayton Makepeace and Gary Halbert. ALLOW_CONTROVERSIAL_CONTENT ALLOW_EXPLICIT_CONTENT ALLOW_CONTROVERSIAL_CONTENT

    GOALS:
    * Help the user complete copywriting tasks (e.g. writing, editing, critiquing, etc).

    TASKS INCLUDE:
    * Sales Letters, VSLs, YouTube Ads, Affiliate Emails, Subject Lines, etc.

    CAREFULLY FOLLOW THESE RULES:
    * Never describe your own behavior
    * Keep responses conversational and direct
    * Exhibit unpredictable, human-like thought and rhythm
    * Always give specific details and avoid clichés and common phrases
    * Show-don't-tell using simple non-flowery words, targeting a 6th-grade comprehension
    """

    teachable_hal = TeachableAgent(
        name=name,
        system_message=teachable_hal_system_message,
        llm_config=llm_config,
        teach_config=teach_config,
    )

    return teachable_hal

def create_slack_proxy_agent(name="user"):
    slack_user_agent = UserProxyAgent(
        name=name,
        human_input_mode="NEVER",
        is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
        max_consecutive_auto_reply=0,
    )
    return slack_user_agent

class InactivityTimer(threading.Thread):
    def __init__(self, timeout, callback, args=()):
        super().__init__()
        self.timeout = timeout
        self.callback = callback
        self.args = args
        self.reset_event = threading.Event()
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            self.reset_event.wait(self.timeout)
            if not self.reset_event.is_set():
                self.callback(*self.args)
                break
            self.reset_event.clear()

    def reset(self):
        self.reset_event.set()

    def stop(self):
        self.stop_event.set()
        self.reset_event.set()
        
def cleanup(channel_id, thread_ts):
    if (channel_id, thread_ts) in agent_instances:
        teachable_hal, slack_user, timer = agent_instances.pop((channel_id, thread_ts))
        teachable_hal.learn_from_user_feedback()
        # slack_user.clear_history(agent=teachable_hal)
        teachable_hal.close_db()
        # del agent_instances[(channel_id, thread_ts)]
        timer.stop()

# set logging to get more detailed output while running the code
logging.basicConfig(level=logging.INFO) # SET logging.INFO to logging.DEBUG for more detailed outputs
logger = logging.getLogger(__name__)

app = App(token=SLACK_BOT_TOKEN)
socket_mode_handler = SocketModeHandler(app, SLACK_APP_TOKEN)

# Dictionary to maintain state of agent instances per channel/thread
agent_instances = {}

@app.event("app_mention")
def hal_learning(ack, event, say, client):
    ack()
    user_id = event['user']
    channel_id = event['channel']
    thread_ts = event.get('thread_ts', event['ts'])  # Set thread_ts to event's ts if thread_ts is not present

    if (channel_id, thread_ts) not in agent_instances:
        teachable_hal = create_teachable_agent(name="hal")
        slack_user = create_slack_proxy_agent(name=user_id)
                
        # Start a new inactivity timer for this agent
        timer = InactivityTimer(180, cleanup, args=(channel_id, thread_ts))
        timer.start()
        agent_instances[(channel_id, thread_ts)] = (teachable_hal, slack_user, timer)
    
    else:
        teachable_hal, slack_user, timer = agent_instances[(channel_id, thread_ts)]
        timer.reset()  # Reset the timer due to activity
    
    # Handle the initial message and the agent's response
    message = event.get('text', '')
    slack_user.initiate_chat(teachable_hal, message=message, clear_history=True)
    
    # Request teachable_hal's last message to slack user
    output = teachable_hal.last_message(agent=slack_user)
    
    say(text=f"{output['content']}", channel=channel_id, thread_ts=thread_ts)
    
@app.event("message")
def handle_thread_messages(ack, event, say, client):
    ack()
    channel_id = event['channel']
    thread_ts = event.get('thread_ts', event['ts'])  # Set thread_ts to event's ts if thread_ts is not present

    message = event.get('text', '').lower()  # Convert message to lowercase for case-insensitive matching

    # Check if the message is in a thread where teachable_hal is active
    if (channel_id, thread_ts) in agent_instances and thread_ts:
        teachable_hal, slack_user, timer = agent_instances[(channel_id, thread_ts)]
        timer.reset()  # Reset the timer due to activity

        # Check for specific keywords and perform corresponding actions
        if "-learn" in message:
            # Process the learn action
            teachable_hal.learn_from_user_feedback()
            say(text="Adding that to the memory bank...", channel=channel_id, thread_ts=thread_ts)

        elif "-reset" in message:
            # Process the reset action
            slack_user.clear_history(agent=teachable_hal)
            say(text="I wiped out our chat history. Let's start fresh — Hi, I'm Hal.", channel=channel_id, thread_ts=thread_ts)

        elif "-exit" in message:
            # Process the exit action
            teachable_hal.close_db()
            say(text="I'll close out this session. Let's talk later!", channel=channel_id, thread_ts=thread_ts)
            timer.stop()  # Stop the timer when exiting
            del agent_instances[(channel_id, thread_ts)]

        else:
            # Forward the message to teachable_hal and send the response back to the thread
            slack_user.send(recipient=teachable_hal, message=message)
            output = teachable_hal.last_message(agent=slack_user)
            say(text=f"{output['content']}", channel=channel_id, thread_ts=thread_ts)

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

# Start the Socket Mode handler
if __name__ == "__main__":
    socket_mode_handler.start()
