// Common mixins for PixyShip vue controls
import moment from 'moment'
import isEmpty from 'lodash'

const apiServer = process.env.VUE_APP_PIXYSHIP_API_URL
const spriteServer = process.env.VUE_APP_SPRITES_URL
const rarityOrder = {
  "common": 0,
  "elite": 1,
  "unique": 2,
  "epic": 3,
  "hero": 4,
  "special": 5,
  "legendary": 6,
}

export default {
  data() {
    return {
      changesEndpoint: apiServer + 'api/changes',
      collectionsEndpoint: apiServer + 'api/collections',
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
      rarityOrder: rarityOrder,
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

    filterCombobox(value, searchArray, andSearch = false) {
      if (searchArray === null) {
        return true
      }

      if (searchArray.length === 0) {
        return true
      }

      if (value == null || value == '') {
        value = 'None'
      }

      let result = false

      if (andSearch) {
        result = searchArray.every(search => {
          if (value.toString().toLowerCase().includes(',')) {
            return value.toString().toLowerCase().includes(search.toString().toLowerCase())
          } else {
            return value.toString().toLowerCase() === search.toString().toLowerCase()
          }

        })
      } else {
        result = searchArray.some(search => {
          if (value.toString().toLowerCase().includes(',')) {
            return value.toString().toLowerCase().includes(search.toString().toLowerCase())
          } else {
            return value.toString().toLowerCase() === search.toString().toLowerCase()
          }

        })
      }


      return result
    },

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
        let computedTerm = term

        if (computedTerm === 'None') {
          computedTerm = ''
        }

        if (computedTerm.length >= 2
          && (computedTerm[0] === "'" || computedTerm[0] === '"')
          && computedTerm[0] === computedTerm[computedTerm.length - 1]
        ) {
          return value.toString().toLowerCase() === computedTerm.substring(1, computedTerm.length - 1)
        }

        return value.toString().toLowerCase().indexOf(computedTerm) !== -1
      })

      return result
    },

    multipleFilterWithNegative(value, search) {
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

      const negativeTerms = terms.filter(term => term.length >= 2 && term[0] === '-')
      const positiveTerms = terms.filter(term => term.length >= 2 && term[0] !== '-')

      let positiveResult = true
      let negativeResult = false

      if (positiveTerms.length > 0) {
        positiveResult = positiveTerms.some(term => {
          if (term.length >= 2
            && (term[0] === "'" || term[0] === '"')
            && term[0] === term[term.length - 1]
          ) {
            return value.toString().toLowerCase() === term.substring(1, term.length - 1)
          }

          return value.toString().toLowerCase().indexOf(term) !== -1
        })
      }

      if (negativeTerms.length > 0) {
        negativeResult = negativeTerms.some(term => {
          let computedTerm = term.substring(1, term.length)

          if (computedTerm.length >= 2
            && (computedTerm[0] === "'" || computedTerm[0] === '"')
            && computedTerm[0] === computedTerm[computedTerm.length - 1]
          ) {
            return value.toString().toLowerCase() === computedTerm.substring(1, computedTerm.length - 1)
          }

          return value.toString().toLowerCase().indexOf(computedTerm) !== -1
        })
      }

      return positiveResult && !negativeResult
    },

    spriteStyle(sprite, color = '', border = 0) {
      if (Object.keys(sprite).length === 0) {
        return {}
      }

      let obj = {
        background: `${color} url('${spriteServer}${sprite.source}.png') -${sprite.x}px -${sprite.y}px`,
        width: `${sprite.width}px`,
        height: `${sprite.height}px`,
        border: `${border}px solid lightgrey`,
        imageRendering: 'pixelated'
      }

      return obj
    },

    spriteStyleScaled(sprite, maxSize, color = '', border = 0) {
      if (Object.keys(sprite).length === 0) {
        return {}
      }

      let scale = maxSize / Math.max(sprite.width, sprite.height)
      scale = scale > 1 ? 1 : scale

      let obj = {
        background: `${color} url('${spriteServer}${sprite.source}.png') -${sprite.x}px -${sprite.y}px`,
        width: `${sprite.width}px`,
        height: `${sprite.height}px`,
        border: `${border}px solid lightgrey`,
        imageRendering: 'pixelated',
        transform: `scale(${scale})`,
        transformOrigin: 'top left'
      }

      return obj
    },

    spriteStyleScaledWrapper(sprite, maxSize) {
      if (Object.keys(sprite).length === 0) {
        return {}
      }

      let scale = maxSize / Math.max(sprite.width, sprite.height)
      scale = scale > 1 ? 1 : scale

      let obj = {
        width: `calc(${sprite.width}px * ${scale})`,
        height: `calc(${sprite.height}px * ${scale})`,
        overflow: 'hidden',
        display: 'block',
      }

      return obj
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
      return this.styleFromSprite({ height: 24, source: 1537, width: 24, x: 469, y: 216 })
    },

    nowTime(time) {
      return time ? moment.utc(time).local().format('YYYY/MM/DD LT') : ''
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
    },

    notEmptyObject(someObject) {
      return Object.keys(someObject).length
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

    getSpriteServer() {
      return spriteServer
    },

    sortRarity(a, b) {
      let rarityAOrder = this.rarityOrder[a.toLowerCase()]
      let rarityBOrder = this.rarityOrder[b.toLowerCase()]

      return this.sortAlphabeticallyExceptNone(rarityAOrder, rarityBOrder)
    },

    sortAlphabeticallyExceptNone(a, b) {
      if (a == b) {
        return 0
      }

      if (a == 'None') {
        return -1
      }

      if (b == 'None') {
        return 1
      }

      if (a < b) {
        return -1
      }

      if (a > b) {
        return 1
      }

      return 0
    },

    updateQueryFromFilter(filterName, filterValue) {
      let searchParams = new URLSearchParams(window.location.search)

      if (isEmpty(filterValue)) {
        searchParams.delete(filterName)
      } else {
        searchParams.set(filterName, filterValue)
      }

      let queryString = searchParams.toString()
      if (queryString) {
        queryString = '?' + queryString
      }

      window.history.pushState('', '', this.$route.path + queryString)
    },

    filterValueComparator(a, b) {
      return a.toLowerCase() == b.toLowerCase()
    }
  }
}
