const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        '@': __dirname + '/client',
      },
    },
    entry: {
      app: './client/main.js'
    },
    plugins: [
      new CopyWebpackPlugin([{
        from: path.join(__dirname, 'client/static'),
        to: path.join(__dirname, 'dist'),
        toType: 'dir',
        ignore: ['.DS_Store']
      }])
    ]
  },
  chainWebpack: config => {
    config.resolve.extensions.prepend('.mjs');
    config.module.rule('mjs').test(/\.mjs$/).include.add(/node_modules/).end().type('javascript/auto');
  },
  devServer: {
    contentBase: path.join(__dirname, 'client/static'),
    disableHostCheck: true
  },
  pages: {
    index: {
      entry: 'client/main.js',
      template: 'client/index.html',
      title: 'Ballistics'
    }
  }
}
