// Vocab entry

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
      url = this.searchUrl + "?search_entry=" + encodeURIComponent(this.searchTerm) + "&search_language=" + this.language
      window.location.replace(url);
    }
  },
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

const EntryToggleTag = {
  mixins: [BaseToggleTag],
  methods: {},
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


// Vocab context

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

// Vocab source

const VocabSources = {
  mixins: [
    AjaxProcessMixin,
    PaginationMixin
  ],
  props: {
    initVocabSourcesUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      vocabSourcesUrl: this.initVocabSourcesUrl,
      vocabSources: null
    }
  },
  methods: {
    getVocabSources(page=1) {
      this.process()

      params = {
        page: page
      }

      axios.get(this.vocabSourcesUrl, {
        params: params
      })
      .then(response => {
        this.vocabSources = response.data.results
        this.setPagination(
          response.data.previous,
          response.data.next,
          response.data.page_num,
          response.data.count,
          response.data.num_pages
        )
        VueScrollTo.scrollTo({
          el: '#sources-scroll-top',
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
    this.getVocabSources()
  }
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
      url = this.searchUrl + '?search_entry=' + encodeURIComponent(this.searchTerm) + '&search_language=' + this.language + '&search_source=' + this.sourceId
      window.location.replace(url);
    }
  },
}

const SourceSearch = {
  mixins: [BaseSearch],
  methods: {
    setResult(result) {
      this.searchTerm =result
      this.search()
    },
    search() {
      clearTimeout(this.searchTimerId)
      this.isOpen = false
      url = this.searchUrl + "?source=" + encodeURIComponent(this.searchTerm)
      window.location.replace(url);
    },
  },
}

// Forms

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

// Keypad

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