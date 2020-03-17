import re
import _thread
import threading
import json
import math
import time
from queue import Queue
from threading import Timer
from time import sleep
from datastore import DataStore
from link import Link
import hashlib
import json

def testdb():
    # Start db
    db = DataStore()


def main():
    print("Starting local test")

    # Test db
    testdb()

if __name__ == "__main__":
    main()
