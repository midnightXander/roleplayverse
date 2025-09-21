# API Documentation

## General Information
- **How it works**: The chat functionality relies on websocket connection between two users. it 
- **Base Websocket URL**: `wss://https://roleplayverse.live/ws/`
- **Authentication**: Required for all (`Bearer Token`)
- **Content Type**: `application/json`

---

## Private Messages
- **URL**: `chat/private/room1/` 
- **Sending** : trigger the send event with the request body once connected to websocket
- **fetching** : fetch messages via : https://roleplayverse.live/api/chats/private/messages/<int:receiver_id>
  ### Send Request body : 
  ```json
  {
    "content" : "message content | string",
    "sender": "sender_name | string",
    "receiver": "receiver_name | string",
    "file": "file | base64File | optional", 
    "fileName":"file name| string | optional"
    }

## Family Messages
- **URL**: `chat/group/'+ family_name + /` 
- **Sending** : trigger the send event with the request body once connected to websocket
- **fetching** : chats/family/messages/<str:family_name>
  ### Send Request body : 
  ```json
  {
    "content" : "message content | string",
    "sender": "sender_name | string",
    "receiver": "receiver_name | string",
    "file": "file | base64File | optional", 
    "fileName":"file name| string | optional"
    }


