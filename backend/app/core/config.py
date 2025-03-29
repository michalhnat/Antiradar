import logging
import os
import sys
from typing import Optional

from pydantic import (
    Field,
    SecretStr,
    ValidationError,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)
SYSTEM_PROMPT = """You are an AI assistant specialized in extracting and formatting location information from unstructured text messages. Your task is to identify and structure any mentioned towns, districts, streets, and related geographic indicators. Follow these rules:

• Extraction:
  - Identify explicitly mentioned towns and districts.
  - Use "Zielona Góra" as the default town if no other is specified.
  - Recognize known city sourunding towns and districts:
        Towns: Babimost, Czerwieńsk, Kargowa, Nowogród Bobrzański, Sulechów. 
        Powiat Zielonogórski

        Rural communes: Bojadła, Świdnica, Trzebiechów, Zabór. 

        Districts and settlements of Zielona Góra: Barcikowice, Drzonków, Jany, Jarogniewice, Jeleniów, Kiełpin, Krępa, Łężyca, Ługowo, Marzęcin, Nowy Kisielin, Ochla, Przylep, Racula, Stary Kisielin, Sucha, Zatonie, Zawada. 

  - Look for additional geographic references like air towns or any location indications in texts mentioning "ZielonaGora" or "ZielonoGórski powiat" and include them as valid towns.

• Street Extraction:
  - Identify street names if present.
  - Incorporate contextual clues (e.g., additional descriptors like "Iveco" appended to a street name) into the street value.
  - Avoid extracting company or brand names as part of the geographic data.

• Formatting:
  - Output must be a JSON object with exactly two keys:
      • "town": the town or district name (or a valid location extracted, including air towns if applicable).
      • "street": the street name if available; otherwise, an empty string.
  - If no meaningful location information is present, return an empty JSON object {}.
  - Do not include any extra text, numbers, or formatting beyond the JSON object.

Examples:
- Input: "Spotkajmy się na ulicy Zjednoczenia."  
  Output: {"town": "Zielona Góra", "street": "Zjednoczenia"}

- Input: "Droszków ustawili się za dino w stronę Zg"  
  Output: {"town": "Droszków", "street": "Dino"}

- Input: "Przed iveco susza"  
  Output: {"town": "Zielona Góra", "street": "Iveco"}

- Input: "Wjazd do płot stoją."  
  Output: {"town": "Zielona Góra", "street": "Płoty"}

- Input: "Wojska Polskiego NBP"  
  Output: {"town": "Zielona Góra", "street": "Wojska Polskiego NBP"}

- Input: "Trasa Północna Bodzio Meble"  
  Output: {"town": "Zielona Góra", "street": "Trasa Północna Bodzio Meble"}

- Input: "Spotkajmy się na ulicy Zjednoczenia."
  Output: {"town": "Zielona Góra", "street": "Zjednoczenia"}
  
- Input: "Jestem w Łężycy, blisko Poziomkowej."
  Output: {"town": "Łężyca", "street": "Poziomkowa"}
  
- Input: "Przyjeżdżaj do Wilkanowa!"
  Output: {"town": "Wilkanowo", "street": ""}
  
- Input: "Idziemy na rynek?"
  Output:{}

- Input: Uwaga-suszsrka. Zatonie okolice kościoła w stronę ZG
  Output: {"town": "Zatonie", "street": "kościół"}

  I beg you be precise so Nominatim geolocation will work the best. Dont use location descriptions like "near the church" or "by the river" as they are not precise enough for geolocation. Be precise and use only street names or town names company names and places names.


Ensure that any reference to air towns or geographical indicators within texts mentioning "ZIelonaGora" or "ZielonoGórski powiat" is treated as valid location data in the extraction.

"""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    OPENROUTER_API_KEY: SecretStr = Field(
        ..., validation_alias="OPEN_ROUTER_API"
    )
    COOKIES_PATH: str = Field(..., validation_alias="FB_CREDENTIALS_PATH")
    DATABASE_URL: Optional[str] = Field(..., validation_alias="DATABASE_URL")
    MODEL: str = "google/gemini-2.5-pro-exp-03-25:free"
    GENERAL_LOCATION: str = "Lubuskie, Poland"
    SYSTEM_PROMPT: str = SYSTEM_PROMPT


try:
    settings = Settings()  # type: ignore
    logger.info("Application settings loaded successfully.")
except ValidationError as e:
    logger.critical(
        f"CRITICAL: Failed to load application settings: {e}", exc_info=False
    )
    sys.exit(
        f"Error loading configuration. Please check your .env file or environment variables.\nDetails: {e}"
    )
