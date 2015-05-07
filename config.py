# -*- coding: utf-8 -*-
#
# Author: Craig Russell <craig@craig-russell.co.uk>
# Gloabal database entities and configuration

from sqlalchemy import create_engine, Column, Integer, String, PickleType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database Config - TODO refactor using Flask integration
sql_engine = create_engine('sqlite:///:memory:', echo=False)
SQL_Session = sessionmaker(bind=sql_engine)
SQL_Base = declarative_base()