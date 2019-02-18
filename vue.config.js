const path = require('path');

module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        '@': __dirname + '/client',
      },
    },
    entry: {
      app: './client/main.js'
    }
  },
  devServer: {
    disableHostCheck: true
  },
  chainWebpack: config => {
    config.plugin('copy').tap(([options]) => {
      options[0].ignore.push('data/**/*')
      return [options]
    })
  }
}
