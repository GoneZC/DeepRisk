const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8082',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        },
        timeout: 60000,
        onError: (err, req, res) => {
          console.error('代理错误:', err);
        }
      },
    },
    hot: true,
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws'
    }
  },
  transpileDependencies: true,
  // 禁用已弃用的功能
  chainWebpack: config => {
    config.resolve.alias.delete('@')
  }
}) 