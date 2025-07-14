# API Documentation

## General Information
- **Base URL**: `https://roleplayverse.live`
- **Authentication**: Required for most endpoints (`Bearer Token`)
- **Content Type**: `application/json`

---

## Endpoints

### 1. User Registration
- **URL**: `/api/user/register/`
- **Method**: `POST`
- **Authentication**: Not Required
- **Description**: Registers a new user.

#### Request Body:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

### 2. User Login(JWT)
- **URL**: `/api/token/`
- **Method**: `POST`
- **Authentication**: Not Required
- **Description**: Get JWT token for authentication.

#### Request Body:
```json
{
  "username": "string",
  //"email": "string",
  "password": "string",
}
```

### 3. Posts
- **URL**: `/api/feed/`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get posts made by users.

#### Request Body:

### 4. Create Post
- **URL**: `/post/new`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: create a post.

#### Request Body:
```json
{
    "body" : "string",
    "image" : "image file object",
}
```

### 5. Delete Post
- **URL**: `/posts/<int:id>`
- **Method**: `DELETE`
- **Authentication**: Required
- **Description**: delete a post.

#### Request Body:

### 6. Get Post
- **URL**: `/posts/<int:id>`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: get a post.

#### Request Body:

### 7. Feed
- **URL**: `/feed/`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get posts,announcements,battles shown on the feed.

#### Request Body:

### 8. Comments
- **URL**: `/post/<int:post_id>/comments`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get comments for a post.

#### Request Body:


### 9. Comments
- **URL**: `/post/comment/new/<int:post_id>`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Create a comment for a post.

#### Request Body:
```json
{
    "body" : "string",
}
```

### 10. React to Post
- **URL**: `/post/react/<int:post_id>`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: add a reaction to a post.

#### Request Body:

### 11. React to Comment
- **URL**: `/comment/react/<int:comment_id>`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: add a reaction to a comment.

#### Request Body:

### 12. Notifications
- **URL**: `/notifications/all`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get notifications for a player.

#### Request Body:

### 13. Notifications
- **URL**: `/notifications/mark_as_read/all`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Mark all of a player's notifications as read.

#### Request Body:

### 13. Notifications
- **URL**: `/notifications/mark_as_read/all`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Mark all of a player's notifications as read.

#### Request Body:

### 14. Notifications

- **URL**: `/notifications/mark_as_read/all`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Mark all of a player's notifications as read.

#### Request Body:

### 15. Battles
- **URL**: `/battles/filter/<int:filter_num>`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Get Battles in a particular state(1:not_started, 2:waiting_refree, 3:ongoing, 4:finished).

#### Request Body:

### 16. Textpads
- **URL**: `/battles/textpads/get/<int:battle_id>`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get textpads sent for particular battle.

#### Request Body:

### 17. Textpads
- **URL**: `/battles/textpads/send/<int:battle_id`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: send a textpad in a battle.

#### Request Body:
```json 
{
    "text" : "string",
    "hidden_action" : "string optional" 
}
```

### 18. Textpads
- **URL**: `/battles/textpads/react/<int:textpad_id>`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: React to a textpad in a battle.

#### Request Body:
```json 
{
    "reaction" : "string, choice in [😂😱👏👍👎]", 
}
```

### 19. Textpads
- **URL**: `/battles/textpads/<int:textpad_id>/comments/add`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Add a  comment to a textpad.

#### Request Body:
```json 
{
    "text" : "string",
    "parent_id" : "integer | this is to manage comment replies, Null if it is not a reply" 
}
```

### 20. Textpads
- **URL**: `/battles/textpads/<int:textpad_id>/comments/`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get  comments for a textpad.

#### Request Body:

### 21. Solo battle
- **URL**: `/battles/solo/init`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Initialize a solo battle.

#### Request Body:
```json
{
    "character" : "string"
}
```
### 22. Solo battle
- **URL**: `/battles/solo/action`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Perform an action in a solo battle.

#### Request Body:
```json
{
    "action" : "string | Name of the action performed(Attack, Defence...)"
}
```

### 23. Characters
- **URL**: `/characters/all`
- **Method**: `GET`
- **Authentication**: Not Required
- **Description**: get all naruto characters.

#### Request Body:


### 24. Battle
- **URL**: `/battles/request`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Make a battle request.

#### Request Body:
```json
{
    "character" : "string | Name of a naruto character",
    "type" : "string | choice in [stake, friendly]"
}
```

### 25. Battle
- **URL**: `/battles/requests`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: get all battle requests.

#### Request Body:

### 26. Battle
- **URL**: `/battles/accept/<int:request_id>`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Accept a battle request.

#### Request Body:
```json
{
    "character" : "string | Name of a naruto character",
}
```




















