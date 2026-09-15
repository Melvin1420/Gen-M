- Has a  history of comments/updates
- Has a linked chat threads (see TicketMessage below)

### TicketMessage
- Belongs to one Ticket
- Sent by either the requester (Employee/Manager) or an assigned Agent
- Has: message text, sender, timestamp
- Ordered chronologically — this is the single communication channel for
  that ticket, both sides read/write the same thread

## Communication
- Once a ticket is created, a chat thread is available on that ticket 
- Both the requester and any Agent assigned to (or working) that department's queue can post messages
- Messages are plain text for v1 — no file attachments yet
- This is a persisted, refresh-based chat (not real-time/websocket) for v1; real-time delivery is a future enhancement