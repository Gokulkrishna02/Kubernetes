pipeline {
    agent any

    environment {
        IMAGE_NAME = "gokulkrishna0201/airline:latest"
    }

    stages {

        stage('Clone') {
            steps {
                git 'https://github.com/Gokulkrishna02/Kubernetes.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t %IMAGE_NAME% ."
            }
        }

        stage('Login DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {
                    bat 'echo %PASS% | docker login -u %USER% --password-stdin'
                }
            }
        }

        stage('Push Image') {
            steps {
                bat "docker push %IMAGE_NAME%"
            }
        }
    }
}
