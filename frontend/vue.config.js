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
            const pad = (n) => n.toString().padStart(2, '0');
            const day = pad(d.getDate());
            const month = pad(d.getMonth() + 1);
            const year = d.getFullYear();
            let hours = d.getHours();
            const minutes = pad(d.getMinutes());
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12;
            return `${day}/${month}/${year}, ${hours}:${minutes}${ampm}`;
          })()
        )
      })
    ]
  },
}