# translate
A (almost) ready to go standalone [maubot](https://github.com/maubot/maubot) to translate words using Google Translate. This is based-on/forked-from https://github.com/maubot/translate ❤️

In comparison too the upstream repo this bot has a auto-translation based on regex match of the room name.

**WARNING**: this bot sends every message to the google translation API. You chat will not be secret anymore in spite of e2ee enabled in your chat room.


- [translate](#translate)
- [Setup](#setup)
  - [requirements](#requirements)
  - [Install](#install)
  - [Enable end 2 end encription](#enable-end-2-end-encription)
- [Start](#start)
- [Usage](#usage)
  - [Command mode](#command-mode)
  - [Auto mode](#auto-mode)

# Setup

## requirements

* A running matrix server with a user account for the bot

## Install

`git clone git@github.com:motey/matrix-translate-bot.git` 

`cd translate`

`docker-compose up`

wait until you get the message `Please modify the config file to your liking and restart the container.` Press `ctrl`+`c` to stop the compose stack.

edit `./_state/config/config.yaml` to your configuration. See next chapter to enable encription

## Enable end 2 end encription

To enable e2ee for your bot you need to set `user.credentials.access_token` and `user.credentials.device_id` in your `config.yaml`.  
The easist way for me to obtain these was via curl:


```bash
curl -X POST --header 'Content-Type: application/json' -d '{
    "identifier": { "type": "m.id.user", "user": "USERNAME" },
    "password": "PASSWORD",
    "type": "m.login.password"
}' 'https://MATRIXHOSTNAME/_matrix/client/r0/login'
```
Replace `USERNAME` with your bot account name, `PASSWORD` with its password and `MATRIXHOSTNAME` with the domain of your matrix server.  
You will get a reply containing a device id and a access token. Use these to fill out `user.credentials`in your `config.yaml`.  

# Start

`docker-compose up -d`

Thats it...


# Usage

## Command mode

After inviting the bot to your room, simply use the `!translate` command:

    !translate en ru Hello world.
    
which results in

    Translate Bot:
    > rubo77
    > !translate en ru Hello world.
    Привет, мир.

You can also use the alias `tr`:

    !tr en ru Hello world.

The first parameter (source language) can be set to `auto` or omitted entirely
to let Google Translate detect the source language. Additionally, you can reply
to a message with `!tr <from> <to>` (no text) to translate the message you
replied to.


## Auto mode

Configure `plugin_config.auto_translate` in `config.yaml` to match the room(s) you want auto-tranlate to be enabled. You can also enter a regex match pattern to enable auto-translate to a whole class of rooms or certain domains, or whatever you need.  
You still need to invite the bot manualy into the room(s).  
After that the bot will try to detect the language of every message (based on the enabled languages in `plugin_config.auto_translate`) and will translate it to every other language configured in `plugin_config.auto_translate`