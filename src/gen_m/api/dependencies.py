from typing import Annotated 

from fastapi import Depends
from sqlalchemy.orm import Session

from gen_m.database.session import get_db

DatabaseSession = Annotated[Session, Depends(get_db)]

