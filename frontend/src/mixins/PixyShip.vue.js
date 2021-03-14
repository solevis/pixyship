// Common mixins for PixyShip vue controls
import moment from 'moment'

const apiServer = process.env.NODE_ENV === 'development' ? 'http://localhost:5000/' : '/'
const spriteServer = '//pixelstarships.s3.amazonaws.com/'

export default {
  data() {
    return {
      changesEndpoint: apiServer + 'api/changes',
      collectionsEndpoint: apiServer + 'api/collections',
      crewEndpoint: apiServer + 'api/crew',
      itemPricesEndpoint: (id) => apiServer + `api/item/${id}/prices`,
      itemsEndpoint: apiServer + 'api/items',
      prestigeEndpoint: apiServer + 'api/prestige/',
      roomsEndpoint: apiServer + 'api/rooms',
      shipsEndpoint: apiServer + 'api/ships',
      shipEndpoint: apiServer + 'api/user/',
      verifyEndpoint: apiServer + 'api/verify/',
      typeaheadEndpoint: apiServer + 'api/name_typeahead',
      dailyEndpoint: apiServer + 'api/daily',
      researchEndpoint: apiServer + 'api/research',
      playersEndpoint: apiServer + 'api/players'
    }
  },

  methods: {
    multipleFilter(value, search) {
      if (value == null) {
        return false
      }

      if (search == null) {
        return false
      }

      const terms = search.split(',').map(term => term.trim().toLowerCase()).filter(term => term)

      if (terms.length === 0) {
        return false
      }

      let result = terms.some(term => {
        let result = false

        let computedTerm = term
        if (term[0] === '-') {
          computedTerm = term.substring(1);
        }

        if (computedTerm.length >= 2
          && (computedTerm[0] === "'" || computedTerm[0] === '"') 
          && computedTerm[0] === computedTerm[computedTerm.length - 1]
        ) {
          result = value.toString().toLowerCase() !== computedTerm.substring(1, computedTerm.length - 1)
        } else if (computedTerm.length >= 2 && (computedTerm[0] === "'" || computedTerm[0] === '"') && computedTerm[0] === computedTerm[computedTerm.length - 1]) {
          result =  value.toString().toLowerCase() === computedTerm.substring(1, computedTerm.length - 1)
        }

        result = value.toString().toLowerCase().indexOf(computedTerm) !== -1

        if (term[0] === '-') {
          result = !result;
        }

        return result
      })

      return result
    },

    spriteStyle(s, color = '', border = 0) {
      if (Object.keys(s).length === 0) {
        return {}
      }

      let obj = {
        background: `${color} url('${spriteServer}${s.source}.png') -${s.x}px -${s.y}px`,
        width: `${s.width}px`,
        height: `${s.height}px`,
        border: `${border}px solid lightgrey`,
        imageRendering: 'pixelated'
      }

      return obj
    },

    styleFromSprite(s, color = '', border = 0, scale = 1, portScale = 1) {
      if (Object.keys(s).length === 0) {
        return {}
      }

      const fillStr = portScale === 1 ? '' : '/ 100% 100%'
      let obj = {
        background: `${color} url('${spriteServer}${s.source}.png') -${s.x}px -${s.y}px ${fillStr}`,
        width: `${s.width / portScale}px`,
        height: `${s.height / portScale}px`,
        border: `${border}px solid lightgrey`,
        imageRendering: 'pixelated'
      }

      if (scale !== 1) {
        obj.transform = `scale(${scale}, ${scale})`
      }

      return obj
    },

    buxSprite() {
      return this.styleFromSprite({ height: 25, source: 57, width: 25, x: 26, y: 400 })
    },

    mineralSprite() {
      return this.styleFromSprite({ height: 24, source: 57, width: 24, x: 213, y: 345 })
    },

    gasSprite() {
      return this.styleFromSprite({ height: 24, source: 57, width: 24, x: 188, y: 345 })
    },

    supplySprite() {
      return this.styleFromSprite({ height: 24, source: 1537, width: 24, x: 469, y: 216 })
    },

    nowTime(time) {
      return time ? moment.utc(time).local().format('M/D LT') : ''
    },

    formatTime(secs) {
      const days = Math.floor(secs / 86400)
      secs -= days * 86400

      const hours = Math.floor(secs / 3600) % 24
      secs -= hours * 3600

      const minutes = Math.floor(secs / 60) % 60
      secs -= minutes * 60

      const dateStr = (days > 0 ? `${days}d ` : '') +
        (hours > 0 ? `${hours}h ` : '') +
        (minutes > 0 ? `${minutes}m ` : '') +
        (secs > 0 ? `${secs}s` : '')

      return dateStr
    }
  }
}
