import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

export default createVuetify({
  theme: {
    defaultTheme: 'dark',  // Équivalent à dark: true
  },
  icons: {
    defaultSet: 'mdi',    // Équivalent à iconfont: 'mdi'
    aliases,
    sets: {
      mdi,
    },
  },
})
