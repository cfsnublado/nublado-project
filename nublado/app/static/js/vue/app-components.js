const VocabEntryContext = {
  mixins: [MarkdownMixin, HighlightMixin],
  props: {
    initEntryContext: {
      type: Object,
      required: true
    },
    initSourceUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      entryContext: this.initEntryContext
    }
  },
  methods: {
    selectSource() {
      if (this.initSourceUrl) {
        this.sourceUrl = this.initSourceUrl
          .replace(0, this.entryContext.vocab_source_id)
          .replace('zzz', this.entryContext.vocab_source_slug)
        window.location.replace(this.sourceUrl)
      }
    }
  },
  created() {
    console.log(this.initSourceUrl)
    this.$nextTick(() => {
      this.highlight(this.entryContext.vocab_entry_tags)
    })
  }
}

const VocabContexts = {
  mixins: [
    AjaxProcessMixin,
    PaginationMixin
  ],
  props: {
    initVocabContextsUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      vocabContextsUrl: this.initVocabContextsUrl,
      vocabContexts: null
    }
  },
  methods: {
    getVocabContexts(page=1) {
      this.process()

      params = {
        page: page
      }

      axios.get(this.vocabContextsUrl, {
        params: params
      })
      .then(response => {
        this.vocabContexts = response.data.results
        this.setPagination(
          response.data.previous,
          response.data.next,
          response.data.page_num,
          response.data.count,
          response.data.num_pages
        )
        VueScrollTo.scrollTo({
          el: '#contexts-scroll-top',
        })
        this.success()
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
  created() {
    this.getVocabContexts()
  }
}

const VocabEntries = {
  mixins: [
    AjaxProcessMixin,
    PaginationMixin
  ],
  props: {
    initLanguage: {
      type: String,
      default: 'en'
    },
    initVocabEntriesUrl: {
      type: String,
      default: ''
    },
    initVocabEntryUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      language: this.initLanguage,
      vocabEntriesUrl: this.initVocabEntriesUrl,
      vocabEntryUrl: '',
      vocabEntries: null
    }
  },
  methods: {
    getVocabEntries(page=1) {
      this.process()

      params = {
        language: this.language,
        page: page
      }

      axios.get(this.vocabEntriesUrl, {
        params: params
      })
      .then(response => {
        this.vocabEntries = response.data.results
        this.setPagination(
          response.data.previous,
          response.data.next,
          response.data.page_num,
          response.data.count,
          response.data.num_pages
        )
        VueScrollTo.scrollTo({
          el: '#entries-scroll-top',
        })
        this.success()
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
    },
    setLanguage(language) {
      this.language = language
      this.getVocabEntries()
    },
    entrySelected(entry) {
       this.vocabEntryUrl = this.initVocabEntryUrl
        .replace('xx', entry.language)
        .replace('zzz', entry.slug)
      window.location.replace(this.vocabEntryUrl)     
    }
  },
  created() {
    this.getVocabEntries()
  }
}

const AjaxDelete = {
  mixins: [AjaxProcessMixin],
  props: {
    confirmationId: {
      type: String,
      default: 'confirmation-modal'
    },
    deleteUrl: {
      type: String,
      default: '',
    },
    redirectUrl: {
      type: String,
      default: ''
    },
    initTimerDelay: {
      type: Number,
      default: 500
    }
  },
  data() {
    return {
      timerId: null,
      timerDelay: this.initTimerDelay,
    }
  },
  methods: {
    confirmDelete() {
      this.$modal.showConfirmation(this.confirmationId)
      .then(yes => {
        console.log(yes)
        this.onSubmit()
      })
      .catch(no => {
        console.log(no)
      })
    },
    onSubmit(event) {
      this.process()
      clearTimeout(this.timerId)
      this.timerId = setTimeout(()=>{
        axios.post(this.deleteUrl)
        .then(response => {
          if (this.redirectUrl) {
            window.location.replace(this.redirectUrl)
          }
          this.success()
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
        .finally(() => this.complete())
      }, this.timerDelay)
    }
  }
}
const AlertMessage = {
  mixins: [BaseMessage]
}

const Dropdown = {
  mixins: [BaseDropdown]
}

const Modal = {
  mixins: [BaseModal],
  created() {
    ModalPlugin.EventBus.$on(this.modalId, () => {
      this.show()
    })
  },
}

const ConfirmationModal = {
  mixins: [BaseModal],
  data() {
    return {
      yes: null,
      no: null
    }
  },
  methods: {
    confirm() {
      this.yes('yes')
      this.isOpen = false
    },
    close() {
      this.no('no')
      this.isOpen = false
    }
  },
  created() {
    ModalPlugin.EventBus.$on(this.modalId, (resolve, reject) => {
      this.show()
      this.yes = resolve
      this.no = reject
    })
  }
}

const EntrySearch = {
  mixins: [BaseLanguageSearch],
  methods: {
    setResult(result) {
      this.searchTerm = result
      this.search()
    },
    search(val) {
      clearTimeout(this.searchTimerId)
      this.isOpen = false
      url = this.searchUrl + "?search_entry=" + this.searchTerm + "&search_language=" + this.language
      window.location.replace(url);
    }
  },
}

const SourceEntrySearch = {
  mixins: [BaseLanguageSearch],
  props: {
    initSourceId: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      sourceId: this.initSourceId,
    }
  },
  methods: {
    setResult(result) {
      this.searchTerm = result
      this.search()
    },
    search(val) {
      clearTimeout(this.searchTimerId)
      this.isOpen = false
      url = this.searchUrl + '?search_entry=' + this.searchTerm + '&search_language=' + this.language + '&search_source=' + this.sourceId
      window.location.replace(url);
    }
  },
}

const ProjectForm = {
  mixins: [BaseForm],
  data() {
    return {
      formData: {
        name: '',
        description: ''
      },
    }
  },
  methods: {
    resetForm() {
      this.formData.name = ''
      this.formData.description = ''
      this.errors = {}
    }
  },
}

const EntryForm = {
  mixins: [BaseForm],
  data() {
    return {
      formData: {
        entry: '',
        language: 'en',
        pronunciation_spelling: '',
        description: ''
      },
    }
  },
  methods: {
    resetForm() {
      this.formData.entry = ''
      this.formData.language = 'en'
      this.formData.pronunciation_spelling = ''
      this.formData.description = ''
      this.errors = {}
    }
  },
}

const ContextForm = {
  mixins: [BaseForm],
  data() {
    return {
      formData: {
        content: '',
      },
    }
  },
  methods: {
    resetForm() {
      this.formData.content = ''
      this.errors = {}
    }
  },
}

const SourceSearch = {
  mixins: [BaseSearch],
  methods: {
    setResult(result) {
      this.searchTerm = result
      this.search()
    },
    search() {
      clearTimeout(this.searchTimerId)
      this.isOpen = false
      url = this.searchUrl + "?source=" + this.searchTerm
      window.location.replace(url);
    },
  },
}

const Tag = {
  mixins: [BaseTag]
}

const ToggleTag = {
  mixins: [BaseToggleTag]
}

const DeleteTag = {
  mixins: [BaseDeleteTag]
}

const EntryTagSearch = {
  mixins: [BaseLanguageSearch],
  methods: {
    setResult(result) {
      this.searchTerm = result
      this.search()
    },
    search() {
      clearTimeout(this.searchTimerId)
      this.isOpen = false
      var tag = {
        language: this.language,
        entry: this.searchTerm
      }
      this.searchTerm = ''
      this.$emit('add-tag', tag)
    }
  },
}

const EntryTagbox = {
  mixins: [BaseTagbox],
  methods: {
    onFocus() {
      this.$emit('tagbox-focus')
    }
  }
}

const EntryInstanceTagbox = {
  mixins: [BaseTagbox, ClickOutsideMixin],
  props: {
    entry: {
      type: Object,
      default: () => {}
    }
  },
  data() {
    return {
      input: ''
    }
  },
  methods: {
    addTag(tag) {
      this.input = ''
      this.$emit('add-tag', tag)
    },
    removeTag(index) {
      this.input = ''
      this.$emit('remove-tag', index)
    },
    selectTag(index) {
      this.input = ''
      this.$emit('select-tag', index)
    },
    onCloseOutside() {
      this.input = ''
    },   
  }
}

const ContextTagger = {
  mixins: [MarkdownMixin, HighlightMixin],
  props: {
    initEntryDetailUrl: {
      type: String,
      required: true
    },
    initAddEntryUrl: {
      type: String,
      required: true
    },
    initAddEntryTagUrl: {
      type: String,
      required: true
    },   
    initRemoveEntryUrl: {
      type: String,
      required: true
    },
    initRemoveEntryTagUrl: {
      type: String,
      required: true
    },
    initContextEditUrl: {
      type: String,
      required: true
    },          
    initEntries: {
      type: Object,
      default: () => ({})
    },
    initContext: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      entryDetailUrl: this.initEntryDetailUrl,
      addEntryUrl: this.initAddEntryUrl,
      addEntryTagUrl: this.initAddEntryTagUrl,
      removeEntryUrl: this.initRemoveEntryUrl,
      removeEntryTagUrl: this.initRemoveEntryTagUrl,
      contextEditUrl: this.initContextEditUrl,
      entries: [],
      currentEntry: null,
      context: this.initContext,
      contextHtml: '',
      isEditing: false
    }
  },
  methods: {
    addEntry(tag) {
      params = {language: tag.language, entry: tag.entry}

      axios.get(this.entryDetailUrl, {
        params: params
      })
      .then(response => {
        console.log('Entry verified.')

        const data = response.data
        console.log(data)
        const entryId = data.id

        const entry = {
          id: entryId,
          value: data.entry,
          language: data.language,
          tags: []
        }

        axios.post(this.addEntryUrl, {"vocab_entry_id": entryId})
        .then(response => {
          console.log('Entry added.')
          this.entries.push(entry)
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
        .finally(() => {})
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
      .finally(() => {})
    },
    removeEntry(index) {
      var tag = this.entries[index]

      axios.post(this.removeEntryUrl, {"vocab_entry_id": tag.id})
      .then(response => {
        console.log('Tag deleted from db.')
        this.entries.splice(index, 1)
        this.reset()
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
      .finally(() => {})      
    },
    selectEntry(index) {
      this.currentEntry = this.entries[index]
      this.clearHighlight()
      this.highlight(this.currentEntry.tags)
      console.log(this.currentEntry.value)
      this.$nextTick(() => {
        if (vm.smallWindow) {
          window.location.hash = "#vocab-entry-instance-tags"
          window.location = window.location.href
        }
      })
    },
    addEntryTag(tag) {
      const data = {
        "vocab_entry_id": this.currentEntry.id,
        "vocab_entry_tag": tag
      }
      axios.post(this.addEntryTagUrl, data)
      .then(response => {
        console.log('Entry tag added.')
        this.currentEntry.tags.push(tag)
        this.highlight(this.currentEntry.tags)
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
      .finally(() => {})
    },
    removeEntryTag(index) {
      var tag = this.currentEntry.tags[index]

      const data = {
        "vocab_entry_id": this.currentEntry.id,
        "vocab_entry_tag": tag
      }

      axios.post(this.removeEntryTagUrl, data)
      .then(response => {
        console.log('Tag instance deleted from db.')
        this.currentEntry.tags.splice(index, 1)
        this.clearHighlight()
        this.highlight(this.currentEntry.tags)
        console.log('entry instance removed ' + tag)
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
      .finally(() => {})      
    },
    selectEntryTag(index) {
      console.log('entry instance selected ' + this.currentEntry.tags[index])
    },
    reset() {
      this.currentEntry = null
      this.clearHighlight()
    },
    loadEntries() {
      for (var k in this.initEntries) {
        const initEntry = this.initEntries[k]['vocab_entry']
        const initTags = this.initEntries[k]['tags']

        const entry = {
          id: initEntry.id,
          value: initEntry.entry,
          language: initEntry.language,
          tags: initTags
        }
        this.entries.push(entry)
      }
    },
    editContext() {
      this.isEditing = true
      this.reset()
    },
    doneEditing() {      
      axios.put(this.contextEditUrl, {"content": this.context})
      .then(response => {
        this.isEditing = false
        this.contextHtml = this.markdownToHtml(this.context)
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
      .finally(() => {})
    }
  },
  created() {
    this.contextHtml = this.markdownToHtml(this.context)
    this.loadEntries()
  }
}

const ContextTagPanel = {
  mixins: [HighlightMixin],
  props: {
    initEntries: {
      type: Object,
      default: () => ({})
    },
    initSelectUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      entries: [],
      currentEntry: null,
      selectUrl: '',
      isVisible: true
    }
  },
  methods: {
    selectTag(index) {
      this.currentEntry = this.entries[index]
      this.selectUrl = this.initSelectUrl
        .replace('xx', this.currentEntry.language)
        .replace('zzz', this.currentEntry.slug)
      window.location.replace(this.selectUrl)
    },
    toggleTag(index) {
      console.log('index ' + index)
      if (this.currentEntry == null) {
        this.currentEntry = this.entries[index]
        this.currentEntry.toggleSelect = true
        this.highlight(this.currentEntry.tags)
      } else if (this.currentEntry.id != this.entries[index].id) {
        this.currentEntry.toggleSelect = false
        this.clearHighlight()
        this.currentEntry = this.entries[index]
        this.currentEntry.toggleSelect = true
        this.highlight(this.currentEntry.tags)
      } else {
        this.currentEntry.toggleSelect = !this.currentEntry.toggleSelect
        if (this.currentEntry.toggleSelect) {
          this.highlight(this.currentEntry.tags)
        } else {
          this.clearHighlight()
        }
      }
    },
    loadEntries() {
      for (var k in this.initEntries) {
        const initEntry = this.initEntries[k]['vocab_entry']
        const initTags = this.initEntries[k]['tags']
        const entry = {
          id: initEntry.id,
          value: initEntry.entry,
          slug: initEntry.slug,
          language: initEntry.language,
          toggleSelect: false,
          tags: initTags
        }
        this.entries.push(entry)
      }
    },
    hidePanel() {
      this.isVisible = false
    }
  },
  created() {
    this.loadEntries()
  }
}

const EntryToggleTag = {
  mixins: [BaseToggleTag],
  methods: {},
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

const SymbolKey = {
  mixins: [BaseSymbolKey]
}

const SymbolKeypad = {
  mixins: [BaseSymbolKeypad]
}

const IpaSymbolKey = {
  mixins: [BaseSymbolKey],
  data() {
    return {
      symbol: he.decode(this.initSymbol)
    }
  },
  template: `
    <a 
    href="#" 
    class="ui tiny basic icon button"
    :title="symbol"
    v-html="symbol"
    @click.prevent="displaySymbol"
    >
    </a>
  `
}

const IpaSymbolKeypad = {
  mixins: [BaseSymbolKeypad],
  data() {
    return {
      ipaSymbolCodes: [
        "&#712;", "&#716;", "&#618;", "&aelig;", "&#593;",
        "&#596;", "&#650;", "&#652;", "&#603;", "&#604;",
        "&#601;", "e&#618;", "a&#618;", "&#596;&#618;", "&#650;",
        "&#618;&#601;", "e&#601;", "&#650;&#601;", "&#952;",
        "&#240;", "&#643;", "&#658;", "t&#643;", "d&#658;",
        "&#331;"
      ]
    }
  },
}

const EntryInfo = {
  mixins: [AjaxProcessMixin],
  props: {
    initEndpointUrl: {
      type: String,
      required: true
    },
    initMsgShowEntryInfo: {
      type: String,
      default: 'Show entry info'
    },
    initMsgHideEntryInfo: {
      type: String,
      default: 'Hide entry info'
    }
  },
  data() {
    return {
      endpointUrl: this.initEndpointUrl,
      entryInfo: {},
      entryInfoVisible: false,
      entryInfoLoaded: false,
      msgShowEntryInfo: this.initMsgShowEntryInfo,
      msgHideEntryInfo: this.initMsgHideEntryInfo
    }
  },
  methods: {
    toggleEntryInfoVisible() {
      this.entryInfoVisible = !this.entryInfoVisible
      if (this.entryInfoVisible && !this.entryInfoLoaded) {
        this.getEntryInfo()
      }
      console.log(this.entryInfoVisible)
    },
    getEntryInfo() {
      console.log('Get entry info')
      this.process()
      axios.get(
        this.endpointUrl
      )
      .then(response => {
        this.entryInfo = response.data;
        console.log(this.entryInfo)
        this.entryInfoLoaded = true
        this.success()
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
      .finally(() => this.complete())
    }
  }
}

/** THIRD PARTY **/

const OxfordApi = {
  mixins: [AjaxProcessMixin],
  props: {
    initEndpointUrl: {
      type: String,
      required: true
    },
    initEntry: {
      type: String,
      required: true
    },
    initLanguage: {
      type: String,
      default: 'en'
    },
    initEnglishRegion: {
      type: String,
      default: 'us'
    }
  },
  data() {
    return {
      endpointUrl: this.initEndpointUrl,
      entry: this.initEntry,
      language: this.initLanguage,
      region: this.initEnglishRegion
    }
  },
  methods: {
    searchApi() {
      axios.get(
        this.endpointUrl, {
          params: {
            language: this.language,
            entry: this.entry,
            region: this.region
          }
        }
      )
      .then(response => {
        this.success()
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
      .finally(() => this.complete())
    }
  }
}