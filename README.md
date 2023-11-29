# Teachable AutoGen Slack Bot

## Introduction

This Slack bot, integrating Microsoft AutoGen, creates a unique AI agent that you can teach directly from Slack. It leverages the power of OpenAI's GPT-4 for generating responses and facilitates interactive learning through user feedback. Whether you need assistance with copywriting tasks or just a smart conversation partner, this bot is designed to adapt and learn from its interactions with users.

## Features

- **Interactive Learning**: Users can directly teach the AI agent in Slack, enhancing its knowledge and response quality over time.
- **Customizable Agent**: Tailored to specialize in direct response copywriting, drawing inspiration from legends like Clayton Makepeace and Gary Halbert.
- **Responsive Interaction**: Engages in Slack threads, understanding context and maintaining continuity.
- **Command-Based Actions**: Includes special commands like `-learn`, `-reset`, and `-exit` for specific interactions.

## Installation

1. **Clone the Repository**: First, clone this repository to your local machine.
2. **Install Dependencies**: Install all the required dependencies listed in `requirements.txt`. Use the command:
   ```
   pip install -r requirements.txt
   ```
3. **Set Up Environment Variables**: Create a `.env` file in your project root with the following keys:
   ```
   SLACK_BOT_TOKEN=your_slack_bot_token
   SLACK_APP_TOKEN=your_slack_app_token
   SLACK_BOT_USER_ID=your_slack_bot_user_id
   ```

## Usage

To start and interact with the bot:

1. **Run the Bot**: Execute the main Python script.

   ```bash
   python app.py
   ```
2. **Interact in Slack**: Mention the bot in any channel or direct message to start an interaction. Use the thread to continue the conversation.
3. **Learn and Reset**:

   - Use `-learn` in a thread with the bot to have it learn from the past conversation. This enhances the bot's understanding and response quality over time.
   - Use `-reset` to reset the chat history. This is useful if you want to start a fresh conversation without previous context.
   - Use `-exit` to close the database connection for the current chat. This is helpful when ending a session or if you want to ensure data is saved properly.

## Configuration

To properly configure your Slack Teachable Bot, follow these steps:

* **Environment Variables**:

  - Create a `.env` file in your project root (you can use `.env.example` as a template).
  - Add the following keys with your respective values:
    ```
    SLACK_BOT_TOKEN=your_slack_bot_token
    SLACK_APP_TOKEN=your_slack_app_token
    SLACK_BOT_USER_ID=your_slack_bot_user_id
    ```
  - To do this via the terminal, you can copy the `.env.example` file:
    ```
    cp .env.example .env
    ```
  - Then edit the `.env` file to insert your specific values.
* **OpenAI Configuration List**:

  - Similarly, create an `OAI_CONFIG_LIST` file (you can use `OAI_CONFIG_LIST.example` as a reference).
  - This file should contain the configuration details for various GPT models and your OpenAI API key.
  - Copy the `OAI_CONFIG_LIST.example` to `OAI_CONFIG_LIST` using the terminal:
    ```
    cp OAI_CONFIG_LIST.example OAI_CONFIG_LIST
    ```
  - Edit the `OAI_CONFIG_LIST` file, replacing `YOUR_OPENAI_API_KEY` with your actual OpenAI API key.

Ensure that the `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `SLACK_BOT_USER_ID`, and the OpenAI API keys are correctly set in these files for the bot to function properly.

## Slack Setup

1. Create a Slack App: Go to the Slack API website and create a new Slack app. Provide a name and select the workspace where you want to install the app.
2. OAuth & Permissions: In the app settings, navigate to the "OAuth & Permissions" section. Add the following scopes under the "Bot Token Scopes" section:

   * app_mentions:read - to listen for app mentions in channels
   * channels:history - to access channel history for inactivity tracking
   * chat:write - to send messages on behalf of the app
   * chat:write.customize - to customize messages sent by the app
   * chat:write.public - to send messages to public channels
   * groups:history - to access group history for inactivity tracking
   * im:history - to access direct message history for inactivity tracking
   * mpim:history - to access multi-party direct message history for inactivity tracking
   * reactions:write - to add reactions to messages
3. Event Subscriptions: Enable the Event Subscriptions feature in the app settings. Set the "Request URL" to the publicly accessible URL where your app is hosted. Subscribe to the following bot events:

   * app_mention - to listen for app mentions in channels
4. Socket Mode: Enable Socket Mode in the app settings. Generate and note down the "App-Level Token" for later use.
5. Install App to Workspace: In the app settings, navigate to the "Install App" section. Click on the "Install to Workspace" button to install the app to your desired workspace.
6. Environment Variables: Set the following environment variables in your deployment environment or in a .env file:

   * SLACK_BOT_TOKEN - set it to the Bot Token generated for your app
   * SLACK_APP_TOKEN - set it to the App-Level Token generated for Socket Mode
   * SLACK_BOT_USER_ID - set it to the user ID of the bot user associated with your app

Once you have completed these steps, your app should be set up in Slack and ready to work with the provided code.

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcomed.

## License

This project is licensed under the [MIT License](LICENSE.md) - see the LICENSE.md file for details.
