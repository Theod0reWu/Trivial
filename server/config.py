from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    room_id_length: int = 6
    #### Timer settings ####
    # all time is in seconds
    picked_time: int = 3 # time that the board flickers over the picked item
    answer_time: int = 6 # time that a user gets to submit an answer
    buzz_in_time: int = 10 # time that users get to buzz-in for a clue
    response_show_time: int = 3 # time to show correct/incorrect reponses