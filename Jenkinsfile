pipeline {
    // 1. Tell Jenkins to run this job on any available processor engine
    agent any

    // 2. Define environment variables you might need across multiple stages
    environment {
        APP_PORT = '5000'
    }

    // 3. The actual workflow execution sequence
    stages {
        
        stage('Pull Code') {
            steps {
                echo 'Fetching the latest code updates from GitHub...'
                checkout scm
            }
        }

        stage('Build & Start Containers') {
            steps {
                echo 'Rebuilding Docker images and launching the application stack...'
                // 'sh' executes a standard Linux terminal command
                sh 'docker compose up -d --build'
            }
        }

        stage('Run Automation Tests') {
            steps {
                echo 'Verifying application health and connectivity...'
                // Give MySQL a brief moment to accept incoming connections
                sh 'sleep 5'
                // Curl the health endpoint to verify it returns a 200 HTTP status code
                sh "curl --fail http://localhost:${APP_PORT}/health"
            }
        }
        
    }

    // 4. Post-execution blocks run automatically based on the status of the stages
    post {
        always {
            echo 'Cleaning up intermediate build assets...'
        }
        success {
            echo 'Deployment successfully verified!'
        }
        failure {
            echo 'Pipeline execution encountered errors. Check the console logs.'
        }
    }
}