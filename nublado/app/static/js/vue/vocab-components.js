const VocabSource = {
  mixins: [
    AdminMixin,
    VisibleMixin,
    MarkdownMixin
  ],
  props: {
    initSource: {
      type: Object,
      required: true
    },
    initViewUrl: {
      type: String,
      default: ""
    },
    initEditUrl: {
      type: String,
      default: ""
    },
    initDeleteUrl: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      source: this.initSource,
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
      this.$emit("delete-vocab-source")
    }
  },
  created() {
    if (this.initViewUrl) {
      this.viewUrl = this.initViewUrl
        .replace(0, this.source.id)
        .replace("zzz", this.source.slug)   
    }

    if (this.initDeleteUrl) {
      this.deleteUrl = this.initDeleteUrl
        .replace(0, this.source.id)
    } 
  }
}

const VocabSources = {
  components: {
    "vocab-source": VocabSource
  },
  mixins: [
    AdminMixin,
    AjaxProcessMixin,
    PaginationMixin,
  ],
  props: {
    vocabSourcesUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
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
          el: "#vocab-sources-scroll-top",
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
    onDeleteVocabSource(index) {
      this.$delete(this.vocabSources, index)
    }
  },
  created() {
    this.getVocabSources()
  }
}

const VocabSourceSearch = {
  mixins: [
    BaseSearch
  ],
  methods: {
    setResult(result) {
      this.searchTerm =result
      this.search()
    },
    search() {
      clearTimeout(this.searchTimerId)
      this.isOpen = false
      url = this.searchUrl + "?source=" + encodeURIComponent(this.searchTerm)
      window.location.replace(url)
    }
  }
}

const VocabSourceEntrySearch = {
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
      url = this.searchUrl + "?search_entry=" + encodeURIComponent(this.searchTerm) + "&search_language=" + this.language + "&search_source=" + this.sourceId
      window.location.replace(url);
    }
  },
}

const VocabEntry = {
  mixins: [
    AdminMixin,
    VisibleMixin
  ],
  props: {
    initEntry: {
      type: Object,
      required: true
    },
    initViewUrl: {
      type: String,
      default: ""
    },
    initEditUrl: {
      type: String,
      default: ""
    },
    initDeleteUrl: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      entry: this.initEntry,
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
      this.$emit("delete-vocab-entry", this.entry.id)
    }
  },
  created() {
    if (this.initViewUrl) {
      this.viewUrl = this.initViewUrl
        .replace("xx", this.entry.language)
        .replace("zzz", this.entry.slug)
    }

    if (this.initDeleteUrl) {
      this.deleteUrl = this.initDeleteUrl
        .replace(0, this.entry.id)
    }
  }
}

const VocabEntries = {
  components: {
    "vocab-entry": VocabEntry
  },
  mixins: [
    AjaxProcessMixin,
    AdminMixin,
    PaginationMixin,
  ],
  props: {
    initLanguage: {
      type: String,
      default: "en"
    },
    vocabEntriesUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      language: this.initLanguage,
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
          el: "#vocab-entries-scroll-top",
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
    onDeleteVocabEntry(index) {
      this.$delete(this.vocabEntries, index)
    }
  },
  created() {
    this.getVocabEntries()
  }
}

const VocabEntrySearch = {
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

const VocabEntryTagSearch = {
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
      this.searchTerm = ""
      this.$emit("search", tag)
    }
  },
}

const VocabEntryTagbox = {
  components: {
    VocabEntryTagSearch
  },
  mixins: [BaseTagbox],
  methods: {
    addTag(tag) {
      /*
      tag: Object with language and entry properties
      */
      if (tag.entry) {
        const vocabEntryTag = {
          language: tag.language,
          value: tag.entry
        }
        this.$emit("add-tag", vocabEntryTag)
      }
    }
  }
}

const VocabEntryInstanceTagbox = {
  mixins: [Tagbox],
  methods: {
    addTag(tag) {
      /*
      tag: text value
      */
      this.$emit("add-tag", vocabEntryTag)
    }
  }
}

const VocabEntryInfo = {
  mixins: [AjaxProcessMixin],
  props: {
    endpointUrl: {
      type: String,
      required: true
    },
    msgShowVocabEntryInfo: {
      type: String,
      default: "Show entry info"
    },
    msgHideVocabEntryInfo: {
      type: String,
      default: "Hide entry info"
    }
  },
  data() {
    return {
      vocabEntryInfo: {},
      vocabEntryInfoVisible: false,
      vocabEntryInfoLoaded: false,
    }
  },
  methods: {
    toggleVocabEntryInfoVisible() {
      this.vocabEntryInfoVisible = !this.vocabEntryInfoVisible
      if (this.vocabEntryInfoVisible && !this.vocabEntryInfoLoaded) {
        this.getVocabEntryInfo()
      }
    },
    getVocabEntryInfo() {
      console.log('Get vocab entry info')
      this.process()
      axios.get(
        this.endpointUrl
      )
      .then(response => {
        this.vocabEntryInfo = response.data;
        console.log(this.vocabEntryInfo)
        this.vocabEntryInfoLoaded = true
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

// const VocabContext = {
//   mixins: [
//     MarkdownMixin,
//     HighlightMixin,
//     AdminMixin
//   ],
//   props: {
//     initContext: {
//       type: Object,
//       required: true
//     },
//     initSourceUrl: {
//       type: String,
//       default: ''
//     }
//   },
//   data() {
//     return {
//       context: this.initContext,
//       sourceUrl: this.initSourceUrl
//     }
//   },
//   methods: {
//     selectSource() {
//       if (this.sourceUrl) {
//         window.location.replace(this.sourceUrl)
//       }
//     }
//   },
//   created() {
//     if (this.initDeleteUrl) {
//       this.deleteUrl = this.initDeleteUrl
//         .replace(0, this.context.id)
//     }

//     if (this.initSourceUrl) {
//       this.sourceUrl = this.initSourceUrl
//         .replace(0, this.context.vocab_source_id)
//         .replace('zzz', this.context.vocab_source_slug)
//     }
//   }
// }

const VocabEntryContext = {
  mixins: [
    MarkdownMixin,
    HighlightMixin,
    VisibleMixin,
    AdminMixin
  ],
  props: {
    initVocabEntryContext: {
      type: Object,
      required: true
    },
    initVocabSourceUrl: {
      type: String,
      default: ""
    },
    initDeleteUrl: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      vocabEntryContext: this.initVocabEntryContext,
      vocabSourceUrl: this.initVocabSourceUrl,
      deleteUrl: this.initDeleteUrl
    }
  },
  methods: {
    selectVocabSource() {
      if (this.vocabSourceUrl) {
        window.location.replace(this.vocabSourceUrl)
      }
    },
    remove() {
      this.$emit("delete-vocab-context")
    }
  },
  created() {
    this.$nextTick(() => {
      this.highlight(this.vocabEntryContext.vocab_entry_tags)
    })

    if (this.initVocabSourceUrl) {
      this.vocabSourceUrl = this.initVocabSourceUrl
        .replace(0, this.vocabEntryContext.vocab_source_id)
        .replace('zzz', this.vocabEntryContext.vocab_source_slug)
    }
  
    if (this.initDeleteUrl) {
      this.deleteUrl = this.initDeleteUrl
        .replace(0, this.entryContext.vocab_context_id)
    }  
  }
}

const VocabContexts = {
  mixins: [
    AjaxProcessMixin,
    PaginationMixin,
    AdminMixin
  ],
  props: {
    vocabContextsUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
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
          el: '#vocab-contexts-scroll-top',
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
    onDeleteVocabContext(index) {
      this.$delete(this.vocabContexts, index)
    }
  },
  created() {
    this.getVocabContexts()
  }
}

const VocabEntryContexts = {
  mixins: [VocabContexts]
}

const VocabContextEditor = {
  components: {
    "markdown-editor": MarkdownEditor
  },
  mixins: [
    HighlightMixin
  ],
  props: {
    initVocabEntries: {
      type: Array,
      default: () => ([])
    },
    vocabEntryDetailUrl: {
      type: String,
      required: true
    },
    addVocabEntryUrl: {
      type: String,
      required: true
    },
    removeVocabEntryUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      vocabEntries: [],
      selectedVocabEntry: null
    }
  },
  methods: {
    selectVocabEntry(index) {
      this.selectedVocabEntry = this.vocabEntries[index]
      console.log(this.selectedVocabEntry.value)
      this.clearHighlight()
      this.highlight(this.selectedVocabEntry.tags)
    },
    addVocabEntry(tag) {
      /*
      tag: Object with value and language properties
      */
      params = {language: tag.language, entry: tag.value}

      axios.get(this.vocabEntryDetailUrl, {
        params: params
      })
      .then(response => {
        console.log("Vocab entry verified.")

        const data = response.data
        const vocabEntryId = data.id

        const vocabEntry = {
          id: vocabEntryId,
          value: data.entry,
          language: data.language,
          tags: []
        }

        axios.post(this.addVocabEntryUrl, {"vocab_entry_id": vocabEntryId})
        .then(response => {
          console.log("Vocab entry added.")
          this.vocabEntries.push(vocabEntry)
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
    removeVocabEntry(index) {
      const vocabEntry = this.vocabEntries[index]

      axios.post(this.removeVocabEntryUrl, {"vocab_entry_id": vocabEntry.id})
      .then(response => {
        console.log("Vocab entry deleted.")
        this.$delete(this.vocabEntries, index)
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
    loadVocabEntries() {
      for (var i in this.initVocabEntries) {
        const initVocabEntry = this.initVocabEntries[i]["vocab_entry"]
        const initTags = this.initVocabEntries[i]["tags"]

        const vocabEntry = {
          id: initVocabEntry.id,
          value: initVocabEntry.entry,
          language: initVocabEntry.language,
          tags: initTags
        }
        this.vocabEntries.push(vocabEntry)
      }
    },
  },
  created() {
    this.loadVocabEntries()
  }
}