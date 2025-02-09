module.exports = {
    transpileDependencies: [
        'vuetify'
    ],

    assetsDir: 'static',
    filenameHashing: true,
    productionSourceMap: false,

    devServer: {
        host: '0.0.0.0',
        port: 8080,
    }
}
