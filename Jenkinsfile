pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/GVanithasri/Airline-Reservation-System.git'
            }
        }

        stage('Debug') {
            steps {
                bat 'dir'
            }
        }

          stage('Setup Python') {
            steps {
                bat "\"C:\\Users\\GV\\AppData\\Local\\Programs\\Python\\Python311\\python.exe\" -m venv venv"
                bat 'venv\\Scripts\\python -m pip install --upgrade pip'
                bat 'venv\\Scripts\\python -m pip install -r requirements.txt'
            }
        }

        stage('Run App') {
            steps {
                bat 'start /B venv\\Scripts\\python app.py'
            }
        }
    }
}
