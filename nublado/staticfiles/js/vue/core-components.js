/**
core-components.js

The core components from which the components used in the app are based on.
These components are meant to be bases and not to be directly implemented.
Implemented components are declared in app-components.js.

**/


/** General mixins **/

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

/** Mixins that app components are based on. **/

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
      processing: false,
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
          this.success(response)
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
      var formData = new FormData();
      for (var key in data) {
        formData.append(key, data[key]);
      }
      return formData
    },
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
  props: {
    initId: {
      type: Number,
      default: 0
    },
    initValue: {
      type: String,
      required: true
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
      isVisible: true
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
      class="delete-tag"
      @click.prevent="remove"
      >
        <i class="fas fa-times"></i>
      </a>
    </div>
    </transition>
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

const BaseDeleteTag = {
  mixins: [BaseTag],
  props: {
    initConfirmationId: {
      type: String,
      default: 'delete-modal'
    },
    initDeleteUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      confirmationId: this.initConfirmationId,
      deleteUrl: this.initDeleteUrl
    }
  },
  methods: {
    remove() {
      this.$emit('tag-remove', this.id)
      this.isVisible = false
    }
  },
  template: `
    <transition name="fade-transition" v-on:after-enter="isVisible = true" v-on:after-leave="isVisible = false">
    <div 
    class="ui label tagblock"
    v-bind:key="id"
    v-show="isVisible"
    >
      <a 
      class="tag-text"
      @click.prevent="select"
      > 
      {{ value }} 
      </a>
      &nbsp;
      <ajax-delete 
      :confirmation-id="confirmationId"
      :delete-url="deleteUrl"
      @ajax-success="remove"
      inline-template
      >
        <a
        @click.prevent="confirmDelete"
        >
          <i class="fa-times fas"></i>
        </a>
      </ajax-delete>

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
