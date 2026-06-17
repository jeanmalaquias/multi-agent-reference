// Azure Container Apps deployment for the multi-agent gateway.
// Deploy: az deployment group create -g <rg> -f main.bicep -p containerImage=<img>

@description('Location for all resources.')
param location string = resourceGroup().location

@description('Container image, e.g. ghcr.io/jeanmalaquias/multi-agent-reference:latest')
param containerImage string

@description('Per-agent LLM provider (see ADR-003).')
param providerName string = 'mock'

var appName = 'multi-agent'

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${appName}-logs'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${appName}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
      }
    }
    template: {
      containers: [
        {
          name: appName
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'MAGENT_PLANNER_PROVIDER', value: providerName }
            { name: 'MAGENT_RESEARCHER_PROVIDER', value: providerName }
            { name: 'MAGENT_WRITER_PROVIDER', value: providerName }
            { name: 'MAGENT_CRITIC_PROVIDER', value: providerName }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/healthz', port: 8080 }
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
      }
    }
  }
}

output fqdn string = app.properties.configuration.ingress.fqdn
