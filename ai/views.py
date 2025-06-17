from django.shortcuts import get_object_or_404, redirect, render
from battles.models import SoloBattle
from users.models import Player
from utility import _solo_battle_character, get_solo_battle_characters
from .models import *
import json, random
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import logout,login,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from pathlib import Path
import os
import json


BASE_DIR = Path(__file__).resolve().parent


