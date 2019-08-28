const AdminMixin = {
  props: {
    initIsAdmin: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isAdmin: this.initIsAdmin
    }
  },
}


const AjaxProcessMixin = {
  props: {
    parentProcessing: {
        type: Boolean,
        default: false
    }
  },
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


const BaseMessage = {
  props: {
    messageType: {
      type: String,
      default: 'success'
    },
    messageText: {
      type: String,
      default: ''
    },
    initAutoClose: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      isOpen: true,
      timerId: null,
      timerDelay: 3000,
      autoClose: this.initAutoClose
    }
  },
  methods: {
    close() {
      clearTimeout(this.timerId)
      this.isOpen = false
    },
    load() {
      if (this.autoClose) {
        this.timerId = setTimeout(()=>{
          this.close()
        }, this.timerDelay) 
      }
    }
  },
  created() {
    this.load()
  },
}

const BaseDropdown = {
  mixins: [ClickOutsideMixin],
  props: {
    id: {
      type: String,
      required: true
    },
    dropdownClasses: {
      type: String,
      default: ''
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
  }
}

const BaseFileUploader = {
  mixins: [AjaxProcessMixin],
  props: {
    initUploadUrl: {
      type: String,
      required: true
    },
  },
  data() {
    return {
      uploadUrl: this.initUploadUrl,
      file: null,
    }
  },
  methods: {
    handleFileUpload() {
      this.file = this.$refs.file.files[0]
      this.$emit('change-file')
    },
    submitFile() {
      if (this.validateFile()) {
        this.process()
        let formData = new FormData()
        formData.append('file', this.file);

        axios.post(
          this.uploadUrl,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        )
        .then(response => {
          this.success(response)
        })
        .catch(error => {
          if (error.response) {
            console.log(error.response)
          } else if (error.request) {
            console.log(error.request)
          } else {
            console.log(error.message)
          }
          console.log(error.config)
        })
        .finally(() => {
          this.complete()
        })
      }
    },
    validateFile() {
      return true
    }
  },
  template: `
    <div class="file has-name is-fullwidth">

    <label class="file-label">

    <input 
    class="file-input" 
    type="file" 
    ref="file" 
    name="resume"
    @change="handleFileUpload"
    :disabled="processing"
    >

    <span class="file-cta">

    <span class="file-icon">
    <i class="fas fa-upload"></i>
    </span>

    <span class="file-label">
    <slot name="label-select-file">
    Choose a file
    </slot>
    </span>

    </span>

    <span class="file-name" ref="filename">
    </span>

    </label>

    <button 
    class="button is-primary"
    v-bind:class="[{ 'is-loading': processing }]"
    @click.prevent="submitFile"
    :disabled="file == ''"
    >

    <slot name="label-submit">
    Submit
    </slot>
    
    </button>

    </div>
  `
}

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
