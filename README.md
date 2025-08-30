# Discord Ticket Bot

A feature-rich Discord ticket management bot with visual status indicators, staff claiming system, and comprehensive ticket management capabilities.

## Features

- **Ticket System**: Create private support channels with customizable categories
- **Status Tracking**: Monitor ticket status with visual indicators (Open, In Progress, On Hold, Closed)
- **Staff Management**: Allow staff members to claim tickets and track responsibility
- **Transcript Generation**: Automatically generate and send conversation transcripts when closing tickets
- **Persistent Data**: Save ticket information and settings across bot restarts
- **Customizable Setup**: Configure ticket messages, button names, and categories
- **Permission Controls**: Restrict ticket actions to appropriate users

## Status Indicators

- 🟢 **Open**: Ticket created, awaiting staff response
- 🟡 **In Progress**: Staff member actively handling the ticket
- 🟠 **On Hold**: Ticket temporarily paused
- 🔴 **Closed**: Ticket resolved and closed

## Installation

1. Clone this repository
2. Install required dependencies: `pip install -r requirements.txt`
3. Configure your bot token in the main script
4. Invite the bot to your server with appropriate permissions
5. Run the bot: `python bot.py`

## Usage

- Use `/setup` to configure the ticket system (admin only)
- Click the ticket button to create a new support channel
- Use `Claim Ticket` to take ownership of a ticket
- Use `/close` or the close button to resolve and archive tickets
- Use `/status` to check current ticket status
- Use `/setstatus` to update ticket status (staff only)

## Permissions

The bot requires the following permissions:
- Manage Channels
- Manage Messages
- View Channels
- Send Messages
- Read Message History

## Support

For issues or feature requests, please open an issue on the GitHub repository.
