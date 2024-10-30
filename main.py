# main.py
import langchain_patch  # Import the patch
from baby_agi import BabyAGI

def main():
    agi = BabyAGI()
    agi.run()  # BabyAGI initiates and orchestrates tasks

if __name__ == "__main__":
    main()
