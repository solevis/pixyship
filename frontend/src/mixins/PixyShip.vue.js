// Common mixins for PixyShip vue controls
import moment from 'moment'

const apiServer = process.env.VUE_APP_PIXYSHIP_API_URL
const spriteServer = process.env.VUE_APP_SPRITES_URL

export default {
  data() {
    return {
      changesEndpoint: apiServer + 'api/changes',
      collectionsEndpoint: apiServer + 'api/collections',
      achievementsEndpoint: apiServer + 'api/achievements',
      crewEndpoint: apiServer + 'api/crew',
      itemPricesEndpoint: (id) => apiServer + `api/item/${id}/prices`,
      itemDetailEndpoint: (id) => apiServer + `api/item/${id}/detail`,
      itemsEndpoint: apiServer + 'api/items',
      prestigeEndpoint: apiServer + 'api/prestige/',
      roomsEndpoint: apiServer + 'api/rooms',
      roomEndpoint: apiServer + 'api/room/',
      shipsEndpoint: apiServer + 'api/ships',
      shipEndpoint: apiServer + 'api/user/',
      verifyEndpoint: apiServer + 'api/verify/',
      typeaheadEndpoint: apiServer + 'api/name_typeahead',
      dailyEndpoint: apiServer + 'api/daily',
      researchesEndpoint: apiServer + 'api/research',
      playersEndpoint: apiServer + 'api/players',
      tournamentEndpoint: apiServer + 'api/tournament',
      lastSalesEndpoint: (type, id) => apiServer + `api/lastsales/${type}/${id}`,
      lastSalesBySaleFromEndpoint: (sale_from) => apiServer + `api/lastsalesbysalefrom/${sale_from}`,
    }
  },

  methods: {
    currencySprite(currency) {
      if (currency == null) {
        return ''
      }

      let lowerCurrency = currency.toLowerCase()

      switch (lowerCurrency) {
        case 'starbux':
          return this.buxSprite()
        case 'gas':
          return this.gasSprite()
        case 'mineral':
          return this.mineralSprite()
        case 'supply':
          return this.supplySprite()
        default:
          return ''
      }
    },

    spriteStyle(sprite, color = '', border = 0) {
      if (Object.keys(sprite).length === 0) {
        return {}
      }

      return {
        background: `${color} url('${spriteServer}${sprite.source}.png') -${sprite.x}px -${sprite.y}px`,
        width: `${sprite.width}px`,
        height: `${sprite.height}px`,
        border: `${border}px solid lightgrey`,
        imageRendering: 'pixelated'
      }
    },

    spriteStyleScaled(sprite, maxSize, color = '', border = 0) {
      if (Object.keys(sprite).length === 0) {
        return {}
      }

      let scale = maxSize / Math.max(sprite.width, sprite.height)
      scale = scale > 1 ? 1 : scale

      return {
        background: `${color} url('${spriteServer}${sprite.source}.png') -${sprite.x}px -${sprite.y}px`,
        width: `${sprite.width}px`,
        height: `${sprite.height}px`,
        border: `${border}px solid lightgrey`,
        imageRendering: 'pixelated',
        transform: `scale(${scale})`,
        transformOrigin: 'top left'
      }
    },

    spriteStyleScaledWrapper(sprite, maxSize) {
      if (Object.keys(sprite).length === 0) {
        return {}
      }

      let scale = maxSize / Math.max(sprite.width, sprite.height)
      scale = scale > 1 ? 1 : scale

      return {
        width: `calc(${sprite.width}px * ${scale})`,
        height: `calc(${sprite.height}px * ${scale})`,
        overflow: 'hidden',
        display: 'block',
      }
    },

    styleFromSprite(sprite, color = '', border = 0, scale = 1, portScale = 1) {
      if (Object.keys(sprite).length === 0) {
        return {}
      }

      const fillStr = portScale === 1 ? '' : '/ 100% 100%'
      let obj = {
        background: `${color} url('${spriteServer}${sprite.source}.png') -${sprite.x}px -${sprite.y}px ${fillStr}`,
        width: `${sprite.width / portScale}px`,
        height: `${sprite.height / portScale}px`,
        border: `${border}px solid lightgrey`,
        imageRendering: 'pixelated'
      }

      if (scale !== 1) {
        obj.transform = `scale(${scale}, ${scale})`
      }

      return obj
    },

    getSpriteUrl(sprite) {
      return `${spriteServer}${sprite.source}.png`
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
      return this.styleFromSprite({ height: 22, source: 57, width: 22, x: 244, y: 345 })
    },

    doveSprite() {
      return this.styleFromSprite({ height: 14, source: 1537, width: 17, x: 490, y: 258 })
    },

    mapSprite() {
      return this.styleFromSprite({ height: 20, source: 1391, width: 30, x: 175, y: 168 })
    },

    nowTime(time) {
      return time ? moment.utc(time).local().format('YYYY/MM/DD LT') : ''
    },

    nowDate(time) {
      return time ? moment.utc(time).local().format('YYYY/MM/DD') : ''
    },

    formatTime(secs) {
      const days = Math.floor(secs / 86400)
      secs -= days * 86400

      const hours = Math.floor(secs / 3600) % 24
      secs -= hours * 3600

      const minutes = Math.floor(secs / 60) % 60
      secs -= minutes * 60

      return (days > 0 ? `${days}d ` : '') +
          (hours > 0 ? `${hours}h ` : '') +
          (minutes > 0 ? `${minutes}m ` : '') +
          (secs > 0 ? `${secs}s` : '')
    },

    getAllAttributes(element) {
      let attributes = element.attributes

      if (element.elements) {
        element.elements.map(innerElement => {
          if (!('elements' in innerElement)) {
            Object.entries(innerElement.attributes).map(innerAttribute => {
              attributes[innerElement.name + '_' + innerAttribute[0]] = innerAttribute[1]
            })
          }
        })
      }

      return attributes
    },

    diffAttributes(newAttributes, oldAttributes) {
      let changes = {
        new: [],
        changed: [],
        removed: []
      }

      if (!oldAttributes) {
        changes.new = Object.entries(newAttributes)
      } else {
        Object.entries(newAttributes).map(newAttribute => {
          if (!(newAttribute[0] in oldAttributes)) {
            changes.new.push(newAttribute)
          } else if (newAttribute[1] !== oldAttributes[newAttribute[0]]) {
            changes.changed.push([newAttribute[0], oldAttributes[newAttribute[0]], newAttribute[1]])
            delete oldAttributes[newAttribute[0]]
          } else {
            delete oldAttributes[newAttribute[0]]
          }
        })
      }

      changes.removed = oldAttributes ? Object.entries(oldAttributes) : []
      return changes
    },

    makeLink(type, id) {
      if (type === 'char') {
        return `/crew/${id}`
      }

      if (type === 'item') {
        return `/item/${id}`
      }

      if (type === 'room') {
        return `/rooms?ids=${id}`
      }

      if (type === 'ship') {
        return `/ships?ids=${id}`
      }

      if (type === 'collection') {
        return `/collections?ids=${id}`
      }

      if (type === 'research') {
        return `/researches?ids=${id}`
      }
    },
  }
}
