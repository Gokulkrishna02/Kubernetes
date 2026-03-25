pipeline {
    agent any

    tools {
        maven 'Maven 3.8.6'  // Adjust to your Maven installation name in Jenkins
        jdk 'JDK 11'         // Adjust to your JDK installation name in Jenkins
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/GVanithasri/Airline-Reservation-System.git'
            }
        }

        stage('Build') {
            steps {
                bat 'mvn clean compile'
            }
        }

        stage('Test') {
            steps {
                bat 'mvn test'
            }
        }

        stage('Package') {
            steps {
                bat 'mvn package'
            }
        }

        stage('Run App') {
            steps {
                bat 'start /B java -jar target/airline-reservation-system-1.0.0.jar'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'target/*.jar', allowEmptyArchive: true
        }
    }
}
