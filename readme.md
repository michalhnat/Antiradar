# Antiradar

**Antiradar** is a Python-based project of mine designed to process and extract geographic information from unstructured text messages. Mostly from local Messenger groups informing about current police speed controls. It integrates various services, including message parsing, geolocation, and database management, to create structured location records.

### Features
* Message Parsing: Extracts towns, streets, and other geographic indicators from unstructured text using an LLM-powered parser.

* Geolocation: Uses the geopy library to convert town and street names into latitude and longitude coordinates. (Currently, I'm using the free Nominatim geolocator, which unfortunately isn't the best in its class.)

* Database Integration: Stores extracted location data in a PostgreSQL database using SQLAlchemy.

* Asynchronous Processing: Handles tasks asynchronously with asyncio for better performance.

* FastAPI-Powered Backend: The application is built using FastAPI, a modern and high-performance web framework. It enables the app to expose RESTful APIs for database access

## Installation

1. Clone repo
```sh
git clone https://github.com/michalhnat/Antiradar

cd Antiradar/backend
```

2. Setup venv and install dependencies
```sh
python3 -m venv venv

source venv/bin/activate

pip install -r backend/requirements.txt
```
3. Setup db
```sh
cd Antiradar/db

#edit docker-compose.yml to match your preferences

docker compose up -d

PYTHONPATH=$PWD python3 backend/utils/init_db.py
```

4. Setup your Facebook cookies
    - Follow instructions on https://github.com/togashigreat/fbchat-muqit to get your fb cookies

    - **IMPORTANT NOTICE** - this is an *unofficial* Messenger API. **Don't** use your personal Facebook account. A dummy account is highly recommended.

    - Store your cookies JSON file in `/Antiradar/backend`. For example, in a new `credentials` folder.`

5. Create `.env` file
```sh
touch .env

vim .env

#Fill with your config

OPEN_ROUTER_API=<your_openrouter_api_key>
FB_CREDENTIALS_PATH=<path_to_cookies>
DATABASE_URL=<your_database_url>
```

## Usage

1. Start the application:
   ```sh
   #while in being at /Antiradar
   python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   ```

2. Access the API:
   ```
   http://127.0.0.1:8000/docs
   ```


3. Example API Endpoints:
   - **GET /locations**: Retrieve all stored locations from the database.

## Licensing

This project is licensed under the GNU General Public License v3.0.

This project uses third-party libraries licensed under BSD-3-Clause, Apache 2.0, and MIT licenses.
See THIRD-PARTY-LICENSES.md for details.