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
        bat 'python -m venv venv'
        bat 'venv\\Scripts\\python -m pip install --upgrade pip'
        bat 'venv\\Scripts\\python -m pip install -r requirements.txt'
    }
}

        stage('Run App') {
            steps {
                bat 'python app.py'
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
