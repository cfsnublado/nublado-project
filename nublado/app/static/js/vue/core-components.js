/**
core-components.js

The core components from which the components used in the app are based on.
These components are meant to be bases and not to be directly implemented.
Implemented components are declared in app-components.js.

**/


/** General mixins **/

const VisibleMixin = {
  props: {
    initIsVisible: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      isVisible: this.initIsVisible
    }
  }
}

const AdminMixin = {
  props: {
    initIsAdmin: {
      type: Boolean,
      default: false
    },
  },
  data() {
    return {
      isAdmin: this.initIsAdmin
    }
  },
}

const AjaxProcessMixin = {
  data() {
    return {
      processing: false
    }
  },
  methods: {
    process() {
      this.processing = true
      this.$emit('ajax-process')
    },
    complete() {
      this.processing = false
      this.$emit('ajax-complete')
    },
    success() {
      this.processing = false
      this.$emit('ajax-success')
    }
  }
}

const ClickOutsideMixin = {
  methods: {
    onCloseOutside() {
      console.log('clicked outside')
    },
    closeOutside(event) {
      if (!this.$el.contains(event.target)) {
        this.onCloseOutside()
      }
    },
    addClickOutsideHandler() {
      window.addEventListener('click', this.closeOutside)
    },
    removeClickOutsideHandler() {
      window.removeEventListener('click', this.closeOutside)
    }
  },
  created() {
    this.addClickOutsideHandler()
  },
  beforeDestroy() {
    this.removeClickOutsideHandler()
  }
}

const MarkdownMixin = {
  data() {
    return {
      converter: new showdown.Converter()
    }
  },
  methods: {
    markdownToHtml(markdown) {
      return this.converter.makeHtml(markdown)
    }
  }
}

const HighlightMixin = {
  props: {
    contextElement: {
      type: String,
      default: '#context'
    }
  },
  data() {
    return {
      highlighter: new Mark(this.contextElement),
      markOptions: {
        "className": "tagged-text",
        "accuracy": {
          "value": "exactly",
          "limiters": [
            ",", ".", "!", "?", ";", ":", "'", "-", "—",
            "\"", "(",  ")", "¿", "¡", 
            "»", "«", 
          ]
        },        
        "acrossElements": true,
        "separateWordSearch": false,
      }
    }
  },
  methods: {
    highlight(terms) {
      this.highlighter.mark(terms, this.markOptions)
    },
    clearHighlight() {
      this.highlighter.unmark(this.markOptions)
    }
  }
}

const PaginationMixin = {
  data() {
    return {
      previousUrl: null,
      nextUrl: null,
      pageNum: null,
      pageCount: null,
      resultsCount: null
    }
  },
  methods: {
    setPagination(previousUrl, nextUrl, pageNum, resultsCount, pageCount) {
      this.previousUrl = previousUrl
      this.nextUrl = nextUrl
      this.pageNum = pageNum
      this.resultsCount = resultsCount
      this.pageCount = pageCount
    }
  }
}

const UrlMixin = {
  methods: {
    getUrlParameter(url, parameter) {
      parameter = parameter.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]')
      var regex = new RegExp('[\\?|&]' + parameter.toLowerCase() + '=([^&#]*)')
      var results = regex.exec('?' + url.toLowerCase().split('?')[1])
      return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '))
    },
    setUrlParameter(url, key, value) {
      var baseUrl = url.split('?')[0]
      var urlQueryString = '?' + url.split('?')[1]
      var newParam = key + '=' + value
      var params = '?' + newParam

      // If the "search" string exists, then build params from it
      if (urlQueryString) {
        var updateRegex = new RegExp('([\?&])' + key + '[^&]*')
        var removeRegex = new RegExp('([\?&])' + key + '=[^&;]+[&;]?')

        if (typeof value === 'undefined' || value === null || value === '') { // Remove param if value is empty
          params = urlQueryString.replace(removeRegex, "$1")
          params = params.replace(/[&;]$/, "")
        } else if (urlQueryString.match(updateRegex) !== null) { // If param exists already, update it
          params = urlQueryString.replace(updateRegex, "$1" + newParam)
        } else { // Otherwise, add it to end of query string
          params = urlQueryString + '&' + newParam
        }
      }
      // no parameter was set so we don't need the question mark
      params = params === '?' ? '' : params

      return baseUrl + params 
    }
  }
}

/** Mixins that app components are based on. **/

const BaseModel = {
  mixins: [ VisibleMixin ],
  props: {
    initViewUrl: {
      type: String,
      default: ''
    },
    initEditUrl: {
      type: String,
      default: ''
    },
    initDeleteUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      viewUrl: this.initViewUrl,
      editUrl: this.initEditUrl,
      deleteUrl: this.initDeleteUrl
    }
  },
  methods: {
    view() {
      if (this.viewUrl) {
        window.location.replace(this.viewUrl)
      }
    },
    edit() {},
    remove() {
      this.isVisible = false
    }
  }
}

/** Message **/

const BaseMessage = {
  props: {
    messageType: {
      type: String,
      default: 'success'
    },
    messageText: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      isOpen: true,
      timerId: null,
      timerDelay: 3000
    }
  },
  methods: {
    close() {
      clearTimeout(this.timerId)
      this.isOpen = false
    },
    load() {
      this.timerId = setTimeout(()=>{
        this.close()
      }, this.timerDelay) 
    }
  },
  created() {
    this.load()
  },
  template: `
    <transition name="fade-transition-slow" v-on:after-enter="isOpen = true" v-on:after-leave="isOpen = false">

    <div v-show="isOpen" :class="['alert-' + messageType, 'alert']">

    <div class="alert-content">
    {{ messageText }}
    </div>

    <button
    type="button" 
    class="close"
    @click.prevent="close"
    >
    <span aria-hidden="true">&times;</span>
    </button>

    </div>

    </transition>
  `
}

/** Modal **/

const BaseModal = {
  props: {
    initId: {
      type: String,
      default: 'modal'
    }
  },
  data() {
    return {
      modalId: this.initId,
      modalEnabled: true,
      isOpen: false,
    }
  },
  methods: {
    show(params) {
      this.isOpen = true
    },
    close() {
      this.isOpen = false
    },
  }
}

/** DROPDOWN **/

const BaseDropdown = {
  mixins: [ClickOutsideMixin],
  props: {
    id: String,
    containerClasses: String,
    triggerClasses: String,
    dropdownClasses: String,
    dropup: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isOpen: false,
    }
  },
  methods: {
    toggle(manual) {
      this.$emit('toggle')
      if (manual === true || manual === false) {
        this.isOpen = manual
      } else {
          this.isOpen = !this.isOpen
      }
    },
    onCloseOutside() {
      this.isOpen = false
    }
  },
  template: `
    <div v-bind:id="id" class="dropdown collapse-container" v-bind:class="[{ open: isOpen }, containerClasses]">

    <a href="#" v-bind:class="triggerClasses" @click.prevent="toggle">
    <slot name="trigger-content">component label</slot>
    </a>

    <div 
    v-bind:class="[dropup ? 'dropup-menu' : 'dropdown-menu', dropdownClasses, 'collapse-item']"
    @click="toggle(false)"
    >

    <slot name="dropdown-content">
      Put something here, ideally a list of menu items.
    </slot>

    </div>

    </div>
  `
}

/** FORM **/

const FormError = {
  props: ['errors'],
  template: `
    <ul class="errorlist">
      <slot></slot>
    </ul>`
}

const BaseForm = {
  mixins: [AjaxProcessMixin],
  components: {
    'form-error': FormError
  },
  props: {
    initTimerDelay: {
      type: Number,
      default: 500
    },
    reset: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      formData: {},
      timerId: null,
      timerDelay: this.initTimerDelay,
      errors: {}
    }
  },
  methods: {
    onSubmit(event, convertData=true) {
      this.process()
      clearTimeout(this.timerId)
      this.timerId = setTimeout(()=>{
        let formData = convertData ? this.convertToFormData(this.formData) : this.formData
  
        axios.post(event.target.action, formData)
        .then(response => {
          this.success()
        })
        .catch(error => {
          if (error.response) {
            console.log(error.response)
            this.errors = error.response.data.errors.fields
          } else if (error.request) {
            console.log(error.request)
          } else {
            console.log(error.message)
          }
          console.log(error.config)
        })
        .finally(() => this.complete())
      }, this.timerDelay)
    },
    resetForm() {
      for (var key in this.formData) {
        if (this.formData.hasOwnProperty(key)) {
          this.formData[key] = ''
        }
      }
    },
    convertToFormData(data) {
      var formData = new FormData()
      for (var key in data) {
        formData.append(key, data[key])
      }
      return formData
    },
  },
  watch: {
    reset: function(val) {
      if (val == true) {
        this.resetForm()
      }
    }
  }
}

/** Search/Autocomplete **/

const BaseSearch = {
  mixins: [ClickOutsideMixin],
  props: {
    initAutocompleteUrl: {
      type: String,
      required: true
    },
    initSearchUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      searchTerm: '',
      searchParams: {
        term: ''
      },
      results: [],
      isOpen: false,
      searchTimerId: null,
      searchDelay: 600,
      minSearchLength: 2,
      autocompleteUrl: this.initAutocompleteUrl,
      searchUrl: this.initSearchUrl
    }
  },
  methods: {
    setResult(result) {
      this.searchTerm = result
      this.isOpen = false
    },
    search() {
      console.log('search')
    },
    success(response) {
      if (response.data.length) {
        this.results = response.data
        this.isOpen = true
      } else {
        this.isOpen = false
      }
    },
    onAutocomplete() {
      clearTimeout(this.searchTimerId)
      this.searchTimerId = setTimeout(()=>{
        if (this.searchTerm.length >= this.minSearchLength) {

          this.searchParams.term = this.searchTerm

          axios.get(this.autocompleteUrl, {
            params: this.searchParams
          })
          .then(response => {
            this.success(response)
          })
          .catch(error => {
            this.error(error)
            if (error.response) {
              console.log(error.response)
            } else if (error.request) {
              console.log(error.request)
            } else {
              console.log(error.message)
            }
            console.log(error.config)
          })
          .finally(() => {})
        } else {
          this.isOpen = false
        }
      }, this.searchDelay)
    },
    onFocus() {
      this.$emit('search-focus')
    },
    onCloseOutside() {
      this.isOpen = false
      this.searchTerm = ''
    },   
  }
}

const BaseLanguageSearch = {
  mixins: [BaseSearch],
  props: {
    initLanguage: {
      type: String,
      default: 'en'
    }
  },
  data() {
    return {
      language: this.initLanguage,
      languageUrl: ''
    }
  },
  methods: {
    setLanguage(lang) {
      this.language = lang
      this.autocompleteUrl = this.languageUrl.replace('zz', this.language)
      this.onAutocomplete()
    },
    search() {
      url = this.searchUrl + "?search_term=" + this.searchTerm + "&search_language=" + this.language
      window.location.replace(url);
    }
  },
  created() {
    this.languageUrl = this.autocompleteUrl
    this.autocompleteUrl = this.languageUrl.replace('zz', this.language)
  },
}

/** Tags **/

const BaseTag = {
  mixins: [ VisibleMixin ],
  props: {
    initId: {
      type: Number,
      default: 0
    },
    initValue: {
      type: String,
      required: true
    },
    initCanRemove: {
      type: Boolean,
      default: false
    },
    selectRedirectUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      id: this.initId,
      value: this.initValue,
      canRemove: this.initCanRemove,
    }
  },
  methods: {
    select() {
      if (this.selectRedirectUrl) {
        window.location.replace(this.selectRedirectUrl)
      }
      this.$emit('tag-select', this.id)
    },
    remove() {
      this.$emit('tag-remove', this.id)
    }
  },
  template: `
    <div 
    class="ui label tagblock"
    v-show="isVisible"
    >
      <a 
      class="tag-text"
      @click.prevent="select"
      > 
      {{ value }} 
      </a>

      &nbsp;

      <a
      v-if="canRemove"
      @click.prevent="remove"
      >
        <i class="fa-times fas"></i>
      </a>

    </div>
  `
}

const BaseToggleTag = {
  mixins: [BaseTag],
  props: {
    toggleSelect: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    toggle() {
      this.$emit('tag-toggle', this.id)
    },
  },
  template: `
    <transition name="fade-transition" v-on:after-enter="isVisible = true" v-on:after-leave="isVisible = false">

    <div 
    class="ui label tagblock"
    v-show="isVisible"
    >
      <a 
      class="tag-text"
      @click.prevent="select"
      > 
      {{ value }} 
      </a>
      &nbsp;
      <a 
      class="toggle-tag"
      @click.prevent="toggle"
      >
        <i v-bind:class="[toggleSelect ? 'fa-check-square' : 'fa-square', 'fas']"></i>
      </a>
    </div>
    
    </transition>
  `
}

const BaseTagbox = {
  props: {
    tags: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    addTag(tag) {
      this.$emit('add-tag', tag)
    },
    removeTag(index) {
      this.$emit('remove-tag', index)
    },
    selectTag(index) {
      this.$emit('select-tag', index)
    }
  }
}

const BaseSymbolKey = {
  props: {
    initSymbol: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      symbol: this.initSymbol
    }
  },
  methods: {
    displaySymbol() {
      this.$emit('display-symbol', (this.symbol))
    }
  },
  template: `
    <a 
    href="#" 
    class="ui tiny basic icon button"
    :title="symbol"
    @click.prevent="displaySymbol"
    >
    {{ symbol }}
    </a>
  `
}

const BaseSymbolKeypad = {
  props: {
    initDisplayEl: {
      type: String,
      default: "#keypad-display"
    }
  },
  data() {
    return {
      display: '',
      displayEl: this.initDisplayEl
    }
  },
  methods: {
    onDisplaySymbol(symbol) {
      var symbolInput = document.querySelector(this.displayEl)
      var caretPos = symbolInput.selectionStart
      var val = this.display.substring(0, caretPos) + symbol + this.display.substring(caretPos)
      this.display = val
      caretPos = caretPos + symbol.length;
      this.$nextTick(() => {
        symbolInput.focus()
        symbolInput.setSelectionRange(caretPos, caretPos)
      })
    },
  }
}
