// Common mixins for Data Table
import _ from 'lodash'

const rarityOrder = {
  "common": 1,
  "elite": 2,
  "unique": 3,
  "epic": 4,
  "hero": 5,
  "special": 6,
  "legendary": 7,
}

const currencies = [
    'Gas',
    'Mineral',
    'Starbux'
]

const itemStats = [
    'ABL',
    'ATK',
    'ENG',
    'RST',
    'ABL',
    'HP',
    'PLT',
    'RPR',
    'SCI',
    'STA',
    'WPN',
]

export default {
  data() {
    return {
      rarityOrder: rarityOrder,
      currencies: currencies,
      itemStats: itemStats,
      globalSortBy: [],
      globalSortDesc: [],
    }
  },

  beforeMount() {
    this.initSorting()
  },

  watch: {
    globalSortBy(value) {
      this.updateQueryFromFilter('sb', value)
    },

    globalSortDesc(value) {
      this.updateQueryFromFilter('sd', value)
    }
  },

  methods: {
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

        if (_.isEmpty(filterValue)) {
          searchParams.delete(filterName)
        } else {
          searchParams.set(filterName, filterValue)
        }

        let queryString = searchParams.toString()
        if (queryString) {
          queryString = '?' + queryString
        }

        if (window.location.search !== queryString) {
          window.history.pushState('', '', this.$route.path + queryString)
        }
    },

    filterValueComparator(a, b) {
      if (typeof a === 'string' && typeof b === 'string') {
        return a.toLowerCase() === b.toLowerCase()
      }

      return a === b
    },

    initSorting() {
      if (this.$route.query.sb) {
        this.globalSortBy = this.$route.query.sb.split(',').map(function(value) {
          return value.trim()
        })
      }

      if (this.$route.query.sd) {
        this.globalSortDesc = this.$route.query.sd.split(',').map(function(value) {
          return value.trim()
        })
      }
    }
  }
}
