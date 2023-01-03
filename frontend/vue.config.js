module.exports = {
    transpileDependencies: [
        'vuetify'
    ],

    assetsDir: 'static',
    filenameHashing: true,
    productionSourceMap: false,

    devServer: {
        public: '0.0.0.0:8080'
    }
}
