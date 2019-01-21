#!/usr/bin/env groovy

import groovy.json.JsonOutput

def dockerImage
def commitSha

try {
 node('agent') {
  stage("Build") {
   checkout scm
   notifyBitbucket()
   commitSha = sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%H'").trim()
   dockerImage = docker.build("sample-service")
  }

  stage("Test") {
   dockerImage.inside("-u root --volume=/var/run/docker.sock:/var/run/docker.sock --entrypoint=''") {
    sh 'python manage.py test --settings=project.settings.dev'
   }
  }

  if (env.BRANCH_NAME == 'master') {
   stage("Push Image") {
    docker.withRegistry("staging-ecr-hostname", "ecr:repo-name") {
     dockerImage.push(commitSha)
    }
    docker.withRegistry("prod-ecr-hostname", "ecr:repo-name") {
     dockerImage.push(commitSha)
    }
   }

   stage('Deploy to staging') {
    withCredentials([usernamePassword(credentialsId: 'sys-user', usernameVariable: 'USERNAME', passwordVariable: 'SPASSWORD')]) {
     deploy('eu-staging', 'sample-service', 'staging-image', commitSha)
    }
   }

   try {
    stage('Promotion') {
     timeout(time: 1, unit: 'HOURS') {
      input 'Deploy to Production?'
     }
    }

    stage('Deploy to prod') {
     withCredentials([usernamePassword(credentialsId: 'sys-user', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
      deploy('eu-production', 'sample-service', 'prod-image', commitSha)
     }
    }
   } catch (FlowInterruptedException) {
    currentBuild.result = 'SUCCESS'
   }
  }
 }

 currentBuild.result = 'SUCCESS'


} catch (err) {
 echo '' + err.toString()
 currentBuild.result = 'FAILED'
}

node('agent') {
  notifyBitbucket()
}

def deploy(cluster, service, image, version) {
    def manifest = [
        team                 : 'team-name',
        cluster              : cluster,
        service              : service,
        features             : ['ssh'],
        version              : version,
        image                : image,
        application_variables: [
            ENVIRONMENT: cluster
        ]
    ]
    def manifestJson = JsonOutput.toJson(manifest)
    print "Manifest: ${manifestJson}"

    sh """
        echo Deploying ${cluster} ${service}
        sb deploy -w - <<BODY
$manifestJson
BODY
    """
}
