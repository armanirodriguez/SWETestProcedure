from app import app
import argparse

parser = argparse.ArgumentParser(description='Run the Test Management Web Application')

if __name__ == '__main__':
    app.run(debug=True)