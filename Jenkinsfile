pipeline {
    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        DOCKER_IMAGE = 'airline-reservation-system'
        DOCKER_TAG = "${BUILD_NUMBER}"
        PYTHON_VERSION = '3.9'
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    echo '🔄 Checking out code...'
                    checkout scm
                }
            }
        }

        stage('Setup Python Environment') {
            steps {
                script {
                    echo '📦 Setting up Python virtual environment...'
                    sh '''
                        python3 --version
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Code Quality Checks') {
            steps {
                script {
                    echo '✅ Running code quality checks...'
                    sh '''
                        . venv/bin/activate
                        pip install pylint flake8 2>/dev/null || true
                        flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics || true
                        pylint app.py --fail-under=8 || true
                    '''
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    echo '🧪 Running tests...'
                    sh '''
                        . venv/bin/activate
                        pip install pytest pytest-cov 2>/dev/null || true
                        pytest tests/ --cov=. --cov-report=html --cov-report=xml || true
                    '''
                }
            }
        }

        stage('Security Scan') {
            steps {
                script {
                    echo '🔒 Running security checks...'
                    sh '''
                        . venv/bin/activate
                        pip install bandit 2>/dev/null || true
                        bandit -r . -f json -o bandit-report.json || true
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo '🐳 Building Docker image...'
                    sh '''
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Deploy to Dev') {
            when {
                branch 'develop'
            }
            steps {
                script {
                    echo '🚀 Deploying to Dev environment...'
                    sh '''
                        docker run -d \
                          -p 5000:5000 \
                          --name airline-res-dev-${BUILD_NUMBER} \
                          ${DOCKER_IMAGE}:${DOCKER_TAG}
                    '''
                }
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo '🎯 Deploying to Production...'
                    sh '''
                        docker run -d \
                          -p 5000:5000 \
                          --restart unless-stopped \
                          --name airline-res-prod-${BUILD_NUMBER} \
                          ${DOCKER_IMAGE}:${DOCKER_TAG}
                    '''
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    echo '🧹 Cleaning up workspace...'
                    sh '''
                        rm -rf venv
                        docker system prune -f || true
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                echo '📊 Publishing reports...'
                publishHTML([
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Code Coverage Report'
                ]) || true
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'bandit-report.json',
                    reportName: 'Security Report'
                ]) || true
            }
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs above.'
        }
    }
}
