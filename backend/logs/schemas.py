# from datetime import datetime
# from Pydantic import BaseModel, Field


# class UserActionLog(BaseModel):
#     log_data : str = Field(description='данные лога пользователя')

# class UserActionLogCreate(UserActionLog):
#     ...

# class UserActionLogResponse(UserActionLog):
#     log_id : int = Field(description='ид лога пользователя')
#     log_date : datetime = Field(description='дата лога')
#     user_id : int = Field(description='ид пользователя')

#     class Config:
#         from_attributes = True