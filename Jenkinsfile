pipeline {
    agent any

    environment {
        IMAGE_NAME = "gokulkrishna0201/airline:latest"
    }

    stages {

        stage('Clone') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Gokulkrishna02/Kubernetes.git'
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
                    powershell '''
                    Write-Host "Logging into DockerHub..."
                    $pass = $env:PASS
                    $pass | docker login -u $env:USER --password-stdin
                    '''
                }
            }
        }

        stage('Push Image') {
            steps {
                bat "docker push %IMAGE_NAME%"
            }
        }
    }

    post {
        success {
            echo "✅ Docker Image pushed successfully!"
        }
        failure {
            echo "❌ Pipeline failed. Check logs."
        }
    }
}
