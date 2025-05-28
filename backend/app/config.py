# For calling the API
import base64
import requests
from openai import OpenAI

# For crawling data
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
import re

# For extracting site and keyword data
from pydantic import BaseModel

# For Q&A
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI

# For FastAPI
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

# For MongoDB
import os
from pymongo import MongoClient
from bson import ObjectId
import gridfs
from datetime import datetime

# For location summarization
from collections import defaultdict

# For crawl Bing
import random
import time

# For split sentences
import spacy
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

# For crawl WHO website and others
import pdfplumber
from contextlib import nullcontext
from PyPDF2 import PdfReader
import concurrent.futures

from dotenv import load_dotenv

# Load file .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
client = OpenAI(
    api_key = OPENAI_API_KEY,
)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

STORAGE_PATH = "./storage/pdf_files"

MINIMUM_K = 1

