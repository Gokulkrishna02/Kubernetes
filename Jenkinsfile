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
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'kuber',   // 🔥 MUST match Jenkins credential ID
                        usernameVariable: 'USER',
                        passwordVariable: 'PASS'
                    )]) {
                        bat "echo %PASS% | docker login -u %USER% --password-stdin"
                    }
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
