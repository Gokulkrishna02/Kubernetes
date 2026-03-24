pipeline {
    agent any

    stages {

        stage('Checkout Code') {
            steps {
                git 'https://github.com/GVanithasri/Airline-Reservation-System.git'
            }
        }

        stage('Setup Python') {
            steps {
                bat '''
                "C:\\Users\\GV\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" -m venv venv
                "C:\\Users\\GV\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run App') {
            steps {
                bat '"C:\\Users\\GV\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" app.py'
            }
        }
    }

    post {
        success {
            echo 'Build Success ✅'
        }
        failure {
            echo 'Build Failed ❌'
        }
    }
}