const fs = require('fs')
const path = require('path')

module.exports = {
  productionSourceMap: false,
  devServer: {
    https: {
      key: fs.readFileSync(path.resolve(__dirname, 'certs/key.pem')),
      cert: fs.readFileSync(path.resolve(__dirname, 'certs/cert.pem')),
    },
    host: '0.0.0.0',
    port: 8080,
    allowedHosts: 'all'
  }
}