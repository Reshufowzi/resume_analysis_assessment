pipeline {
    agent any

    environment {
        DOCKER_USERNAME = "reshma0209"
        IMAGE_NAME = "resume-app"
        TAG = "${BUILD_NUMBER}"
        CONTAINER_NAME = "resume-container"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t $DOCKER_USERNAME/$IMAGE_NAME:$TAG .
                docker tag $DOCKER_USERNAME/$IMAGE_NAME:$TAG $DOCKER_USERNAME/$IMAGE_NAME:latest
                '''
            }
        }

        stage('Login to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-creds',
                    usernameVariable: 'USERNAME',
                    passwordVariable: 'PASSWORD'
                )]) {
                    sh 'echo $PASSWORD | docker login -u $USERNAME --password-stdin'
                }
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                sh '''
                docker push $DOCKER_USERNAME/$IMAGE_NAME:$TAG
                docker push $DOCKER_USERNAME/$IMAGE_NAME:latest
                '''
            }
        }

        stage('Stop Old Container') {
            steps {
                sh '''
                docker stop $CONTAINER_NAME || true
                docker rm $CONTAINER_NAME || true
                '''
            }
        }

        stage('Run New Container') {
            steps {
                sh '''
                docker run -d -p 5000:5000 \
                --name $CONTAINER_NAME \
                $DOCKER_USERNAME/$IMAGE_NAME:latest
                '''
            }
        }
    }
}
