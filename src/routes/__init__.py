from flask import Blueprint
from pathlib import Path

router = Blueprint('router',__name__)
# define file address
baseLocation = Path(__file__).absolute().parent.parent # naik ke folder src

# import semua route yang ada ke sini
from .mainHRDRoute import *
from .userData import *
from .masterData import *
