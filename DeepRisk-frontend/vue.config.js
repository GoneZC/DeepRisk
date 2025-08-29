const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  devServer: {
    proxy: {
      '/api': {
        target: 'http://172.20.10.164:8081',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        },
        timeout: 120000,
        proxyTimeout: 120000,
        secure: false,
        logLevel: 'debug',
        onError: (err, req, res) => {
          console.error('代理错误:', err);
        },
        onProxyReq: (proxyReq, req, res) => {
          console.log('代理请求:', req.method, req.url);
        },
        onProxyRes: (proxyRes, req, res) => {
          console.log('代理响应:', proxyRes.statusCode, req.url);
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