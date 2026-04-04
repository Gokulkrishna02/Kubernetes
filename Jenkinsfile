pipeline {
    agent any

    environment {
        DOCKER_USERNAME = "gokulkrishna0201"
        IMAGE_NAME = "airline"
        IMAGE_TAG = "latest"
    }

    stages {

        stage('Clone') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker') {
            steps {
                bat 'docker build -t %DOCKER_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG% .'
            }
        }

        stage('Login DockerHub') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'kuber',
                        usernameVariable: 'USER',
                        passwordVariable: 'PASS'
                    )]) {
                        bat 'echo %PASS% | docker login -u %USER% --password-stdin'
                    }
                }
            }
        }

        stage('Push Image') {
            steps {
                bat 'docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG%'
            }
        }
    }
}
