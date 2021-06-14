# Game APIs

- Install the requirements
- run info: `python game_spi/wsgi.py`
- Server link: http://localhost:7000

## Endpoints

- Admin Page: http://localhost:7000/admin
    - Admin page creds: `admin@example.com/admin`
- User:
    - `/login`
    - `/register`
    - `/user-token-refresh`
    - `/user-roles`
    - `/user-roles-assign`
    - `/fresh-login`
- Game: (Make Sure to use the specific method)
    - `/games` - List of games and applied filters
    - `/game/<id>` - Detail of specific game
    - `/game` - Create the game
