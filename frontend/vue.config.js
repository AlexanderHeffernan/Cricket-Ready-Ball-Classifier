const fs = require('fs')
const path = require('path')
const webpack = require('webpack')

const isLocalDev = process.env.NODE_ENV === 'development' && fs.existsSync(path.resolve(__dirname, 'certs/key.pem'));

module.exports = {
  productionSourceMap: false,
  publicPath: process.env.NODE_ENV === 'production' ? '/Cricket-Ready-Ball-Classifier/' : '/',
  devServer: isLocalDev ? {
    https: {
      key: fs.readFileSync(path.resolve(__dirname, 'certs/key.pem')),
      cert: fs.readFileSync(path.resolve(__dirname, 'certs/cert.pem')),
    },
    host: '0.0.0.0',
    port: 8080,
    allowedHosts: 'all'
  } : {},
  configureWebpack: {
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all'
          }
        }
      }
    },
    plugins: [
      new webpack.DefinePlugin({
        __BUILD_DATE__: JSON.stringify(
          (() => {
            const d = new Date();
            // Format date in NZ time zone
            return d.toLocaleString('en-NZ', {
              timeZone: 'Pacific/Auckland',
              day: '2-digit',
              month: '2-digit',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              hour12: true,
            }) + ' NZ time';
          })()
        )
      })
    ]
  },
}