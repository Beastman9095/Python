## Installation

!! USE Python 3.11

First of all, initialize a MongoDB database on their website as you will need one. You only need a connection URL so just an account + database without any collections would suffice. Secondly, input your token and mongo url in the .env file. Don't forget to edit metadata.yml up to your preferences. After you're done with all of these you should be aware that all permissions are handled manually on your end. You can disable usages for commands by specific people/role or allow for specific people/role through discord server settings, integrations.

You can run the bot with

```
python bot.py
```

## Main Features

### Announcements (ext.commands.announce.py)

I have configured announcements to be a little then their predecessor this time around. It is based on an unreleased version of my Ham5teak Bot 3.0 which had been used for a short time in our discord server. The idea behind this new version is to allow creating announcements without sending any messages to the channel itself.

    Run the following command to use the feature: /announce
    The command has two optional arguments, anyone or any role you want to mention and optional attachment

This new system will move forward by sending a modal to the player in which it takes the inputs of the user. This system allows for a cleaner and relatively simpler approach to our previous system.

Reactions have been replaced with components this time around for a better ease of use. This prevents any unwanted reactions to be added while still allowing players to express their feelings through emojis.

This system utilizes modal_worker, component_worker to create the embeds and handle reactions which I will be explaining later on.

### Suggestions (ext.commands.suggest.py)

Suggestions use the same modal_worker, component_worker and embedding technique as announcements. The only true difference is that suggestions don't have a "notes" option and it uses different emojis compared to the announcements.

    Run the following command to use the feature: /suggestion

Accepted/Rejected/Demanded Suggestions have been ditched due to unnecessity and low demand.

### Polls (ext.commands.poll.py)

Polls use the same modal_worker but it is the only true exception out of these three. Polls follow a special regex to get input options. I had to find some way to add options to a message without causing a hassle to the user and I used a regex check in the "options" field of modal_worker to do this.
`Regex: /(-(.+)\n)+-(.+)/`

    Run the following command to use the feature: /poll
    The command has a single description optional argument, describe the poll further in the field if you would like to.

### Edit Announcement (ext.context_menu.edit_announcement.py)

I used a similar modal strategy like the commands above for this particular feature but it does not need to use the modal_worker as its rather straightforward and goes against the working method of modal_worker as it only creates, it doesn't edit.

    Right Click/Hold a message to use the feature, select "Apps" and "Edit Announcement"

## Utilities

### Modal Worker (ext.listeners.modal_worker.py)

Modal worker is a modal submit listener that is always running on the bot's background. It essentially gets the values of submitted input fields from the modal and processes them to create an embed. The embed is thereby sent to the modal context as an interaction response. I used some special cases for attachments and I will detail how they work in a later part.

### Component Worker (ext.listeners.component_worker.py)

Component Worker is a component submit listener that is also always running in the bot's background.

Components work to add/remove reactions/votes using a MongoDB database thanks to the library beanie. Each embedded message (announcement/poll/suggestion) is stored on the database with their unique id. Every database document has a counts array which holds count of the users who have clicked that particular emoji. Following it is a user_ids array that does the opposite to make sure all are in place and it serves as a check to see if the user has chosen. A user can only choose a single emoji out of the options for all instances.

### Databases

I have used a MongoDB database and the beanie library in this project to make it easier to configure, use. Instead of caching many variables I have used direct database calls.

### Attachments

Attachments are utilized only on two occasions on the bot. /announce and the edit_announcement context menu. Announcements use the save, delete and get method of my Attachment (common.utils.attachment.py) class avoiding taking in an unnecessary attachment argument for each function. Edit Announcements finally supports embedded images unlike the previous iteration.
